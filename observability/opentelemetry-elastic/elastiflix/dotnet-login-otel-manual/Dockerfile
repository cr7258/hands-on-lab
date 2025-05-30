FROM ${ARCH}mcr.microsoft.com/dotnet/aspnet:7.0. AS base
WORKDIR /app
EXPOSE 8000

FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0-preview AS build
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
COPY appsettings.json . 

ENV OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
ENV OTEL_TRACES_EXPORTER=otlp
ENV OTEL_METRICS_EXPORTER=otlp
ENV OTEL_LOGS_EXPORTER=otlp
ENV OTEL_RESOURCE_ATTRIBUTES=service.name=Login,service.version=1.0.0,deployment.environment=production 
ENV OTEL_EXPORTER_OTLP_ENDPOINT=https://2a773133cd7c4cf29134d0d4a81e3ae0.apm.us-central1.gcp.cloud.es.io:443
ENV OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer XXX" 

ENTRYPOINT ["dotnet", "login.dll"]
