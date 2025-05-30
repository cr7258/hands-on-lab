FROM ${ARCH}mcr.microsoft.com/dotnet/aspnet:7.0. AS base
WORKDIR /app
EXPOSE 8000

FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0-preview AS build
ARG TARGETPLATFORM

WORKDIR /src
COPY ["login.csproj", "./"]
RUN dotnet restore "./login.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "login.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "login.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Install dependencies
RUN apt-get update && apt-get install -y zip curl
RUN mkdir /otel
RUN curl -L -o /otel/otel-dotnet-install.sh https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/releases/download/v0.7.0/otel-dotnet-auto-install.sh
RUN chmod +x /otel/otel-dotnet-install.sh

#ENV OTEL_METRICS_EXPORTER=otlp
#ENV OTEL_LOGS_EXPORTER=otlp
#ENV OTEL_RESOURCE_ATTRIBUTES=service.name=dotNet,service.version=1.0,deployment.environment=production


ENV OTEL_DOTNET_AUTO_HOME=/otel

RUN /bin/bash /otel/otel-dotnet-install.sh

# Provide necessary permissions for the script to execute
RUN chmod +x /otel/instrument.sh

COPY platform-detection.sh /otel/

# Run the platform detection script
RUN chmod +x /otel/platform-detection.sh && /otel/platform-detection.sh

# Run the env setup script and then start the dotnet application on container startup
ENTRYPOINT ["/bin/bash", "-c", "source /otel/instrument.sh && dotnet login.dll"]
