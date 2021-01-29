# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import logging
from typing import List

import fossology
from fossology.exceptions import FossologyApiError, FossologyUnsupported
from fossology.obj import Group

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Groups:
    """Class dedicated to all "groups" related endpoints"""

    def list_groups(self) -> List:
        """Get the list of groups (accessible groups for user, all groups for admin)

        API Endpoint: GET /groups

        :return: a list of groups
        :rtype: list()
        :raises FossologyApiError: if the REST call failed
        """
        if fossology.versiontuple(self.version) < fossology.versiontuple("1.2.1"):
            description = f"Endpoint /groups is not supported by your Fossology API version {self.version}"
            raise FossologyUnsupported(description)

        response = self.session.get(f"{self.api}/groups")
        if response.status_code == 200:
            groups_list = []
            response_list = response.json()
            for group in response_list:
                single_group = Group.from_json(group)
                groups_list.append(single_group)
            return groups_list
        else:
            description = f"Unable to get a list of groups for {self.user.name}"
            raise FossologyApiError(description, response)

    def create_group(self, name):
        """Create a group

        API Endpoint: POST /groups

        :param name: the name of the group
        :type name: str
        :raises FossologyApiError: if the REST call failed
        """
        if fossology.versiontuple(self.version) < fossology.versiontuple("1.2.1"):
            description = f"Endpoint /groups is not supported by your Fossology API version {self.version}"
            raise FossologyUnsupported(description)

        headers = {"name": f"{name}"}
        response = self.session.post(f"{self.api}/groups", headers=headers)

        if response.status_code == 200:
            logger.info(f"Group '{name}' has been added")
            return
        else:
            description = f"Group {name} already exists, failed to create group or no group name provided"
            raise FossologyApiError(description, response)
