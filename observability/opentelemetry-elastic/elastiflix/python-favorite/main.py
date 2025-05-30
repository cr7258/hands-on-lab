from flask import Flask, request

import logging
import redis
import os
import ecs_logging
import datetime
import random
import time

delay_time = os.environ.get("TOGGLE_SERVICE_DELAY")
if delay_time == "" or delay_time is None:
    delay_time = 0
delay_time = int(delay_time)

redis_host = os.environ.get("REDIS_HOST") or "localhost"
redis_port = os.environ.get("REDIS_PORT") or 6379

application_port = os.environ.get("APPLICATION_PORT") or 5000

app = Flask(__name__)

# Get the Logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

# Add an ECS formatter to the Handler
handler = logging.StreamHandler()
handler.setFormatter(ecs_logging.StdlibFormatter())
logger.addHandler(handler)
logging.getLogger("werkzeug").setLevel(logging.ERROR)
logging.getLogger("werkzeug").addHandler(handler)

r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


@app.after_request
def after_request(response):
    print(response)
    # timestamp in iso8601
    timestamp = datetime.datetime.utcnow().isoformat()
    logger.info(
        "%s %s %s %s %s %s",
        timestamp,
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        response.status,
        extra={
            "event.dataset": "favorite.log",
            "http.request.method": request.method,
            "http.request.path": request.full_path,
            "source.ip": request.remote_addr,
            "http.response.status_code": response.status,
        },
    )
    return response


@app.route("/")
def hello():
    logger.info("Main request successfull")
    return "Hello World!"


@app.route("/favorites", methods=["GET"])
def get_favorite_movies():
    # add artificial delay if enabled
    if delay_time > 0:
        time.sleep(max(0, random.gauss(delay_time / 1000, delay_time / 1000 / 10)))

    user_id = str(request.args.get("user_id"))

    logger.info(
        "Getting favorites for user " + user_id,
        extra={"event.dataset": "favorite.log", "user.id": request.args.get("user_id")},
    )

    favorites = r.smembers(user_id)

    # convert to list
    favorites = list(favorites)
    logger.info(
        "User " + user_id + " has favorites: " + str(favorites),
        extra={"event.dataset": "favorite.log", "user.id": user_id},
    )
    return {"favorites": favorites}


@app.route("/favorites", methods=["POST"])
def add_favorite_movie():
    # add artificial delay if enabled
    if delay_time > 0:
        time.sleep(max(0, random.gauss(delay_time / 1000, delay_time / 1000 / 10)))
    user_id = str(request.args.get("user_id"))
    movie_id = request.json["id"]

    logger.info(
        "Adding or removing favorites for user " + user_id, extra={"event.dataset": "favorite.log", "user.id": user_id}
    )

    # add movie to the user's favorite list. If it already exists, remove it from the list
    redisRespone = r.srem(user_id, int(movie_id))
    if redisRespone == 0:
        r.sadd(user_id, movie_id)
    favorites = r.smembers(user_id)

    # convert to list
    favorites = list(favorites)

    logger.info(
        "User " + user_id + " has favorites: " + str(favorites),
        extra={"event.dataset": "favorite.log", "user.id": user_id},
    )

    # if enabled, in 50% of the cases, sleep for 2 seconds
    sleep_time = os.getenv("TOGGLE_CANARY_DELAY")
    if sleep_time is None or sleep_time == "":
        sleep_time = 0
    sleep_time = int(sleep_time)

    if sleep_time > 0 and random.random() < 0.5:
        time.sleep(max(0, random.gauss(delay_time / 1000, delay_time / 1000 / 10)))
        # add label to transaction
        logger.info("Canary enabled")
        if random.random() < float(os.getenv("TOGGLE_CANARY_FAILURE", 0)):
            # throw an exception in 50% of the cases
            logger.error("Something went wrong")
            raise Exception("Something went wrong")

    return {"favorites": favorites}


logger.info("App startup")
app.run(host="0.0.0.0", port=application_port)
logger.info("App Stopped")
