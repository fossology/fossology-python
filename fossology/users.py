# mypy: disable-error-code="attr-defined"
# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT
import logging

from fossology.exceptions import FossologyApiError
from fossology.obj import Agents, User

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Users:
    """Class dedicated to all "users" related endpoints"""

    def detail_user(self, user_id: int):
        """Get details of Fossology user.

        API Endpoint: GET /users/{id}

        :param id: the ID of the user
        :type id: int
        :return: the requested user's details
        :rtype: User
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/users/{user_id}")
        if response.status_code == 200:
            user_agents = None
            user_details = response.json()
            if user_details.get("agents"):
                user_agents = Agents.from_json(user_details["agents"])
            user = User.from_json(user_details)
            user.agents = user_agents
            return user
        else:
            description = f"Error while getting details for user {user_id}"
            raise FossologyApiError(description, response)

    def list_users(self):
        """List all users from the Fossology instance

        API Endpoint: GET /users

        :return: the list of users
        :rtype: list of User
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/users")
        if response.status_code == 200:
            users_list = list()
            for user in response.json():
                if user.get("name") == "Default User":
                    continue
                if user.get("email"):
                    foss_user = User.from_json(user)
                    agents = user.get("agents")
                    if agents:
                        foss_user.agents = Agents.from_json(agents)
                    users_list.append(foss_user)
            return users_list
        else:
            description = f"Unable to get a list of users from {self.host}"
            raise FossologyApiError(description, response)

    def create_user(self, user_spec: dict):
        """Create a new Fossology user

        API Endpoint: POST /users

        :Example:

        >>> user_spec = {
        ...     "id": 0,
        ...     "name": "New User",
        ...     "description": "A brand new user",
        ...     "email": "new.user@fossology.com",
        ...     "accessLevel": "none",
        ...     "rootFolderId": 0,
        ...     "emailNotification": True,
        ...     "defaultGroup": 0,
        ...     "agents": {
        ...         "bucket": True,
        ...         "copyright_email_author": True,
        ...         "ecc": True,
        ...         "keyword": True,
        ...         "mime": True,
        ...         "monk": True,
        ...         "nomos": True,
        ...         "ojo": True,
        ...         "package": True,
        ...         "reso": True,
        ...         "heritage": True
        ...     },
        ...     "defaultBucketpool": 0,
        ...     "user_pass": "$PASSWORD",
        ...     "defaultVisibility": "public"
        ... }
        >>> foss.create_user(user_spec)  # doctest: +SKIP

        :param user_spec: the user creation data
        :type user_spec: dict
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.post(f"{self.api}/users", json=user_spec)
        if response.status_code == 201:
            logger.info(
                f"User {user_spec['name']} was created, call list_users() to get more information."
            )
        elif response.status_code == 409:
            logger.info(f"User {user_spec['name']} already exists.")
        else:
            description = f"Error while creating user {user_spec['name']}"
            raise FossologyApiError(description, response)

    def delete_user(self, user):
        """Delete a Fossology user.

        API Endpoint: DELETE /users/{id}

        :param user: the user to be deleted
        :type user: User
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.delete(f"{self.api}/users/{user.id}")

        if response.status_code == 202:
            return
        else:
            description = f"Error while deleting user {user.name} ({user.id})"
            raise FossologyApiError(description, response)
