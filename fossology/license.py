# mypy: disable-error-code="attr-defined"
# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import json
import logging
from json.decoder import JSONDecodeError
from typing import Tuple
from urllib.parse import quote

from fossology.enums import LicenseType
from fossology.exceptions import FossologyApiError
from fossology.obj import License, Obligation

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def check_empty_response(response) -> bool:
    try:
        message = response.json().get("message")
        if message and message == "Can not exceed total pages: 0":
            return True
    except JSONDecodeError:
        # No JSON response available
        pass
    return False


class LicenseEndpoint:
    """Class dedicated to all "license" related endpoints"""

    def list_licenses(
        self,
        active: bool = False,
        kind: LicenseType = LicenseType.ALL,
        page_size: int = 100,
        page: int = 1,
        all_pages: bool = False,
    ) -> Tuple[list[License], int]:
        """Get all license from the DB

        API Endpoint: GET /license

        :param active: list only active licenses (default: False)
        :param kind: list only licenses from type LicenseType  (default: LicenseType.ALL)
        :param page_size: the maximum number of results per page (default: 100)
        :param page: the number of pages to be retrieved (default: 1)
        :param all_pages: get all licenses (default: False)
        :type active: bool
        :type kind: LicenseType
        :type page_size: int
        :type page: int
        :type all_pages: boolean
        :return: a list of licenses
        :rtype: List[License]
        :raises FossologyApiError: if the REST call failed
        """
        license_list = list()
        headers = {"limit": str(page_size)}
        if active:
            headers["active"] = json.dumps(True)
        if all_pages:
            # will be reset after the total number of pages has been retrieved from the API
            x_total_pages = 2
        else:
            x_total_pages = page
        while page <= x_total_pages:
            headers["page"] = str(page)
            response = self.session.get(
                f"{self.api}/license?kind={kind.value}", headers=headers
            )
            if response.status_code == 200:
                for license in response.json():
                    license_list.append(License.from_json(license))
                x_total_pages = int(response.headers.get("X-TOTAL-PAGES", 0))
                if not all_pages or x_total_pages == 0:
                    logger.info(
                        f"Retrieved page {page} of license, {x_total_pages} pages are in total available"
                    )
                    return license_list, x_total_pages
                page += 1
            else:
                if check_empty_response(response):
                    return license_list, 0
                description = (
                    f"Unable to retrieve the list of licenses from page {page}"
                )
                raise FossologyApiError(description, response)
        logger.info(f"Retrieved all {x_total_pages} pages of licenses")
        return license_list, x_total_pages

    def detail_license(
        self, shortname: str, group: int | None = None
    ) -> Tuple[int, License, list[Obligation]]:
        """Get a license from the DB

        API Endpoint: GET /license/{shortname}

        :param shortname: Short name of the license
        :param group: the group this license belongs to (default: None)
        :type name: str
        :type group: int
        :return: the license id, the license data and the associated obligations
        :rtype: tuple(int, License, list[Obligation])
        :raises FossologyApiError: if the REST call failed
        """
        headers = dict()
        if group:
            headers["groupName"] = group
        response = self.session.get(
            f"{self.api}/license/{quote(shortname)}", headers=headers
        )
        if response.status_code == 200:
            return License.from_json(response.json())
        elif response.status_code == 404:
            description = f"License {shortname} not found"
            raise FossologyApiError(description, response)
        else:
            description = f"Error while getting license {shortname}"
            raise FossologyApiError(description, response)

    def add_license(self, license: License, merge_request: bool = False):
        """Add a new license to the DB

        API Endpoint: POST /license

        License data are added to the request body, here is an example:

        >>> new_license = License(
        ...     "GPL-1.0",
        ...     "GNU General Public License 1.0",
        ...     "Text of the license...",
        ...     "http://www.gnu.org/licenses/gpl-1.0.txt",
        ...     "red",
        ...     "false"
        ... )
        >>> foss.add_license(new_license, merge_request=True) # doctest: +SKIP

        :param license: the license data
        :param merge_request: open a merge request for the license candidate? (default: False)
        :type license: License
        :type merge_request: bool
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"Content-Type": "application/json"}
        license_data = license.to_dict()
        if merge_request:
            license_data["mergeRequest"] = json.dumps(True)
        response = self.session.post(
            f"{self.api}/license", headers=headers, data=json.dumps(license_data)
        )
        if response.status_code == 201:
            logger.info(f"License {license.shortName} has been added to the DB")
        elif response.status_code == 409:
            logger.info(f"License {license.shortName} already exists")
        else:
            description = f"Error while adding new license {license.shortName}"
            raise FossologyApiError(description, response)

    def update_license(
        self,
        shortname: str,
        fullname: str = "",
        text: str = "",
        url: str = "",
        risk: int = 2,
    ):
        """Update a license

        API Endpoint: PATCH /license/{shortname}

        :param shortName: the short name of the license to be updated
        :param fullName: the new fullName of the license (optional)
        :param text: the new text of the license (optional)
        :param url: the new url of the license (optional)
        :param risk: the new risk of the license (default: 2)
        :type shortName: str
        :type fullName: str
        :type text: str
        :type url: str
        :type risk: int
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"Content-Type": "application/json"}
        license_data = {
            "fullName": fullname,
            "text": text,
            "url": url,
            "risk": str(risk),
        }
        response = self.session.patch(
            f"{self.api}/license/{quote(shortname)}",
            data=json.dumps(license_data),
            headers=headers,
        )
        if response.status_code == 200:
            logger.info(f"License {shortname} has been updated")
        else:
            description = f"Unable to update license {shortname}"
            raise FossologyApiError(description, response)
