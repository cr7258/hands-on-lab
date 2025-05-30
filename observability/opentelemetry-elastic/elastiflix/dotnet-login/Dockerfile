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
ENTRYPOINT ["dotnet", "login.dll"]