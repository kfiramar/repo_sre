import configobj

# create all the variables
config = configobj.ConfigObj('config.ini')

PYPI_HASH = config['PYPI']['HASH']
PYPI_PACKAGE_VERSION = config['PYPI']['PACKAGE_VERSION']
PYPI_PACKAGE_NAME = config['PYPI']['PACKAGE_NAME']
PYPI_PACKAGE_URL = config['PYPI']['PACKAGE_URL'].format(
    PACKAGE_NAME=PYPI_PACKAGE_NAME,
    PACKAGE_LETTER=PYPI_PACKAGE_NAME[0],
    PACKAGE_VERSION=PYPI_PACKAGE_VERSION,
)

NPM_HASH = config['NPM']['HASH']
NPM_PACKAGE_VERSION = config['NPM']['PACKAGE_VERSION']
NPM_PACKAGE_NAME = config['NPM']['PACKAGE_NAME']
NPM_PACKAGE_URL = config['NPM']['PACKAGE_URL'].format(
    PACKAGE_NAME=PYPI_PACKAGE_NAME,
    PACKAGE_LETTER=PYPI_PACKAGE_NAME[0],
    PACKAGE_VERSION=PYPI_PACKAGE_VERSION,
)

DEB_HASH = config['DEB']['HASH']
DEB_PACKAGE_VERSION = config['DEB']['PACKAGE_VERSION']
DEB_PACKAGE_NAME = config['DEB']['PACKAGE_NAME']
DEB_PACKAGE_URL = config['DEB']['PACKAGE_URL'].format(
    PACKAGE_NAME=PYPI_PACKAGE_NAME,
    PACKAGE_LETTER=PYPI_PACKAGE_NAME[0],
    PACKAGE_VERSION=PYPI_PACKAGE_VERSION,
)


REQUEST_EVERY = config['GENERAL'].as_int('REQUEST_EVERY')
TIMEOUT = config['GENERAL'].as_float('TIMEOUT')
DEQUE_SIZE = config['GENERAL'].as_int('DEQUE_SIZE')
SLA = config['GENERAL'].as_float('SLA')

