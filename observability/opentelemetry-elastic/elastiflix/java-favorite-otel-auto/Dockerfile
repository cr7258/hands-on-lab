# Start with a base image containing Java runtime
FROM maven:3.8.2-openjdk-17-slim as build

# Make port 8080 available to the world outside this container
EXPOSE 5000

# Change to the app directory
WORKDIR /usr/src/app

# Copy the local code to the container
COPY . .

# Build the application
RUN mvn clean install

USER root
RUN apt-get update && apt-get install -y zip curl

ARG OTEL_AGENT_VERSION=2.0.0
RUN mkdir /otel
RUN curl -L -o /otel/opentelemetry-javaagent.jar https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_AGENT_VERSION}/opentelemetry-javaagent.jar

# For now use only the latest snapshot
RUN mkdir /elastic
RUN curl -L -o /elastic/elastic-otel-javaagent.jar https://oss.sonatype.org/service/local/artifact/maven/redirect\?r\=snapshots\&g\=co.elastic.otel\&a\=elastic-otel-javaagent\&v\=LATEST

COPY start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
