'''This module contains the row class which represents a row in a CLI chart'''

from collections import deque
import hashlib
import requests
from config import TIMEOUT


class BasicPackage:
    '''
    Initialize a Row object with the given attributes.

    Parameters:
        package_type (str): The type of package.
        package_url (str): The URL of the package.
        package_hash (str): The hash of the package.
        failed_downloads_counter (int): The counter for failed downloads.
        successful_downloads_counter (int): The counter for successful downloads.
        request_time_summary (float): Prometheus summary of request times.
        content (bytes, optional): The content of the package. Defaults to None.
    '''
    def __init__(self, package_type, package_url, package_hash, failed_downloads_counter, successful_downloads_counter, request_time_summary, content=None):
        self.package_type = package_type
        self.package_url = package_url
        self.package_hash = package_hash
        self.content = content
        self.failed_downloads_counter = failed_downloads_counter
        self.successful_downloads_counter = successful_downloads_counter
        self.request_time_summary = request_time_summary

    # Method to increase the counter for failed downloads and add 0 to the requests deque
    def prometheus_fail(self, requests_deque: deque) -> None:
        '''
        Increase the counter for failed downloads and add 0 to the requests deque.

        Parameters:
            requests_deque (deque): A deque of requests.
        '''
        requests_deque.append(0)
        self.failed_downloads_counter.inc()

    # Method to increase the counter for successful downloads and add 1 to the requests deque
    def prometheus_info(self, requests_deque: deque) -> None :
        '''
        Increase the counter for successful downloads and add 1 to the requests deque.

        Parameters:
            requests_deque (deque): A deque of requests.
        '''
        requests_deque.append(1)
        self.successful_downloads_counter.inc()

    @classmethod
    def create_downloaded_package(cls, package_type, failed_downloads_counter, successful_downloads_counter, request_time_summary, package_url, package_hash):
        with request_time_summary.time():
            response = requests.get(package_url, timeout=TIMEOUT)
            response.raise_for_status()
            return cls(
                package_type=package_type,
                package_url=package_url,
                package_hash=package_hash,
                content=response.content,
                failed_downloads_counter=failed_downloads_counter,
                successful_downloads_counter=successful_downloads_counter,
                request_time_summary=request_time_summary
            )

    # Method to download the package
    def download_package(self) -> str:
        with self.request_time_summary.time():
            try:
                # Send a GET request to the package URL
                response = requests.get(self.package_url, timeout=TIMEOUT)
                # Raise exception if the request was not successful
                response.raise_for_status()
                # Set the package content to the response content
                self.content = response.content
            except requests.exceptions.RequestException as exception:
                return exception

    def verify_package_hash(self) -> bool:
        """Verify the hash of the given package."""
        # Calculate the hash of the package content
        package_hash = hashlib.sha256(self.content).hexdigest()
        # Return True if the calculated hash matches the package hash, False otherwise
        return package_hash == self.package_hash
