FROM python:3.9-slim as base

ENV REDIS_HOST="redis"
ENV REDIS_PORT="6379"
ENV ENVIRONMENT="dev"
ENV OTEL_SERVICE_NAME="favorite_otel_manual"
ENV OTEL_SERVICE_VERSION="1.0.0"

# get packages
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /favoriteservice


# Add the application
COPY . .

EXPOSE 5000
ENTRYPOINT [ "python", "main.py" ]