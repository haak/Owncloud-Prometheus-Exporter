from prometheus_client import start_http_server, Gauge
import time
import yaml
import requests
import time
import os


# TODO: add regex check for email address

OWNCLOUD_SLEEP_TIME = 600
OWNCLOUD_METRICS_API_KEY = ''
OWNCLOUD_URL = ''

# Global ones
OWNCLOUD_TOTAL_USERS = Gauge('owncloud_total_users', 'Description of gauge')
OWNCLOUD_ACTIVE_USERS = Gauge('owncloud_active_users', 'Description of gauge')
OWNCLOUD_CONCURRENT_USERS = Gauge(
    'owncloud_concurrent_users', 'Description of gauge')

OWNCLOUD_TOTAL_FILES = Gauge('owncloud_total_files', 'Description of gauge')

OWNCLOUD_STORAGE_FREE = Gauge('owncloud_storage_free', 'Description of gauge')
OWNCLOUD_STORAGE_TOTAL = Gauge(
    'owncloud_storage_total', 'Description of gauge')
OWNCLOUD_STORAGE_USED = Gauge('owncloud_storage_used', 'Description of gauge')

# shared between users.
OWNCLOUD_QUOTA_FREE_BYTES = Gauge(
    'owncloud_user_quota_free_bytes', 'Description of gauge', ['user'])
OWNCLOUD_QUOTA_TOTAL_BYTES = Gauge(
    'owncloud_user_quota_total_bytes', 'Description of gauge', ['user'])
OWNCLOUD_QUOTA_USED_BYTES = Gauge(
    'owncloud_user_quota_used_bytes', 'Description of gauge', ['user'])

OWNCLOUD_USER_FILES_TOTAL = Gauge(
    'owncloud_user_files_total', 'Desc of gauge', ['user'])


def load_config():
    global OWNCLOUD_METRICS_API_KEY
    OWNCLOUD_METRICS_API_KEY = os.environ.get('OWNCLOUD_METRICS_API_KEY')
    global OWNCLOUD_SLEEP_TIME
    OWNCLOUD_SLEEP_TIME = os.environ.get('OWNCLOUD_SLEEP_TIME')
    global OWNCLOUD_URL
    OWNCLOUD_URL = os.environ.get('OWNCLOUD_URL')
    global OWNCLOUD_EXPORTER_PORT
    OWNCLOUD_EXPORTER_PORT = os.environ.get('OWNCLOUD_EXPORTER_PORT')


def get_active_users_from_owncloud():
    # print(OWNCLOUD_METRICS_API_KEY)
    headers = {
        'OC-MetricsApiKey': OWNCLOUD_METRICS_API_KEY,
    }

    params = {
        'files': 'true',
        'users': 'true',
        'format': 'json',
    }

    response = requests.get(OWNCLOUD_URL + '/ocs/v1.php/apps/metrics/api/v1/metrics',
                            params=params, headers=headers)

    # print(response.status_code)
    # print(response.text)

    totalCount = response.json()['ocs']['data']['users']['totalCount']
    OWNCLOUD_TOTAL_USERS.set(totalCount)

    activeCount = response.json()['ocs']['data']['users']['activeUsersCount']
    OWNCLOUD_ACTIVE_USERS.set(activeCount)

    concurrentCount = response.json(
    )['ocs']['data']['users']['concurrentUsersCount']

    OWNCLOUD_CONCURRENT_USERS.set(concurrentCount)

    storage_free = response.json()['ocs']['data']['files']['storage']['free']
    OWNCLOUD_STORAGE_FREE.set(storage_free)

    storage_total = response.json()['ocs']['data']['files']['storage']['total']
    OWNCLOUD_STORAGE_TOTAL.set(storage_total)

    storage_used = response.json()['ocs']['data']['files']['storage']['used']
    OWNCLOUD_STORAGE_USED.set(storage_used)

    total_files = response.json()['ocs']['data']['files']['totalFilesCount']
    OWNCLOUD_TOTAL_FILES.set(total_files)


def get_csv_from_owncloud():
    headers = {
        'OC-MetricsApiKey': OWNCLOUD_METRICS_API_KEY,
        'Content-Type': 'application/csv',
    }

    makeRequest = True
    if makeRequest == True:
        response = requests.get(OWNCLOUD_URL + '/index.php/apps/metrics/download-api/users',
                                headers=headers)

        # print(response.status_code)
        # print(response.text)
        lines = response.text.splitlines()

    else:
        with open('test7.csv', newline='') as csvfile:
            lines = csvfile.readlines()

    parse_csv_from_owncloud(lines)

    return


def parse_csv_from_owncloud(lines):
    for line in lines:
        # skip first line
        if line.startswith("userId"):
            continue
        try:
            user = line.split(",")[0]
            name = line.split(",")[1]
            quotaUsed = line.split(",")[3]
            quotaFree = line.split(",")[4]
            quotaTotal = line.split(",")[5]
            files = line.split(",")[6]
            OWNCLOUD_QUOTA_FREE_BYTES.labels(user).set(quotaFree)
            OWNCLOUD_QUOTA_TOTAL_BYTES.labels(user).set(quotaTotal)
            OWNCLOUD_QUOTA_USED_BYTES.labels(user).set(quotaUsed)
            OWNCLOUD_USER_FILES_TOTAL.labels(user).set(files)

        except:
            print("error could not parse csv")
            continue


def start_prometheus_server():
    start_http_server(OWNCLOUD_EXPORTER_PORT)


if __name__ == '__main__':
    load_config()
    startTime = time.time()
    get_active_users_from_owncloud()
    get_csv_from_owncloud()
    print("time elapsed: " + str(time.time() - startTime))
    start_prometheus_server()
    while True:
        print("sleeping")
        time.sleep(int(OWNCLOUD_SLEEP_TIME))
        print("waking up")
        startTime = time.time()
        get_csv_from_owncloud()
        get_active_users_from_owncloud()
        print("time elapsed: " + str(time.time() - startTime))
