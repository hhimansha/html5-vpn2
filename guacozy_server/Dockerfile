FROM python:3.11-slim
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# install psycopg2 dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*  # Add this to clean up

COPY requirements*.txt /app/

# Install with timeout and retry options
RUN pip install --upgrade pip --timeout 100 && \
    pip install -r requirements-ldap.txt --timeout 100 --retries 3

# Create staticfiles directory
RUN mkdir -p /app/staticfiles

# Django service
EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p 8000 guacozy_server.asgi:application"]