# Use the official Golang image as the base image
FROM golang:1.17-alpine as builder

# Set the working directory
WORKDIR /app

# Copy the Go module files
# COPY go.mod .
# COPY go.sum .

# Download the dependencies
# RUN go mod download

# Copy the source code into the container
COPY main.go .

# Build the Go binary for Linux AMD (x86_64) architecture
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o server main.go

# Use the scratch image for the runtime environment
FROM scratch

# Copy the binary from the builder image
COPY --from=builder /app/server /server

# Expose port 80 for the HTTP server
EXPOSE 80

# Run the server
ENTRYPOINT ["/server"]