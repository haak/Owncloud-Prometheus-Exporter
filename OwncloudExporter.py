"""Application exporter"""

import os
import time
from prometheus_client import start_http_server, Gauge, Enum
import requests


class OwncloudMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, polling_interval_seconds=500):
        self.metrics_health = False
        self.polling_interval_seconds = polling_interval_seconds
        self.owncloud_url = os.getenv("OWNCLOUD_URL", None)
        self.metrics_api_key = os.getenv("OWNCLOUD_METRICS_API_KEY", None)

        self.health = Enum("app_health", "Health", states=[
                           "healthy", "unhealthy"])
        self.total_users = Gauge("owncloud_total_users", "Total users")
        self.active_users = Gauge("owncloud_active_users", "Active users")
        self.concurrent_users = Gauge(
            "owncloud_concurrent_users", "Concurrent users")
        self.total_files = Gauge("owncloud_total_files", "Total files")
        self.storage_free = Gauge("owncloud_storage_free", "Storage free")
        self.storage_total = Gauge("owncloud_storage_total", "Storage total")
        self.storage_used = Gauge("owncloud_storage_used", "Storage used")
        self.quota_free_bytes = Gauge(
            "owncloud_user_quota_free_bytes", "Quota free bytes", ["user"])
        self.quota_total_bytes = Gauge(
            "owncloud_user_quota_total_bytes", "Quota total bytes", ["user"])
        self.quota_used_bytes = Gauge(
            "owncloud_user_quota_used_bytes", "Quota used bytes", ["user"])
        self.user_files_total = Gauge(
            "owncloud_user_files_total", "User files total", ["user"])

    def run_metrics_loop(self):
        """Metrics fetching loop"""

        while True:
            self.fetch()

            print("Sleeping for " + str(self.polling_interval_seconds) + " seconds")
            time.sleep(self.polling_interval_seconds)
            print("Done sleeping")

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        self.fetch_system_metrics()
        self.fetch_user_metrics()

    def fetch_user_metrics(self):
        print("Fetching user metrics")
        headers = {
            'OC-MetricsApiKey': self.metrics_api_key,
            'Content-Type': 'application/csv',
        }

        try:
            response = requests.get(self.owncloud_url + '/index.php/apps/metrics/download-api/users',
                                    headers=headers)
            if response.status_code != 200:
                self.health.state("unhealthy")
                self.metrics_health = False
                print("error fetching metrics")

            lines = response.text.splitlines()
            for line in lines:
                # skip first line
                if line.startswith("userId"):
                    continue
                else:
                    user = line.split(",")[0]
                    name = line.split(",")[1]
                    quotaUsed = line.split(",")[3]
                    quotaFree = line.split(",")[4]
                    quotaTotal = line.split(",")[5]
                    files = line.split(",")[6]
                    self.quota_free_bytes.labels(user).set(quotaFree)
                    self.quota_total_bytes.labels(user).set(quotaTotal)
                    self.quota_used_bytes.labels(user).set(quotaUsed)
                    self.user_files_total.labels(user).set(files)
            print("done fetching user metrics")
        except:
            print("error could not parse csv")
            self.health.state("unhealthy")
            self.metrics_health = False
            return False
        self.health.state("healthy")
        self.metrics_health = True

    def fetch_system_metrics(self):
        print("Fetching system metrics")
        headers = {
            'OC-MetricsApiKey': self.metrics_api_key,
        }

        params = {
            'files': 'true',
            'users': 'true',
            'format': 'json',
        }

        try:
            response = requests.get(self.owncloud_url + '/ocs/v1.php/apps/metrics/api/v1/metrics',
                                    params=params, headers=headers)

            if response.status_code != 200:
                self.health.state("unhealthy")
                self.metrics_health = False
                print("error fetching metrics")
                return

            self.total_users.set(
                response.json()['ocs']['data']['users']['totalCount'])
            self.active_users.set(
                response.json()['ocs']['data']['users']['activeUsersCount'])
            self.concurrent_users.set(
                response.json()['ocs']['data']['users']['concurrentUsersCount'])
            self.storage_free.set(
                response.json()['ocs']['data']['files']['storage']['free'])
            self.storage_total.set(
                response.json()['ocs']['data']['files']['storage']['total'])
            self.storage_used.set(
                response.json()['ocs']['data']['files']['storage']['used'])
            self.total_files.set(
                response.json()['ocs']['data']['files']['totalFilesCount'])
        except:
            print("error could not parse json")
            self.health.state("unhealthy")
            self.metrics_health = False
            return

        print("fetched system metrics")
        self.health.state("healthy")
        self.metrics_health = True


def main():
    """Main entry point"""
    polling_interval_seconds = int(os.getenv("OWNCLOUD_SLEEP_TIME", "500"))
    exporter_port = int(os.getenv("OWNCLOUD_EXPORTER_PORT", "9000"))

    print(f"Polling interval: {polling_interval_seconds} seconds")
    owncloud_metrics = OwncloudMetrics(
        polling_interval_seconds=polling_interval_seconds
    )
    owncloud_metrics.fetch()
    print("Initial metrics fetched")
    if owncloud_metrics.metrics_health:
        start_http_server(exporter_port)
        print(f"Started metrics server on port {exporter_port}")
        owncloud_metrics.run_metrics_loop()
    else:
        print("Metrics server not started due to health check failure")


if __name__ == "__main__":
    main()
