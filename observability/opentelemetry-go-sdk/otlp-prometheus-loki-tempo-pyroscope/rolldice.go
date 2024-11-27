package main

import (
	"context"
	"fmt"
	"github.com/grafana/pyroscope-go"
	"go.opentelemetry.io/contrib/bridges/otelslog"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
	"io"
	"log"
	"math/rand"
	"net/http"
	"strconv"
	"time"
)

const name = "go.opentelemetry.io/otel/example/dice"

var (
	tracer  = otel.Tracer(name)
	meter   = otel.Meter(name)
	logger  = otelslog.NewLogger(name)
	rollCnt metric.Int64Counter
)

func init() {
	var err error
	rollCnt, err = meter.Int64Counter("dice.rolls",
		metric.WithDescription("The number of rolls by roll value"),
		metric.WithUnit("{roll}"))

	if err != nil {
		panic(err)
	}
}

func rolldice(w http.ResponseWriter, r *http.Request) {
	ctx, span := tracer.Start(r.Context(), "roll")
	defer span.End()

	pyroscope.TagWrapper(context.Background(), pyroscope.Labels("controller", "slow_controller"), func(c context.Context) {
		// Simulate CPU high load
		var i int64 = 0
		startTime := time.Now()
		for time.Since(startTime) < 500*time.Millisecond {
			i++
		}
	})

	roll := 1 + rand.Intn(6)

	// Log
	var msg string
	if player := r.PathValue("player"); player != "" {
		msg = fmt.Sprintf("%s is rolling the dice", player)
	} else {
		msg = "Anonymous player is rolling the dice"
	}
	logger.InfoContext(ctx, msg, "result", roll)

	// Trace
	rollValueAttr := attribute.Int("roll.value", roll)
	span.SetAttributes(rollValueAttr)

	// Metric
	rollCnt.Add(ctx, 1, metric.WithAttributes(rollValueAttr))

	resp := strconv.Itoa(roll) + "\n"
	if _, err := io.WriteString(w, resp); err != nil {
		log.Printf("Write failed: %v\n", err)
	}
}
