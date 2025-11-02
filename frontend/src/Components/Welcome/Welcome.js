import React, { useContext } from 'react';
import { Button, Icon, Segment, Statistic, Grid, Header, Card, Container } from "semantic-ui-react";
import { AppContext } from "../../Context/AppContext";

// Helper function to count connections (remains the same)
function getConnectionsCount(tree, protocol) {
    let filter = () => true;

    if (protocol) {
        // Assuming 'protocol' is directly on connection nodes, not folders.
        filter = (node) => node.protocol === protocol;
    }

    if (tree) {
        return tree.reduce(function (total, node) {
            // Count if it's NOT a folder AND it passes the protocol filter
            const count = (!node.isFolder && filter(node)) ? 1 : 0;
            // Recursively count children
            return total + count + getConnectionsCount(node.children, protocol);
        }, 0)
    }
    return 0;
}

// Dark Mode Styles and Constants
const DARK_MODE_BACKGROUND = '#1e1e1e';
const CARD_BACKGROUND = '#2d2d2d';
const TEXT_COLOR = '#f0f0f0';
const PRIMARY_COLOR = '#00bcd4'; // Cyan for primary actions/highlights
const ACCENT_COLOR = '#ff9800'; // Orange for secondary highlights

const containerStyle = {
    padding: '30px',
    minHeight: '100vh',
    backgroundColor: DARK_MODE_BACKGROUND,
};

