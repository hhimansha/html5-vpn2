import asyncio
import uuid
import logging
from urllib.parse import parse_qsl

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from guacamole.client import GuacamoleClient
from guacamole.exceptions import GuacamoleError
from guacamole.instruction import GuacamoleInstruction

from backend.models import Ticket, Connection, AppSettings, TicketLog

logger = logging.getLogger(__name__)

class GuacamoleConsumer(AsyncWebsocketConsumer):
    gclient = None
    ticket = None
    allow_control = False
    connected = False
    _polling_task = None
    _connection_ready = False

    async def connect(self):
        """
        Handles Websocket connect event
        """
        print(f"=== WebSocket Connection Attempt ===")
        print(f"Subprotocols: {self.scope['subprotocols']}")
        print(f"Query string: {self.scope['query_string']}")
        
        # Check if client indicated 'guacamole' as supported subprotocols
        if 'guacamole' not in self.scope['subprotocols']:
            print("Missing guacamole subprotocol")
            await self.close()
            return

        # Accept connection immediately
        await self.accept(subprotocol='guacamole')
        print("WebSocket accepted")

        try:
            # Parse connection parameters
            params = {'audio': []}
            parsed_query = parse_qsl(self.scope["query_string"].decode('utf8'))

            for p in parsed_query:
                if p[0] == 'width':
                    params['width'] = p[1]
                if p[0] == 'height':
                    params['height'] = p[1]
                if p[0] == 'audio':
                    params['audio'] = [p[1]]

            # Get ticket
            ticket_id = self.scope["url_route"]["kwargs"]["ticket"]
            print(f"Looking up ticket: {ticket_id}")
            
            ticket = await database_sync_to_async(Ticket.objects.get)(id=ticket_id)
            self.allow_control = ticket.control
            print(f"Ticket found: {ticket.id}, control: {self.allow_control}")

            # Check user ownership
            if await sync_to_async(lambda: ticket.user != self.scope['user'])():
                await self.send_error("You are not allowed to use this ticket", 771)
                return

            # Check ticket validity
            if not await sync_to_async(ticket.check_validity)():
                await self.send_error("Ticket is no longer valid", 523)
                return

            sessionid = await self.get_ticket_sessionid(ticket)
            connection = await self.get_ticket_connection(ticket)

            # Get guacd server
            guacd = await sync_to_async(lambda: connection.guacdserver)()
            if guacd is None:
                guacd = await self.get_default_guacd_server()

            if guacd is None:
                await self.send_error("No guacd server available", 512)
                return

            print(f"Connecting to guacd: {guacd.hostname}:{guacd.port}")
            self.gclient = GuacamoleClient(guacd.hostname, guacd.port)

            # Try to reconnect to existing session
            if sessionid:
                try:
                    print(f"Attempting to reconnect to session: {sessionid}")
                    await sync_to_async(self.gclient.handshake)(
                        connectionid="$" + str(sessionid), **params
                    )
                    print("Reconnected to existing session")
                except (AttributeError, GuacamoleError) as e:
                    print(f"Reconnect failed: {e}")
                    await self.update_ticket_sessionid(ticket, None)
                    sessionid = None

            # Create new session if needed
            if not sessionid:
                print("Creating new session")
                parameters = await sync_to_async(
                    lambda: Connection.objects.get(pk=ticket.connection.pk).get_guacamole_parameters(self.scope['user'])
                )()

                if parameters['passthrough_credentials']:
                    try:
                        parameters['username'] = self.scope['session']['username']
                        parameters['password'] = self.scope['session']['password']
                    except KeyError:
                        await self.send_error("Username/password not found in session", 999)
                        return

                # Debug parameters (without password)
                debug_params = parameters.copy()
                if 'password' in debug_params:
                    debug_params['password'] = '***'
                print(f"Connection parameters: {debug_params}")

                try:
                    await sync_to_async(self.gclient.handshake)(**parameters, **params)
                    await self.update_ticket_sessionid(ticket, self.gclient.id)
                    print(f"New session created: {self.gclient.id}")
                except Exception as e:
                    print(f"Handshake failed: {e}")
                    import traceback
                    traceback.print_exc()
                    await self.send_error(f"Guacamole handshake failed: {str(e)}", 512)
                    return

            if not self.gclient.id:
                await self.send_error("No session ID after handshake", 512)
                return

            # Save ticket reference and log event
            self.ticket = ticket
            self.connected = True
            await self.log_ticket_action(ticket, 'connect', self.scope)

            # Wait a bit for the connection to stabilize before starting polling
            await asyncio.sleep(0.5)
            
            # Start polling loop
            self._polling_task = asyncio.create_task(self.data_polling())
            
            # Mark connection as ready for user input
            self._connection_ready = True
            print("=== WebSocket Connection Successful ===")

        except Ticket.DoesNotExist:
            await self.send_error("Ticket does not exist", 771)
        except Exception as e:
            print(f"Connection error: {e}")
            import traceback
            traceback.print_exc()
            await self.send_error(f"Connection failed: {str(e)}", 512)

    async def disconnect(self, close_code):
        """
        Websocket disconnect event handler
        """
        print(f"=== WebSocket Disconnect ===")
        print(f"Close code: {close_code}")
        
        # Set connected to False first to stop polling and receiving
        self.connected = False
        self._connection_ready = False
        
        # Cancel polling task if it exists
        if self._polling_task and not self._polling_task.done():
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                print("Polling task cancelled")
            except Exception as e:
                print(f"Error waiting for polling task: {e}")
        
        if self.ticket:
            await self.log_ticket_action(self.ticket, 'disconnect', self.scope)
            await self.update_ticket_sessionid(self.ticket, None)
        
        if self.gclient:
            try:
                await sync_to_async(self.gclient.close)()
                print("Guacamole client closed")
            except Exception as e:
                print(f"Error closing guacamole client: {e}")
        
        print("Disconnect completed")

    async def send_error(self, error_text, error_code):
        """
        Send error and close connection
        """
        print(f"Sending error: {error_text} (code: {error_code})")
        try:
            await self.send(text_data=GuacamoleInstruction("error", error_text, error_code).encode())
        except Exception as e:
            print(f"Error sending error message: {e}")
        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        """
        Websocket receive event handler
        """
        if not self.connected or not self.gclient or not self._connection_ready:
            print(f"Received data but connection not ready: {text_data[:100] if text_data else 'None'}")
            return
            
        # Validate control permissions
        if not self.allow_control:
            if text_data and (text_data.startswith("5.mouse") or text_data.startswith("3.key") or text_data.startswith("4.key")):
                print("Control not allowed, ignoring input event")
                return
        
        if text_data is not None:
            try:
                # Validate the instruction format before sending
                if not self.is_valid_guacamole_instruction(text_data):
                    print(f"Invalid Guacamole instruction received: {text_data[:100]}")
                    return
                    
                print(f"Sending instruction to guacd: {text_data[:100]}...")
                await sync_to_async(self.gclient.send)(text_data)
                
            except (ConnectionResetError, BrokenPipeError, GuacamoleError) as e:
                print(f"Error sending data to guacd: {e}")
                self.connected = False
                self._connection_ready = False
                await self.close()
            except Exception as e:
                print(f"Unexpected error in receive: {e}")
                # Don't close on unexpected errors, just log

    def is_valid_guacamole_instruction(self, instruction):
        """
        Basic validation of Guacamole instruction format
        """
        if not instruction or not isinstance(instruction, str):
            return False
            
        # Check if it ends with semicolon
        if not instruction.endswith(';'):
            print(f"Instruction missing semicolon: {instruction[:100]}")
            return False
            
        # Check basic structure (opcode.element1.element2...;)
        parts = instruction[:-1].split('.')  # Remove semicolon and split
        if len(parts) < 1:
            print(f"Instruction has no parts: {instruction[:100]}")
            return False
            
        # Validate opcode (first part should be a single digit)
        opcode = parts[0]
        if not opcode.isdigit():
            print(f"Invalid opcode: {opcode}")
            return False
            
        return True

    async def data_polling(self):
        """
        Polling loop - receives data from GuacamoleClient and passes to websocket
        """
        print("Starting data polling loop")
        polling_interval = 0.01  # 10ms interval
        message_count = 0
        
        try:
            while self.connected and self.gclient:
                try:
                    content = await sync_to_async(self.gclient.receive)()
                    
                    if content:
                        message_count += 1
                        if message_count <= 5:  # Log first 5 messages for debugging
                            print(f"Received from guacd [{message_count}]: {content[:200]}...")
                        
                        # Skip 0x0 size workaround
                        if content == "4.size,1.1,1.0,1.0;":
                            continue
                            
                        try:
                            await self.send(text_data=content)
                        except Exception as e:
                            print(f"Error sending to WebSocket: {e}")
                            break
                    
                    # Small delay to prevent busy waiting
                    await asyncio.sleep(polling_interval)
                    
                except (ConnectionResetError, BrokenPipeError, GuacamoleError) as e:
                    print(f"Connection error in polling: {e}")
                    break
                except asyncio.CancelledError:
                    print("Polling task cancelled")
                    break
                except Exception as e:
                    print(f"Unexpected error in polling iteration: {e}")
                    # Don't break on unexpected errors, just log and continue
                    await asyncio.sleep(polling_interval)
                    
        except Exception as e:
            print(f"Polling loop error: {e}")
        finally:
            print(f"Data polling loop ended after {message_count} messages")
            # Only close if we're still supposed to be connected
            if self.connected:
                self.connected = False
                self._connection_ready = False
                await self.close()

    @database_sync_to_async
    def update_ticket_sessionid(self, ticket, sessionid):
        """
        Update session id of ticket or it's parent in case this is a shared ticket
        """
        if not ticket:
            return
            
        if not ticket.parent:
            ticket_to_update = ticket
        else:
            ticket_to_update = ticket.parent

        if sessionid is None:
            ticket_to_update.sessionid = None
        else:
            # remove first character, because guacd sessionid has '$' as it's first symbol
            newuuid = str(sessionid)[1:37]
            ticket_to_update.sessionid = uuid.UUID(newuuid)

        ticket_to_update.save()

    @database_sync_to_async
    def log_ticket_action(self, ticket, action, scope):
        if ticket:
            TicketLog.addlog(ticket, action, scope=scope)

    @database_sync_to_async
    def get_ticket_sessionid(self, ticket):
        """
        Gets session id associated with ticket or with it's parent if this is a shared ticket
        """
        if not ticket:
            return None
        if not ticket.parent:
            return ticket.sessionid
        return ticket.parent.sessionid

    @database_sync_to_async
    def get_ticket_connection(self, ticket):
        """
        Get connection definition from ticket or from tickets's parent if this is a shared ticket
        """
        if not ticket:
            return None
        if not ticket.parent:
            return ticket.connection
        return ticket.parent.connection

    @database_sync_to_async
    def get_default_guacd_server(self):
        return AppSettings.load().default_guacd_server