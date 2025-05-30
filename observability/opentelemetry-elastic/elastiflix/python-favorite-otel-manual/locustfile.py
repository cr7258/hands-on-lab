from locust import HttpUser, task

from time import sleep
import random


class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/api/favorites")

        # in 50% of the cases, call the login endpoint
        if random.random() < 0.5:
            self.client.get("/api/login")
        sleep(100)
