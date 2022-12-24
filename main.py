import collections
import logging

# Import the BlockingScheduler class from the apscheduler library
from apscheduler.schedulers.blocking import BlockingScheduler

# Import custom classes and variables
from basic_package import BasicPackage
from prometheus_items import (up_status, pypi_request_time, pypi_successful_downloads, pypi_failed_downloads,
                              npm_request_time, npm_successful_downloads, npm_failed_downloads,
                              deb_request_time, deb_successful_downloads, deb_failed_downloads)

# Import constants from config file
from config import DEB_HASH, DEB_PACKAGE_URL, DEQUE_SIZE, DOWNLOAD_FAILED, INCORRECT_HASH, \
    NPM_HASH, NPM_PACKAGE_URL, PYPI_HASH, PYPI_PACKAGE_URL, REQUEST_EVERY, SLA, SUCCESS

# Set up logging
logger = logging.getLogger(__name__)
# Set the logging level for the apscheduler logger to ERROR to suppress unnecessary log messages
logging.getLogger('apscheduler').setLevel(logging.ERROR)
# Set the logging level for the current logger to INFO
logger.setLevel(logging.INFO)
# Create a formatter for the log messages
myformatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s', '%H:%M:%S')
# Create a stream handler to log messages to the console
myhandler = logging.StreamHandler()
# Set the formatter for the stream handler
myhandler.setFormatter(myformatter)
# Add the stream handler to the logger
logger.addHandler(myhandler)

# Create a deque to store the history of requests. It is used by the up_status variable.
requests_deque = collections.deque(maxlen=DEQUE_SIZE)


def process_package(package : BasicPackage) -> None:
    """
    Downloads the packages and checks if they are valid. 
    If the package is valid, update prometheus with information about the package.
    If the package is invalid, log an error and update prometheus with information about the failure.

    Args:
        package (BasicPackage): An instance of the BasicPackage class representing a package to be processed.
    """
    # Download the package and store exception (if exists) result in the exception variable
    exception = package.download_package()
    # If the download was successful (i.e. no exception was raised)
    if not exception:
        # Verify the package hash to ensure the package is valid
        if package.verify_package_hash():
            package.prometheus_info(requests_deque)
            logger.info(SUCCESS.format(package.package_url))
        else:
            # Update prometheus with information about the failed download
            package.prometheus_fail(requests_deque)
            logger.error(INCORRECT_HASH.format(package.url))
    # If the download was not successful (i.e. an exception was raised)
    else:
        # Update prometheus with information about the failed download
        package.prometheus_fail(requests_deque)
        logger.error(DOWNLOAD_FAILED.format(exception))
    # Update the up_status variable based on the success rate of recent requests
    up_status.set(SLA < (sum(requests_deque) / len(requests_deque)))


def main() -> None:
    """Set up scheduling and run the process_package function on a regular interval for each package type."""
    # Create instances of the BasicPackage class for each package type
    pypi_package = BasicPackage("pypi", PYPI_PACKAGE_URL, PYPI_HASH,
                                pypi_failed_downloads, pypi_successful_downloads, pypi_request_time)
    npm_package = BasicPackage("NPM", NPM_PACKAGE_URL, NPM_HASH,
                               npm_failed_downloads, npm_successful_downloads, npm_request_time)
    deb_package = BasicPackage("DEB", DEB_PACKAGE_URL, DEB_HASH,
                               deb_failed_downloads, deb_successful_downloads, deb_request_time)
    # Create a blocking scheduler
    scheduler = BlockingScheduler()
    # Add a job to the scheduler to run the process_package function on a regular interval for each package type
    scheduler.add_job(process_package, 'interval', seconds=REQUEST_EVERY, args=(
        pypi_package,), id='pypi_job',)
    scheduler.add_job(process_package, 'interval',
                      seconds=REQUEST_EVERY, args=(npm_package,), id='npm_job',)
    scheduler.add_job(process_package, 'interval',
                      seconds=REQUEST_EVERY, args=(deb_package,), id='deb_job',)
    # Start the scheduler
    scheduler.start()
