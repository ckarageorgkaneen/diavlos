"""A module for fetching diaugeia API information."""

import logging
import requests

from .error import DiaugeiaErrorCode as ErrorCode

logger = logging.getLogger(__name__)

API_BASE_URL = "https://diavgeia.gov.gr/opendata"
API_TEST_URL = "https://test3.diavgeia.gov.gr/luminapi/opendata/decisions/"


class Diaugeia:

    def fetch(self, code):
        """Fetch ada information by code from diaugeia API.

            Args:
                code (string): The ada  code, e.g. ΒΛΕΖΝ-Ρ7Ν.

            Returns:
                :obj:`enum 'DiaugeiaErrorCode'`: A DiaugeiaErrorCode.NOT_FOUND
                    enum, if an ada for the code is not found.
                dict: ada information
        """
        resource = f'{API_TEST_URL}{code}.json'
        try:
            response = requests.get(resource).json()
        except ConnectionError:
            result = ErrorCode.NOT_FOUND
        else:
            result = ErrorCode.NOT_FOUND if 'errors' in response else response
        return result
