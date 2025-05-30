package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-redis/redis/extra/redisotel/v8"
	"github.com/go-redis/redis/v8"

	"github.com/sirupsen/logrus"

	"github.com/gin-gonic/gin"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace"
	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"

	"go.opentelemetry.io/otel/propagation"

	//"go.opentelemetry.io/otel/sdk/resource"
	sdktrace "go.opentelemetry.io/otel/sdk/trace"

	"go.opentelemetry.io/contrib/instrumentation/github.com/gin-gonic/gin/otelgin"

	//semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
	//"go.opentelemetry.io/otel/sdk"
	"go.opentelemetry.io/otel/trace"

	"math/rand"
	"strconv"
	"strings"

	"go.opentelemetry.io/otel/codes"
)

var tracer trace.Tracer

func initTracer() func(context.Context) error {
	tracer = otel.Tracer("go-favorite-otel-manual")

	// Process the collector URL to make it compatible with gRPC
	// Remove any protocol prefix (http:// or https://) as the gRPC client will add its own
	collectorURL = strings.TrimPrefix(collectorURL, "http://")
	collectorURL = strings.TrimPrefix(collectorURL, "https://")
	//serviceVersion := "v1.0.0"

	secureOption := otlptracegrpc.WithInsecure()

	// split otlpHeaders by comma and convert to map
	headers := make(map[string]string)
	for _, header := range strings.Split(otlpHeaders, ",") {
		headerParts := strings.Split(header, "=")

		if len(headerParts) == 2 {
			headers[headerParts[0]] = headerParts[1]
		}
	}

	exporter, err := otlptrace.New(
		context.Background(),
		otlptracegrpc.NewClient(
			secureOption,
			otlptracegrpc.WithEndpoint(collectorURL),
			otlptracegrpc.WithHeaders(headers),
		),
	)

	if err != nil {
		log.Fatal(err)
	}

	otel.SetTracerProvider(
		sdktrace.NewTracerProvider(
			sdktrace.WithSampler(sdktrace.AlwaysSample()),
			sdktrace.WithBatcher(exporter),
			//sdktrace.WithResource(resources),
		),
	)
	otel.SetTextMapPropagator(
		propagation.NewCompositeTextMapPropagator(
			propagation.Baggage{},
			propagation.TraceContext{},
		),
	)
	return exporter.Shutdown
}

var (
	collectorURL = os.Getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
	otlpHeaders  = os.Getenv("OTEL_EXPORTER_OTLP_HEADERS")
)

var logger = &logrus.Logger{
	Out:   os.Stderr,
	Hooks: make(logrus.LevelHooks),
	Level: logrus.InfoLevel,
	Formatter: &logrus.JSONFormatter{
		FieldMap: logrus.FieldMap{
			logrus.FieldKeyTime:  "@timestamp",
			logrus.FieldKeyLevel: "log.level",
			logrus.FieldKeyMsg:   "message",
			logrus.FieldKeyFunc:  "function.name", // non-ECS
		},
		TimestampFormat: time.RFC3339Nano,
	},
}

func contextLogger(c *gin.Context) logrus.FieldLogger {
	return logger
}

func logrusMiddleware(c *gin.Context) {
	start := time.Now()
	method := c.Request.Method
	path := c.Request.URL.Path
	if rawQuery := c.Request.URL.RawQuery; rawQuery != "" {
		path += "?" + rawQuery
	}
	c.Next()
	status := c.Writer.Status()
	contextLogger(c).Infof("%s %s %d %s", method, path, status, time.Since(start))
}

