# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging
from typing import TYPE_CHECKING

from fossology.enums import MemberPerm
from fossology.exceptions import FossologyApiError
from fossology.obj import Group, UserGroupMember

if TYPE_CHECKING:
    import requests

    from fossology.obj import User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Groups:
    """Class dedicated to all "groups" related endpoints"""

    api: str
    session: "requests.Session"
    user: "User"

    def list_groups(self, deletable: bool = False) -> list[Group]:

        """Get the list of groups (accessible groups for user, all groups for admin)

        If parameter deletable is True, the method will return only deletable groups.

        API Endpoint: GET /groups

        :param deletable: wether to limit the scope only to deletable groups
        :type deletable: bool (default: False)
        :return: a list of groups
        :rtype: list()
        :raises FossologyApiError: if the REST call failed
        """
        endpoint = f"{self.api}/groups"
        endpoint += "/deletable" if deletable else ""
        response = self.session.get(endpoint)
        if response.status_code == 200:
            groups_list = []
            response_list = response.json()
            for group in response_list:
                single_group = Group.from_json(group)
                groups_list.append(single_group)
            return groups_list
        else:
            description = f"Unable to get a list of {'deletable ' if deletable else ''}groups for {self.user.name}"
            raise FossologyApiError(description, response)

    def list_group_members(self, group_id: int) -> list[UserGroupMember]:
        """Get the list of members for a given group (accessible groups for user, all groups for admin)

        API Endpoint: GET /groups/{id}/members

        :return: a list of members
        :rtype: list()
        :raises FossologyApiError: if the REST call failed
        """
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

    def create_group(self, name: str) -> None:
        """Create a group

        API Endpoint: POST /groups

        :param name: the name of the group
        :type name: str
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"name": f"{name}"}
        response = self.session.post(f"{self.api}/groups", headers=headers)

        if response.status_code == 200:
            logger.info(f"Group '{name}' has been added")
        else:
            description = f"Group {name} already exists, failed to create group or no group name provided"
            raise FossologyApiError(description, response)

    def delete_group(self, group_id: int) -> None:
        """Delete a group

        API Endpoint: DELETE /groups/{group_id}

        :param group_id: the id of the group
        :type group_id: int
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.delete(f"{self.api}/groups/{group_id}")

        if response.status_code == 202:
            logger.info(f"Group {group_id} will be deleted")
        else:
            description = f"Group {group_id} could not be deleted"
            raise FossologyApiError(description, response)

    def add_group_member(
        self, group_id: int, user_id: int, perm: MemberPerm = MemberPerm.USER
    ) -> None:
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
        data = dict()
        data["perm"] = perm.value
        response = self.session.post(
            f"{self.api}/groups/{group_id}/user/{user_id}", json=data
        )
        if response.status_code == 201:
            logger.info(f"User {user_id} has been added to group {group_id}.")
        elif response.status_code == 400:
            logger.info(f"User {user_id} is already a member of group {group_id}.")
        else:
            description = (
                f"An error occurred while adding user {user_id} to group {group_id}"
            )
            raise FossologyApiError(description, response)

    def change_group_member_permission(
        self, group_id: int, user_id: int, perm: MemberPerm
    ) -> None:
        """Change the permission of a user in a group

        API Endpoint: PUT /groups/{group_id}/user/{user_id}

        :param group_id: the id of the group
        :param user_id: the id of the user
        :param perm: the new permission level for the user
        :type group_id: int
        :type user_id: int
        :type perm: MemberPerm
        :raises FossologyApiError: if the REST call failed
        """
        data = {"perm": perm.value}
        response = self.session.put(
            f"{self.api}/groups/{group_id}/user/{user_id}", json=data
        )
        if response.status_code == 202:
            logger.info(
                f"Permission of user {user_id} in group {group_id} has been updated to {perm.name}."
            )
        elif response.status_code == 400:
            description = f"Validation error while changing permission of user {user_id} in group {group_id}."
            raise FossologyApiError(description, response)
        elif response.status_code == 403:
            description = f"Not authorized to change permission of user {user_id} in group {group_id}."
            raise FossologyApiError(description, response)
        elif response.status_code == 404:
            description = f"User {user_id} or group {group_id} not found."
            raise FossologyApiError(description, response)
        else:
            description = (
                f"An error occurred while changing permission of user {user_id} in group {group_id}"
            )
            raise FossologyApiError(description, response)

    def delete_group_member(self, group_id: int, user_id: int) -> None:
        """Delete a user from a group

        API Endpoint: DELETE /groups/{group_id}/user/{user_id}

        :param group_id: the id of the group
        :param user_id: the id of the user
        :type group_id: int
        :type user_id: int
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.delete(f"{self.api}/groups/{group_id}/user/{user_id}")
        if response.status_code == 202:
            logger.info(f"User {user_id} will be removed from group {group_id}.")
        elif response.status_code == 400:
            description = f"Validation error while removing member {user_id} from group {group_id}."
            raise FossologyApiError(description, response)
        elif response.status_code == 404:
            description = f"Member {user_id} or group {group_id} not found."
            raise FossologyApiError(description, response)
        else:
            description = (
                f"An error occurred while deleting user {user_id} from group {group_id}"
            )
            raise FossologyApiError(description, response)