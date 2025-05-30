package com.movieapi;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPoolConfig;

import javax.annotation.PostConstruct;


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
        if (user_id == null) {
            logger.info("Main request successful");
            return "Hello World!";
        } else {
            return getUserFavorites(user_id);
        }
    }

    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public String handlePost(@RequestParam String user_id, @RequestBody String requestBody) throws InterruptedException, Exception {
        handleDelay();
        logger.info("Adding or removing favorites");

        JSONObject json = new JSONObject(requestBody);
        String movieID = Integer.toString(json.getInt("id"));
        
        logger.info("Adding or removing favorites for user " +  user_id + ", movieID " + movieID);
        Jedis jedis = r.getResource();

        try  {
            Long redisResponse = jedis.srem(user_id, movieID);
            if (redisResponse == 0) {
                jedis.sadd(user_id, movieID);
            }
        } catch (Exception e) {
            logger.error("Error adding or removing favorites for user " + user_id + ", movieID " + movieID);
        } finally {
            jedis.close();
        }

        String favorites = getUserFavorites(user_id);
        handleCanary();
        return favorites;
    }

    private String getUserFavorites(String user_id) throws InterruptedException {
        Jedis jedis = r.getResource();
        String returnedFavorites = "";

        try  {
            handleDelay();

            logger.info("Getting favorites for user " + user_id);

            List<String> favorites = new ArrayList<>(jedis.smembers(user_id));
            JSONObject favorites_json = new JSONObject();
            favorites_json.put("favorites", favorites);

            logger.info("User " + user_id + " has favorites " + favorites);
            returnedFavorites =  favorites_json.toString();

        } catch (Exception e) {

        } finally {
            jedis.close();
        }

        logger.info("User " + user_id + " has favorites " + returnedFavorites);

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
        Random random = new Random();
        if (sleepTime > 0 && random.nextDouble() < 0.5) {
            double randomGaussDelay = Math.min(sleepTime*5, Math.max(0, random.nextGaussian() * (sleepTime)));
            TimeUnit.MILLISECONDS.sleep((long) randomGaussDelay);
            logger.info("Canary enabled");

            if (random.nextDouble() < toggleCanaryFailure) {
                logger.error("Something went wrong");
                throw new Exception("Something went wrong");
            }
        }
    }
}
