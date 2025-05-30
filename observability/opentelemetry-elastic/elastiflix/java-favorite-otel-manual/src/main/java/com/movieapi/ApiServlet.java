package com.movieapi;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.context.Scope;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.Jedis;
import javax.annotation.PostConstruct;

import io.opentelemetry.api.GlobalOpenTelemetry;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.Tracer;
import redis.clients.jedis.JedisPoolConfig;


@RestController
@RequestMapping("/favorites")
public class ApiServlet {
    private static final Logger logger = LogManager.getLogger(ApiServlet.class);

    // Create artificial delay if set
    @Value("${TOGGLE_SERVICE_DELAY:0}")
    private Integer delayTime;

    @Value("${TOGGLE_CANARY_DELAY:0}")
    private Integer sleepTime;

    @Value("${TOGGLE_CANARY_FAILURE:0}")
    private double toggleCanaryFailure;

    // Create redis pool using Jedis client
    @Value("${REDIS_HOST:localhost}")
    private String redisHost;

    @Value("${REDIS_PORT:6379}")
    private Integer redisPort;

    String SERVICE_NAME = System.getenv("OTEL_SERVICE_NAME");


    private JedisPool r;

    @PostConstruct
    public void init() {
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxWaitMillis(3000); // Set the maximum blocked time to 3 seconds
        poolConfig.setMaxTotal(100); // set the max total connections
        r = new JedisPool(poolConfig, redisHost, redisPort);
    }

    @GetMapping
    public String helloWorld(@RequestParam(required = false) String user_id) throws InterruptedException {
        Span span = GlobalOpenTelemetry.getTracer(SERVICE_NAME).spanBuilder("helloWorld").startSpan();
        Scope scope = span.makeCurrent();
        String returnedString = "";

        if (user_id == null) {
            logger.info("Main request successful");
            returnedString= "Hello World!";
        } else {
            returnedString = getUserFavorites(user_id);
        }

        span.addEvent("a span event", Attributes
                .of(AttributeKey.longKey("someKey"), Long.valueOf(93)));
        span.setStatus(StatusCode.OK);
        span.end();
        scope.close();

        return returnedString;

    }
    public void postUserFavorites(String user_id, String movieID) {
        Span span = GlobalOpenTelemetry.getTracer(SERVICE_NAME).spanBuilder("Redis.Post").setSpanKind(SpanKind.CLIENT).startSpan();
        Jedis jedis = r.getResource();

        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("db.system", "redis");
            span.setAttribute("db.connection_string", redisHost);
            span.setAttribute("db.statement", "POST user_id " + user_id +" AND movie_id "+movieID);

                Long redisResponse = jedis.srem(user_id, movieID);
                if (redisResponse == 0) {
                    jedis.sadd(user_id, movieID);
                }
        } catch (Exception e) {
            span.setStatus(StatusCode.ERROR, "Error while getting data from Redis");
            span.recordException(e);
        } finally {
            jedis.close();
            span.end();
        }
    }


    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public String handlePost(@RequestParam String user_id, @RequestBody String requestBody) throws InterruptedException, Exception {
        Span span = GlobalOpenTelemetry.getTracer(SERVICE_NAME).spanBuilder("handlePost").startSpan();
        Scope scope = span.makeCurrent();

        handleDelay();
        logger.info("Adding or removing favorites");

        JSONObject json = new JSONObject(requestBody);
        String movieID = Integer.toString(json.getInt("id"));

       /// String movieID = Integer.toString(requestBody.getInt("id"));

        logger.info("Adding or removing favorites for user " +  user_id + ", movieID " + movieID);

        postUserFavorites(user_id,movieID);
        String favorites = getUserFavorites(user_id);
        handleCanary();

        span.addEvent("a span event", Attributes
                .of(AttributeKey.longKey("someKey"), Long.valueOf(93)));

        span.setStatus(StatusCode.OK);

        span.end();

        scope.close();
        return favorites;
    }
    public String getUserFavorites(String user_id) {
        Span span = GlobalOpenTelemetry.getTracer(SERVICE_NAME).spanBuilder("Redis.Get").setSpanKind(SpanKind.CLIENT).startSpan();
        String returnedFavorites = "";
        Jedis jedis = r.getResource();

        try (Scope scope = span.makeCurrent()) {
            span.setAttribute("db.system", "redis");
            span.setAttribute("db.connection_string", redisHost);
            span.setAttribute("db.statement", "GET user_id" + user_id);

            handleDelay();

            logger.info("Getting favorites for user " + user_id);

            List<String> favorites = new ArrayList<>(jedis.smembers(user_id));
            JSONObject favorites_json = new JSONObject();
            favorites_json.put("favorites", favorites);

            logger.info("User " + user_id + " has favorites " + favorites);

            logger.info("Delay time is " + delayTime);
            logger.info("Sleep time is " + sleepTime);
            logger.info("Toggle canary failure is " + toggleCanaryFailure);

            returnedFavorites =  favorites_json.toString();

        } catch (Exception e) {
            span.setStatus(StatusCode.ERROR, "Error while getting data from Redis");
            span.recordException(e);
        } finally {
            jedis.close();
            span.end();
        }
        // get currently active span
        Span currentSpan = Span.current();
        currentSpan.setStatus(StatusCode.OK);
        return returnedFavorites;
    }



    private void handleDelay() throws InterruptedException {
        if (delayTime != null && delayTime > 0) {
            Random random = new Random();
            double randomGaussDelay = Math.min(delayTime*5, Math.max(0, random.nextGaussian() * (delayTime)));
            TimeUnit.MILLISECONDS.sleep((long) randomGaussDelay);
        }
    }

    private void handleCanary() throws Exception {
        Span span = GlobalOpenTelemetry.getTracer(SERVICE_NAME).spanBuilder("handleCanary").startSpan();
        Scope scope = span.makeCurrent();

        Random random = new Random();
        if (sleepTime > 0 && random.nextDouble() < 0.5) {
            double randomGaussDelay = Math.min(sleepTime*5, Math.max(0, random.nextGaussian() * (sleepTime)));
            TimeUnit.MILLISECONDS.sleep((long) randomGaussDelay);
            logger.info("Canary enabled");
            Span.current().setAttribute("canary", "test-new-feature");
            Span.current().setAttribute("quiz_solution", "correlations");

            if (random.nextDouble() < toggleCanaryFailure) {
                logger.error("Something went wrong");
                throw new Exception("Something went wrong");
            }
        }
        span.addEvent("a span event", Attributes.of(AttributeKey.longKey("someKey"), Long.valueOf(93)));
        span.setStatus(StatusCode.OK);
        span.end();
        scope.close();
    }
}
