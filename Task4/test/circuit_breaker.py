# python3 -m locust -f circuit_breaker.py --host=http://localhost:8080 --web-port=8082

from locust import HttpUser, task, constant


class LogisticsUser(HttpUser):
    wait_time = constant(0.2)

    @task
    def call_failing_logistics(self):
        with self.client.get(
            "/logistics/error",
            name="/logistics/error",
            catch_response=True,
        ) as resp:
            body = resp.text or ""
            if "Circuit open" in body:
                resp.failure("circuit OPEN -> fallback")
            elif resp.status_code >= 500:
                resp.failure(f"upstream error ({resp.status_code})")
            else:
                resp.success()
