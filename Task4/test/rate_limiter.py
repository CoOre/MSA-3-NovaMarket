# python3 -m locust -f rate_limiter.py --host=http://localhost:8080 --web-port=8082


from locust import HttpUser, task, between


class WebUser(HttpUser):
    wait_time = between(0.01, 0.1)

    @task
    def call_api(self):
        with self.client.get(
            "/api/",
            headers={"client_type": "web"},
            name="/api/ [web]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 429:
                resp.failure("rate limited (429)")
            elif resp.status_code == 200:
                resp.success()

#
class MobileUser(HttpUser):
    wait_time = between(0.01, 0.1)

    @task
    def call_api(self):
        with self.client.get(
            "/api/",
            headers={"client_type": "mobile"},
            name="/api/ [mobile]",
            catch_response=True,
        ) as resp:
            if resp.status_code == 429:
                resp.failure("rate limited (429)")
            elif resp.status_code == 200:
                resp.success()
