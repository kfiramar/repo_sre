'''This module contains the row class which represents a row in a CLI chart'''

import hashlib
import requests
from config import TIMEOUT


class BasicPackage:
    '''This class represents a row in a CLI chart'''

    def __init__(self, package_type, package_url, package_hash, failed_downloads_counter, successful_downloads_counter, request_time_summary, content=None):
        self.package_type = package_type
        self.package_url = package_url
        self.package_hash = package_hash
        self.content = content
        self.failed_downloads_counter = failed_downloads_counter
        self.successful_downloads_counter = successful_downloads_counter
        self.request_time_summary = request_time_summary

    def prometheus_fail(self, requests_deque):
        requests_deque.append(0)
        self.failed_downloads_counter.inc()

    def prometheus_info(self, requests_deque):
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

    def download_package(self):
        with self.request_time_summary.time():
            try:
                response = requests.get(self.package_url, timeout=TIMEOUT)
                response.raise_for_status()
                self.content = response.content
            except requests.exceptions.RequestException as exception:
                return exception

    def verify_package_hash(self) -> bool:
        """Verify the hash of the given package."""
        package_hash = hashlib.sha256(self.content).hexdigest()
        return package_hash == self.package_hash
