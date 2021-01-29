# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import logging

import fossology
from fossology.exceptions import FossologyApiError, FossologyUnsupported
from fossology.obj import License

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LicenseEndpoint:
    """Class dedicated to all "license" related endpoints"""

    def detail_license(self, name) -> License:
        """Get a license from the DB

        API Endpoint: GET /license

        :param name: Short name of the license
        :rtype name: str
        :return: a list of groups
        :rtype: License() object
        :raises FossologyApiError: if the REST call failed
        """
        if fossology.versiontuple(self.version) < fossology.versiontuple("1.1.3"):
            description = f"Endpoint /license is not supported by your Fossology API version {self.version}"
            raise FossologyUnsupported(description)

        headers = {"shortName": f"{name}"}
        response = self.session.get(f"{self.api}/license", headers=headers)
        if response.status_code == 200:
            return License.from_json(response.json())
        else:
            description = f"Unable to get license {name}"
            raise FossologyApiError(description, response)
