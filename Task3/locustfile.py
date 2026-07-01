from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def index(self):
        # GET / — получение идентификатора пода; именно по этому методу
        # растёт http_requests_total и утилизация ресурсов пода.
        self.client.get("/")