func main() {
	delayTime, _ := strconv.Atoi(os.Getenv("TOGGLE_SERVICE_DELAY"))

	cleanup := initTracer()
	defer cleanup(context.Background())

	redisHost := os.Getenv("REDIS_HOST")
	if redisHost == "" {
		redisHost = "localhost"
	}

	redisPort := os.Getenv("REDIS_PORT")
	if redisPort == "" {
		redisPort = "6379"
	}

	applicationPort := os.Getenv("APPLICATION_PORT")
	if applicationPort == "" {
		applicationPort = "5000"
	}

	// Initialize Redis client
	rdb := redis.NewClient(&redis.Options{
		Addr:     redisHost + ":" + redisPort,
		Password: "",
		DB:       0,
	})
	rdb.AddHook(redisotel.NewTracingHook())

	// Initialize router
	r := gin.New()
	r.Use(logrusMiddleware)
	r.Use(otelgin.Middleware("go-favorite-otel-manual"))

	// Define routes
	r.GET("/", func(c *gin.Context) {
		contextLogger(c).Infof("Main request successful")
		c.String(http.StatusOK, "Hello World!")
	})

	r.GET("/favorites", func(c *gin.Context) {
		// artificial sleep for delayTime
		time.Sleep(time.Duration(delayTime) * time.Millisecond)

		userID := c.Query("user_id")

		contextLogger(c).Infof("Getting favorites for user %q", userID)

		favorites, err := rdb.SMembers(c.Request.Context(), userID).Result()
		if err != nil {
			contextLogger(c).Error("Failed to get favorites for user %q", userID)
			c.String(http.StatusInternalServerError, "Failed to get favorites")
			return
		}

		contextLogger(c).Infof("User %q has favorites %q", userID, favorites)

		c.JSON(http.StatusOK, gin.H{
			"favorites": favorites,
		})
	})

	r.POST("/favorites", func(c *gin.Context) {
		// start otel span
		ctx := c.Request.Context()
		ctx, span := tracer.Start(ctx, "add_favorite_movies")
		defer span.End()

		// artificial sleep for delayTime
		time.Sleep(time.Duration(delayTime) * time.Millisecond)

		userID := c.Query("user_id")

		contextLogger(c).Infof("Adding or removing favorites for user %q", userID)

		var data struct {
			ID int `json:"id"`
		}
		if err := c.BindJSON(&data); err != nil {
			contextLogger(c).Error("Failed to decode request body for user %q", userID)
			c.String(http.StatusBadRequest, "Failed to decode request body")
			return
		}

		redisResponse := rdb.SRem(c.Request.Context(), userID, data.ID)
		if redisResponse.Err() != nil {
			contextLogger(c).Error("Failed to remove movie from favorites for user %q", userID)
			c.String(http.StatusInternalServerError, "Failed to remove movie from favorites")
			return
		}

		if redisResponse.Val() == 0 {
			rdb.SAdd(c.Request.Context(), userID, data.ID)
		}

		favorites, err := rdb.SMembers(c.Request.Context(), userID).Result()
		contextLogger(c).Infof("Getting favorites for user")
		if err != nil {
			contextLogger(c).Error("Failed to get favorites for user %q", userID)
			c.String(http.StatusInternalServerError, "Failed to get favorites")
			return
		}

		contextLogger(c).Infof("User %q has favorites %q", userID, favorites)

		// if enabled, in 50% of the cases, sleep for 2 seconds
		sleepTimeStr := os.Getenv("TOGGLE_CANARY_DELAY")
		sleepTime := 0
		if sleepTimeStr != "" {
			sleepTime, _ = strconv.Atoi(sleepTimeStr)
		}

		if sleepTime > 0 && rand.Float64() < 0.5 {
			time.Sleep(time.Duration(rand.NormFloat64()*float64(sleepTime/10)+float64(sleepTime)) * time.Millisecond)
			// add label to transaction
			logger.Info("Canary enabled")

			span := trace.SpanFromContext(c.Request.Context())
			span.SetAttributes(attribute.String("quiz_solution", "correlations"))
			span.SetAttributes(attribute.String("canary", "test-new-feature"))

			// read env var TOGGLE_CANARY_FAILURE, which is a float between 0 and 1
			if toggleCanaryFailureStr := os.Getenv("TOGGLE_CANARY_FAILURE"); toggleCanaryFailureStr != "" {
				toggleCanaryFailure, err := strconv.ParseFloat(toggleCanaryFailureStr, 64)
				if err != nil {
					toggleCanaryFailure = 0
				}
				if rand.Float64() < toggleCanaryFailure {
					// throw an exception in 50% of the cases
					span.SetStatus(codes.Error, "Something went wrong")
					logger.Error("Something went wrong")
					panic("Something went wrong")
				}
			}
		}

		c.JSON(http.StatusOK, gin.H{
			"favorites": favorites,
		})
	})

	// Start server
	logger.Infof("App startup")
	log.Fatal(http.ListenAndServe(":"+applicationPort, r))
	logger.Infof("App stopped")
}
