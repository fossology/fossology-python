# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import logging
from typing import List

import fossology
from fossology.exceptions import FossologyApiError, FossologyUnsupported
from fossology.obj import Group, MemberPerm, UserGroupMember

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

    def list_group_members(self, group_id: int) -> List:
        """Get the list of members for a given group (accessible groups for user, all groups for admin)

        API Endpoint: GET /groups/{id}/members

        :return: a list of members
        :rtype: list()
        :raises FossologyApiError: if the REST call failed
        """
        if fossology.versiontuple(self.version) < fossology.versiontuple("1.5.0"):
            description = f"Endpoint /groups/id/members is not supported by your Fossology API version {self.version}"
            raise FossologyUnsupported(description)

        response = self.session.get(f"{self.api}/groups/{group_id}/members")
        if response.status_code == 200:
            members_list = []
            response_list = response.json()
            for member in response_list:
                single_member = UserGroupMember.from_json(member)
                members_list.append(single_member)
            return members_list
        else:
            description = f"Unable to get a list of members for group {group_id}"
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

    def add_group_member(
        self, group_id: int, user_id: int, perm: MemberPerm = MemberPerm.USER
    ):
        """Add a user to a group

        API Endpoint: POST /groups/{group_id}/user/{user_id}

        :param group_id: the id of the group
        :param user_id: the id of the user
        :param perm: the permission level for the user
        :type group_id: int
        :type user_id: int
        :type perm: MemberPerm
        :raises FossologyApiError: if the REST call failed
        """
        if fossology.versiontuple(self.version) < fossology.versiontuple("1.5.0"):
            description = f"Endpoint /groups/id/user/id is not supported by your Fossology API version {self.version}"
            raise FossologyUnsupported(description)

        data = dict()
        data["perm"] = perm.value
        response = self.session.post(
            f"{self.api}/groups/{group_id}/user/{user_id}", json=data
        )
        if response.status_code == 200:
            logger.info(f"User {user_id} has been added to group {group_id}.")
        elif response.status_code == 400:
            logger.info(f"User {user_id} is already a member of group {group_id}.")
        else:
            description = (
                f"An error occurred while adding user {user_id} to group {group_id}"
            )
            raise FossologyApiError(description, response)
        return
