# Set up Prometheus metrics
from prometheus_client import Counter, Gauge, Summary, start_http_server

start_http_server(8000)
up_status = Gauge('up_status', 'Repository up status')

pypi_request_time = Summary(
    'pypi_request_processing_seconds', 'Time spent processing request')
pypi_successful_downloads = Counter(
    'pypi_download_success', 'Number of successful package downloads')
pypi_failed_downloads = Counter(
    'pypi_download_failure', 'Number of failed package downloads')

npm_request_time = Summary(
    'npm_request_processing_seconds', 'Time spent processing request')
npm_successful_downloads = Counter(
    'npm_download_success', 'Number of successful package downloads')
npm_failed_downloads = Counter(
    'npm_download_failure', 'Number of failed package downloads')

deb_request_time = Summary(
    'deb_request_processing_seconds', 'Time spent processing request')
deb_successful_downloads = Counter(
    'deb_download_success', 'Number of successful package downloads')
deb_failed_downloads = Counter(
    'deb_download_failure', 'Number of failed package downloads')
