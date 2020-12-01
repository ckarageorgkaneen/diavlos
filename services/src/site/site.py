import logging
import yaml

import mwclient

from services.data import IN_FILES

logger = logging.getLogger(__name__)


class SiteError(Exception):
    pass


def _error(message):
    logger.error(message)
    raise SiteError(message)


class Site:
    _URL = 'diadikasies.dev.grnet.gr'
    _SCHEME = 'https'
    _PATH = '/'
    _CREDENTIALS_FILE = IN_FILES['site_credentials']

    def __init__(self):
        self._client = mwclient.Site(
            self._URL, scheme=self._SCHEME, path=self._PATH)
        self.__credentials = None
        self.pages = self._client.pages
        self.categories = self._client.categories
        self.api = self._client.api
        self.get = self._client.get

    @property
    def _credentials(self):
        if self.__credentials is None:
            with open(self._CREDENTIALS_FILE) as f:
                self.__credentials = tuple(yaml.safe_load(f).values())
        return self.__credentials

    def auto_login(self):
        self._client.login(*self._credentials)

    def login(self, username, password):
        try:
            self._client.login(username, password)
        except (mwclient.errors.LoginError,
                mwclient.errors.APIError) as e:
            _error(str(e))
