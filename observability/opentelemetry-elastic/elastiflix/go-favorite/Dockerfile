# Use the official Golang image as the base image
FROM golang:1.20-alpine AS build

# Set the working directory to /app
WORKDIR /app

# Copy the source code to the container
COPY . .

# Build the application
RUN go build -o /app/main

# Use a minimal Alpine image as the base image for the final image
FROM alpine:3.14

# Copy the application binary from the build image to the final image
COPY --from=build /app/main /app/main

# Set the working directory to /app
WORKDIR /app

# Expose the port that the application listens on
EXPOSE 5000

# Start the application
CMD ["/app/main"]