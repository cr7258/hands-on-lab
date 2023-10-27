FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o my-scheduler main.go


FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/my-scheduler .
CMD ["./my-scheduler"]