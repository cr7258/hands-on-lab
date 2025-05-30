FROM ${ARCH}mcr.microsoft.com/dotnet/aspnet:7.0. AS base
WORKDIR /app
EXPOSE 8000

FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0-preview AS build
WORKDIR /src
COPY ["login.csproj", "./"]
RUN dotnet restore "./login.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet add package Elastic.Apm --version 1.22.0
RUN dotnet build "login.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "login.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

ENV ELASTIC_APM_ENVIRONMENT=production
ENV ELASTIC_APM_SECRET_TOKEN=XXX
ENV ELASTIC_APM_SERVER_URL=https://2a773133cd7c4cf29134d0d4a81e3ae0.apm.us-central1.gcp.cloud.es.io:443
ENV ELASTIC_APM_SERVICE_NAME=dotnet-login-elastic-auto

ENTRYPOINT ["dotnet", "login.dll"]
