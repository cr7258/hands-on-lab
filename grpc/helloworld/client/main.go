package main

import (
	"context"
	"google.golang.org/grpc/metadata"
	"log"
	"time"

	pb "github.com/cr7258/hands-on-lab/grpc/helloworld/proto"
	"google.golang.org/grpc"
)

const (
	address = "localhost:8080"
	name    = "world"
)

func main() {
	// Set up a connection to the server.
	conn, err := grpc.Dial(address, grpc.WithInsecure())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	defer conn.Close()
	c := pb.NewGreeterClient(conn)

	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()

	// ！metadata 用于在服务间传递一些参数，注意后面它在交互中出现的位置
	ctx = metadata.AppendToOutgoingContext(ctx, "metadata", "is metadata")

	r, err := c.SayHello(ctx, &pb.HelloRequest{Name: name})
	if err != nil {
		log.Fatalf("could not greet: %v", err)
	}
	log.Printf("Greeting: %s", r.GetMessage())
}
