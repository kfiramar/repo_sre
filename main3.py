import os

import collections
import hashlib
import logging
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from package_type.basic_package import BasicPackage
from prometheus_items import up_status, pypi_request_time, pypi_successful_downloads, pypi_failed_downloads, npm_request_time, npm_successful_downloads, npm_failed_downloads, deb_request_time, deb_successful_downloads, deb_failed_downloads
from config import DEB_HASH, DEB_PACKAGE_URL, DEQUE_SIZE, NPM_HASH, NPM_PACKAGE_URL, PYPI_HASH, PYPI_PACKAGE_URL, REQUEST_EVERY, SLA

# Set up logging
logger = logging.getLogger(__name__)
logging.getLogger('apscheduler').setLevel(logging.ERROR)
logger.setLevel(logging.INFO)
myformatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s', '%H:%M:%S')
myhandler = logging.StreamHandler()
myhandler.setFormatter(myformatter)
logger.addHandler(myhandler)

# set deque
requests_deque = collections.deque(maxlen=DEQUE_SIZE)


def update_metrics(package):
    """Update the Prometheus metrics."""
    exeption = package.download_package()
    if not exeption:
        if package.verify_package_hash():
            package.prometheus_info(requests_deque)
            logger.info(f'Downlaoded and verified! {package.package_url}')
        else:
            package.prometheus_fail(requests_deque)
            logger.error(f'Downlaoded, but HASH INCORRECT! {package.url}')
    else:
        package.prometheus_fail(requests_deque)
        logger.error(f'FAILED! {exeption}')
    up_status.set(SLA < (sum(requests_deque) / len(requests_deque)))
    print(requests_deque)


def main():
    """Main function."""
    # Set up scheduling
    pypi_package = BasicPackage("pypi", PYPI_PACKAGE_URL, PYPI_HASH,
                                pypi_failed_downloads, pypi_successful_downloads, pypi_request_time)
    npm_package = BasicPackage("NPM", NPM_PACKAGE_URL, NPM_HASH,
                               npm_failed_downloads, npm_successful_downloads, npm_request_time)
    deb_package = BasicPackage("DEB", DEB_PACKAGE_URL, DEB_HASH,
                               deb_failed_downloads, deb_successful_downloads, deb_request_time)
    scheduler = BlockingScheduler()
    scheduler.add_job(update_metrics, 'interval',
                      seconds=REQUEST_EVERY, args=(pypi_package,), id='pypi_job',)
    scheduler.add_job(update_metrics, 'interval',
                      seconds=REQUEST_EVERY, args=(npm_package,), id='npm_job',)
    scheduler.add_job(update_metrics, 'interval',
                      seconds=REQUEST_EVERY, args=(deb_package,), id='deb_job',)
    scheduler.start()


if __name__ == '__main__':
    main()
