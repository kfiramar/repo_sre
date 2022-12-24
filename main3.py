import os
import configobj
import collections
import hashlib
import logging
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from prometheus_client import Counter, Gauge, Summary, start_http_server

# create all the variables
config = configobj.ConfigObj('config.ini')
PYPI_PACKAGE_VERSION = config['PYPI']['PACKAGE_VERSION']
PYPI_PACKAGE_NAME = config['PYPI']['PACKAGE_NAME']
PYPI_PACKAGE_URL = config['PYPI']['PACKAGE_URL'].format(
    PACKAGE_NAME=PYPI_PACKAGE_NAME,
    PACKAGE_LETTER=PYPI_PACKAGE_NAME[0],
    PACKAGE_VERSION=PYPI_PACKAGE_VERSION,
)
PYPI_HASH = config['PYPI']['HASH']
REQUEST_EVERY = config['GENERAL'].as_int('REQUEST_EVERY')
TIMEOUT = config['GENERAL'].as_int('TIMEOUT')
DEQUE_SIZE = config['GENERAL'].as_int('DEQUE_SIZE')
SLA = config['GENERAL'].as_float('SLA')
requests_deque = collections.deque(maxlen=DEQUE_SIZE)

# Set up logging
logger = logging.getLogger(__name__)
logging.getLogger('apscheduler').setLevel(logging.ERROR)
logger.setLevel(logging.INFO)
myformatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%H:%M:%S')
myhandler = logging.StreamHandler()
myhandler.setFormatter(myformatter)
logger.addHandler(myhandler)


# Set up Prometheus metrics
start_http_server(8000)
request_time = Summary('request_processing_seconds', 'Time spent processing request')
up_status = Gauge('up_status', 'Repository up status')
successful_downloads = Counter('download_success', 'Number of successful package downloads')
failed_downloads = Counter('download_failure', 'Number of failed package downloads')


def download_package(url: str, timeout: int) -> bytes:
    """Download a package from the given URL."""
    with request_time.time():
        try:
            with requests.Session() as session:
                response = session.get(url, timeout=timeout)
                response.raise_for_status()
                return response.content
        except requests.exceptions.RequestException as exception:
            logger.error(f"Request failed: {url} \nWith exception: {exception}")


def verify_package_hash(package: bytes, desired_hash: str) -> bool:
    """Verify the hash of the given package."""
    package_hash = hashlib.sha256(package).hexdigest()
    return package_hash == desired_hash

def update_metrics(url: str, desired_hash: str):
    """Update the Prometheus metrics."""
    package = download_package(url, TIMEOUT)
    if package:
        if verify_package_hash(package, desired_hash):
            prometheus_updater(failed=False, text=f'Downlaoded and verified! {url}')
        else:
            prometheus_updater(failed=True, text=f'Downlaoded, but HASH INCORRECT! {url}')
    else:
        prometheus_updater(failed=True)


def prometheus_updater(failed: bool, text: str = ''):
    """Update the repository status based on the given deque of request results."""
    if failed:
        requests_deque.append(0)
        failed_downloads.inc()
        if text:
            logger.error(text)
    else:
        requests_deque.append(1)
        successful_downloads.inc()
        logger.info(text)
    up_status.set(SLA < (sum(requests_deque) / len(requests_deque)))


def main():
    """Main function."""
    # Set up scheduling
    scheduler = BlockingScheduler()
    scheduler.add_job(update_metrics,'interval',seconds=REQUEST_EVERY,args=[PYPI_PACKAGE_URL, PYPI_HASH],id='update_metrics_job',)
    scheduler.start()


if __name__ == '__main__':
    main()
