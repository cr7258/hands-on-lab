package main

import (
	"log"
	"net/http"
	"os"
	"time"

	"github.com/go-redis/redis/v8"

	"github.com/sirupsen/logrus"

	"github.com/gin-gonic/gin"
	"strconv"
	"math/rand"
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

	// Initialize router
	r := gin.New()
	r.Use(logrusMiddleware)

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
			time.Sleep(time.Duration(rand.NormFloat64()*float64(sleepTime / 10)+float64(sleepTime))* time.Millisecond)
			// add label to transaction
			logger.Info("Canary enabled")

			// read env var TOGGLE_CANARY_FAILURE, which is a float between 0 and 1
			if toggleCanaryFailureStr := os.Getenv("TOGGLE_CANARY_FAILURE"); toggleCanaryFailureStr != "" {
				toggleCanaryFailure, err := strconv.ParseFloat(toggleCanaryFailureStr, 64)
				if err != nil {
					toggleCanaryFailure = 0
				}
				if rand.Float64() < toggleCanaryFailure {
					// throw an exception in 50% of the cases
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
