# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging
import requests

from .obj import Agents, User
from .folders import Folders
from .uploads import Uploads
from .jobs import Jobs
from .exceptions import AuthenticationError, AuthorizationError, FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Fossology(Folders, Uploads, Jobs):

    """Main Fossology API class

    Authentication against a running Fossology instance is performed using an API token.

    :Example:

    >>> from fossology.api import Fossology
    >>> foss = Fossology(FOSS_URL, FOSS_TOKEN)

    .. note: The class instantiation exits if the session with the Fossology server
             can't be established

    :param url: URL of the Fossology instance
    :type url: str
    :param token: The API token generated using the Fossology UI
    :type token: str
    """

    def __init__(self, url, token, email):
        self.host = url
        self.token = token
        self.email = email
        self.users = list()
        self.folders = list()

        self.api = self.host + "/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

        self.user = self._auth()
        self.rootFolder = self.detail_folder(self.user.rootFolderId)
        self.folders = self.list_folders()

        logger.debug(self.user)
        logger.debug(self.rootFolder)

    def _auth(self):
        """Perform the first API request and populate user variables

        :return: the authenticated user's details - or None if the REST call failed
        :rtype: User() object
        """
        try:
            self.users = self.list_users()
            for user in self.users:
                if user.email == self.email:
                    self.user = user
                    logger.info(
                        f"Authenticated as {self.user.name} against {self.host}."
                    )
                    return self.user
            logger.error(f"User with email {self.email} was not found")
            raise AuthenticationError(self.host)
        except AuthorizationError as error:
            logger.error(error.message)
            return None

    def detail_user(self, user_id):
        """Get details of Fossology user.

        API Endpoint: GET /users/{id}

        :param id: the ID of the user
        :type id: int
        :return: the requested user's details - or None if the REST call failed
        :rtype: User() object
        """
        try:
            response = self.session.get(self.api + f"/users/{user_id}")
            if response.status_code == 200:
                user_details = response.json()
                if user_details["agents"]:
                    user_agents = Agents.from_json(user_details["agents"])
                user = User.from_json(user_details)
                user.agents = user_agents
                return user
            else:
                description = f"Error while getting details for user {user_id}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)
            return None

    def list_users(self):
        """ List all users from the Fossology instance

        API Endpoint: GET /users
        """
        try:
            response = self.session.get(self.api + "/users")
            if response.status_code == 200:
                users_list = list()
                for user in response.json():
                    foss_user = User.from_json(user)
                    if user["agents"]:
                        foss_user.agents = Agents.from_json(user["agents"])
                    users_list.append(foss_user)
                return users_list
            else:
                description = f"Unable to get a list of users from {self.host}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)