// Component Start
function Welcome(props) {
    const [appState] = useContext(AppContext);

    // Ticket calculation logic remains the same
    const personalTickets = appState.tickets.filter(t => t.user.id === appState.user.id).length;
    const receivedTickets = appState.tickets.filter(t => t.user.id === appState.user.id && t.user.id !== t.author.id).length;
    const sharedTickets = appState.tickets.filter(t => t.author.id === appState.user.id && t.user.id !== t.author.id).length;

    // Connection Counts
    const totalConnections = getConnectionsCount(appState.connections);
    const rdpConnections = getConnectionsCount(appState.connections, "rdp");
    const sshConnections = getConnectionsCount(appState.connections, "ssh");
    const vncConnections = getConnectionsCount(appState.connections, "vnc");


    // Helper for consistent dark segment styling
    const DarkSegment = ({ children, header, icon, color, style = {} }) => (
        <Segment style={{
            ...style,
            background: CARD_BACKGROUND,
            border: '1px solid #3a3a3a',
            borderRadius: '10px',
            padding: '25px',
            marginBottom: '20px'
        }}>
            {header && (
                <Header as='h3' style={{ marginBottom: '15px', color: PRIMARY_COLOR, borderBottom: '1px solid #3a3a3a', paddingBottom: '10px' }}>
                    <Icon name={icon} color={color} />
                    <Header.Content style={{ color: TEXT_COLOR }}>
                        {header}
                    </Header.Content>
                </Header>
            )}
            {children}
        </Segment>
    );

    // Render Logic
    return (
        <Container style={containerStyle}>
            {/* 1. Welcome Header Section */}
            <Segment clearing style={{
                background: `linear-gradient(135deg, #004c4c 0%, #00838f 100%)`, // Deep Teal Gradient
                border: 'none',
                borderRadius: '12px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.4)',
                padding: '30px',
                marginBottom: '30px'
            }}>
                <Grid stackable verticalAlign="middle">
                    <Grid.Column floated='left' width={12}>
                        <Header as='h1' inverted style={{ marginBottom: '5px', fontSize: '2em' }}>
                            <Icon name='hand peace' style={{ color: TEXT_COLOR }} />
                            <Header.Content>
                                Hello, {appState.user.first_name}
                                <Header.Subheader style={{ marginTop: '5px', color: '#e0f7fa' }}>
                                    @{appState.user.username}
                                </Header.Subheader>
                            </Header.Content>
                        </Header>
                    </Grid.Column>
                    <Grid.Column floated='right' width={4} textAlign="right">
                        <Button
                            color='red'
                            size='large'
                            icon
                            labelPosition='left'
                            onClick={appState.actions.logout}
                            style={{ borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.2)' }}
                        >
                            <Icon name='sign out' />
                            Logout
                        </Button>
                    </Grid.Column>
                </Grid>
            </Segment>

            {/* 2. Key Metrics Overview */}
            <Grid stackable columns={2}>
                <Grid.Column>
                    {/* Connection Overview */}
                    <DarkSegment header="Connection Overview" icon="sitemap" color="blue">
                        <Statistic.Group widths='four' size='small' inverted>
                            <Statistic color='grey'>
                                <Statistic.Value style={{ color: TEXT_COLOR }}>
                                    {totalConnections}
                                </Statistic.Value>
                                <Statistic.Label>Total</Statistic.Label>
                            </Statistic>

                            <Statistic color='blue'>
                                <Statistic.Value>
                                    <Icon name='desktop' />
                                    {rdpConnections}
                                </Statistic.Value>
                                <Statistic.Label>RDP</Statistic.Label>
                            </Statistic>

                            <Statistic color='green'>
                                <Statistic.Value>
                                    <Icon name='terminal' />
                                    {sshConnections}
                                </Statistic.Value>
                                <Statistic.Label>SSH</Statistic.Label>
                            </Statistic>

                            <Statistic color='teal'>
                                <Statistic.Value>
                                    <Icon name='computer' />
                                    {vncConnections}
                                </Statistic.Value>
                                <Statistic.Label>VNC</Statistic.Label>
                            </Statistic>
                        </Statistic.Group>
                    </DarkSegment>
                </Grid.Column>

                <Grid.Column>
                    {/* Access Tickets Overview */}
                    <DarkSegment header="Access Tickets" icon="ticket" color="orange">
                        <Card.Group itemsPerRow={3} stackable>
                            {/* Personal Tickets */}
                            <Card raised fluid style={{ background: '#3b3b3b', border: `1px solid ${PRIMARY_COLOR}` }}>
                                <Card.Content textAlign='center' style={{ padding: '20px' }}>
                                    <Statistic size='tiny' inverted color='cyan'>
                                        <Statistic.Value><Icon name='user' />{personalTickets}</Statistic.Value>
                                        <Statistic.Label>Personal</Statistic.Label>
                                    </Statistic>
                                </Card.Content>
                            </Card>

                            {/* Received Tickets */}
                            <Card raised fluid style={{ background: '#3b3b3b', border: `1px solid ${ACCENT_COLOR}` }}>
                                <Card.Content textAlign='center' style={{ padding: '20px' }}>
                                    <Statistic size='tiny' inverted color='orange'>
                                        <Statistic.Value><Icon name='inbox' />{receivedTickets}</Statistic.Value>
                                        <Statistic.Label>Received</Statistic.Label>
                                    </Statistic>
                                </Card.Content>
                            </Card>

                            {/* Shared Tickets */}
                            <Card raised fluid style={{ background: '#3b3b3b', border: `1px solid #f44336` }}>
                                <Card.Content textAlign='center' style={{ padding: '20px' }}>
                                    <Statistic size='tiny' inverted color='red'>
                                        <Statistic.Value><Icon name='share alternate' />{sharedTickets}</Statistic.Value>
                                        <Statistic.Label>Shared</Statistic.Label>
                                    </Statistic>
                                </Card.Content>
                            </Card>
                        </Card.Group>
                    </DarkSegment>
                </Grid.Column>
            </Grid>

            {/* 3. Footer */}
            <Segment textAlign='center' style={{
                marginTop: '30px',
                background: CARD_BACKGROUND,
                borderRadius: '12px',
                border: '1px solid #3a3a3a',
                padding: '15px'
            }}>
                <a
                    href="https://guacozy.readthedocs.io"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: TEXT_COLOR, textDecoration: 'none' }}
                >
                    <img src='favicon.ico' alt="Guacozy logo" style={{ height: '24px', verticalAlign: 'middle', marginRight: '10px' }} />
                    <span style={{ fontWeight: 'bold' }}>Guacozy</span>
                    <span style={{ opacity: 0.7, marginLeft: '10px', fontSize: '0.9em' }}>
                        Version {process.env.REACT_APP_VERSION}
                    </span>
                </a>
            </Segment>
        </Container>
    );
}

export default Welcome;