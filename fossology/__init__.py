# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import re
import logging
import requests
from datetime import date, timedelta

from .obj import Agents, User, TokenScope, SearchTypes
from .folders import Folders
from .uploads import Uploads
from .jobs import Jobs
from .report import Report
from .exceptions import AuthenticationError, FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def fossology_token(
    url, username, password, token_name, token_scope=TokenScope.READ, token_expire=None
):
    """Generate an API token using username/password

    API endpoint: POST /tokens

    :Example:

    >>> from fossology import fossology_token
    >>> from fossology.obj import TokenScope
    >>> token = fossology_token("https://fossology.example.com", "Me", "MyPassword", "MyToken")


    :param url: the URL of the Fossology server
    :param username: name of the user the token will be generated for
    :param password: the password of the user
    :param name: the name of the token
    :param scope: the scope of the token (default: READ)
    :param expire: the expire date of the token (default max. 30 days)
    :type url: string
    :type username: string
    :type password: string
    :type name: string
    :type scope: TokenScope (default TokenScope.READ)
    :type expire: string, e.g. 2019-12-25
    :return: the new token
    :rtype: string
    """
    data = {
        "username": username,
        "password": password,
        "token_name": token_name,
        "token_scope": token_scope.value,
    }
    if token_expire:
        data["token_expire"] = token_expire
    else:
        now = date.today()
        data["token_expire"] = str(now + timedelta(days=30))
    try:
        response = requests.post(url + "/api/v1/tokens", data=data)
        if response.status_code == 201:
            token = response.json()["Authorization"]
            return re.sub("Bearer ", "", token)
        else:
            description = "Error while generating new token"
            raise FossologyApiError(description, response)
    except requests.exceptions.ConnectionError as error:
        exit(f"Server {url} does not seem to be running or is unreachable: {error}")


class Fossology(Folders, Uploads, Jobs, Report):

    """Main Fossology API class

    Authentication against a running Fossology instance is performed using an API token.

    :Example:

    >>> from fossology import Fossology
    >>> foss = Fossology(FOSS_URL, FOSS_TOKEN, username)

    .. note::

        The class instantiation exits if the session with the Fossology server
        can't be established

    :param url: URL of the Fossology instance
    :param token: The API token generated using the Fossology UI
    :param name: The name of the token owner
    :type url: str
    :type token: str
    :type name: str
    :raises AuthenticationError: if the user couldn't be found
    """

    def __init__(self, url, token, name):
        self.host = url
        self.token = token
        self.name = name
        self.users = list()
        self.folders = list()

        self.api = f"{self.host}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

        self.user = self._auth()
        self.version = self.get_version()
        self.rootFolder = self.detail_folder(self.user.rootFolderId)
        self.folders = self.list_folders()

        logger.info(
            f"Authenticated as {self.user.name} against {self.host} using API version {self.version}"
        )

    def _auth(self):
        """Perform the first API request and populate user variables

        :return: the authenticated user's details
        :rtype: User
        :raises AuthenticationError: if the user couldn't be found
        """
        self.users = self.list_users()
        for user in self.users:
            if user.name == self.name:
                self.user = user
                return self.user
        logger.error(f"User {self.name} was not found")
        raise AuthenticationError(self.host)

    def close(self):
        self.session.close()

    def get_version(self):
        """Get API version from the server

        API endpoint: GET /version

        :return: the API version string
        :rtype: string
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/version")
        if response.status_code == 200:
            return response.json()["version"]
        else:
            description = "Error while getting API version"
            raise FossologyApiError(description, response)

    def detail_user(self, user_id):
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
        """ List all users from the Fossology instance

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
                    if agents := user.get("agents"):
                        foss_user.agents = Agents.from_json(agents)
                    users_list.append(foss_user)
            return users_list
        else:
            description = f"Unable to get a list of users from {self.host}"
            raise FossologyApiError(description, response)

    def delete_user(self, user):
        """Delete a Fossology user.

        API Endpoint: DELETE /users/{id}

        :param user: the user to be deleted
        :type user: User
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.delete(f"{self.api}/users/{user.id}")
        print(response.json())
        if response.status_code == 202:
            return
        else:
            description = f"Error while deleting user {user.name} ({user.id})"
            raise FossologyApiError(description, response)

    def search(
        self,
        searchType=SearchTypes.ALLFILES,
        filename=None,
        tag=None,
        filesizemin=None,
        filesizemax=None,
        license=None,
        copyright=None,
    ):
        """Search for a specific file

        API Endpoint: GET /search

        :param searchType: Limit search to: directory, allfiles (default), containers
        :param filename: Filename to find, can contain % as wild-card
        :param tag: tag to find
        :param filesizemin: Min filesize in bytes
        :param filesizemax: Max filesize in bytes
        :param license: License search filter
        :param copyright: Copyright search filter
        :type searchType: SearchType Enum
        :type filename: string
        :type tag: string
        :type filesizemin: int
        :type filesizemax: int
        :type license: string
        :type copyright: string
        :return: list of items corresponding to the search criteria
        :rtype: JSON
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"searchType": searchType.value}
        if filename:
            headers["filename"] = filename
        if tag:
            headers["tag"] = tag
        if filesizemin:
            headers["filesizemin"] = filesizemin
        if filesizemax:
            headers["filesizemax"] = filesizemax
        if license:
            headers["license"] = license
        if copyright:
            headers["copyright"] = copyright

        response = self.session.get(f"{self.api}/search", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            description = "Unable to get a result with the given search criteria"
            raise FossologyApiError(description, response)
