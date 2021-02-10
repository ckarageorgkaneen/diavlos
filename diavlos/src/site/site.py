import logging
import yaml

import mwclient

from diavlos.data import IN_FILES

logger = logging.getLogger(__name__)


class SiteError(Exception):
    pass


def _error(message):
    logger.error(message)
    raise SiteError(message)


class Site:
    _DEFAULT_CONFIG_FILE = IN_FILES['greek_site_config']
    _SCHEME = 'https'
    _PATH = '/'

    def __init__(self, config_file=_DEFAULT_CONFIG_FILE):
        self.__client = None
        self._config_file = config_file
        self.__config = None
        self._logged_in = False
        self.categories = self._client.categories
        self.api = self._client.api
        self.get = self._client.get

    @property
    def _client(self):
        if self.__client is None:
            self.__client = mwclient.Site(
                self._config['url'], scheme=self._SCHEME, path=self._PATH)
        return self.__client

    @property
    def _config(self):
        if self.__config is None:
            with open(self._config_file) as f:
                self.__config = yaml.safe_load(f)
        return self.__config

    def pages(self, name):
        try:
            return self._client.pages[name]
        except mwclient.errors.InvalidPageTitle as e:
            message = f'Page title: {name}. {str(e)}'
            _error(message)

    def auto_login(self):
        self._client.login(self._config['username'], self._config['password'])

    def login(self, username, password, force=False):
        if self._logged_in and not force:
            return
        try:
            self._client.login(username, password)
        except (mwclient.errors.LoginError,
                mwclient.errors.APIError) as e:
            _error(str(e))
        else:
            self._logged_in = True
