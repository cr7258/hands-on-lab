from locust import HttpUser, task

from time import sleep
import random


class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/api/favorites")

        if random.random() < 0.5:
            self.client.post("/api/favorites", json={"id": random.randint(1, 100)})

        # in 50% of the cases, call the login endpoint
        if random.random() < 0.5:
            self.client.get("/api/login")
        sleep(1)
