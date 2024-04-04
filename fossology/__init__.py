# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging
import sys
from datetime import date, timedelta

import requests

from fossology.enums import TokenScope
from fossology.exceptions import AuthenticationError, FossologyApiError
from fossology.folders import Folders
from fossology.groups import Groups
from fossology.items import Items
from fossology.jobs import Jobs
from fossology.license import LicenseEndpoint
from fossology.obj import Agents, ApiInfo, HealthInfo, User
from fossology.report import Report
from fossology.search import Search
from fossology.uploads import Uploads
from fossology.users import Users

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def fossology_token(
    url,
    username,
    password,
    token_name,
    token_scope=TokenScope.READ,
    token_expire=None,
    version="v1",
):
    """Generate an API token using username/password

    API endpoint: POST /tokens

    :Example:

    >>> from fossology import fossology_token # doctest: +SKIP
    >>> from fossology.obj import TokenScope # doctest: +SKIP
    >>> token = fossology_token("https://fossology.example.com/repo", "Me", "MyPassword", "MyToken", version="v1") # doctest: +SKIP


    :param url: the URL of the Fossology server
    :param username: name of the user the token will be generated for
    :param password: the password of the user
    :param name: the name of the token
    :param scope: the scope of the token (default: TokenScope.READ)
    :param expire: the expire date of the token, e.g. 2019-12-25 (default: max. 30 days)
    :param version: the version of the API to use (default: "v1")
    :type url: string
    :type username: string
    :type password: string
    :type name: string
    :type scope: TokenScope
    :type expire: string
    :type version: string
    :return: the new token
    :rtype: string
    :raises AuthenticationError: if the username or password is incorrect
    :raises FossologyApiError: if another error occurs
    """
    if version == "v2":
        data = {
            "username": username,
            "password": password,
            "tokenName": token_name,
            "tokenScope": token_scope.value,
        }
    else:
        data = {
            "username": username,
            "password": password,
            "token_name": token_name,
            "token_scope": token_scope.value,
        }
    if token_expire:
        if version == "v2":
            data["tokenExpire"] = token_expire
        else:
            data["token_expire"] = token_expire
    else:
        now = date.today()
        if version == "v2":
            data["tokenExpire"] = str(now + timedelta(days=30))
        else:
            data["token_expire"] = str(now + timedelta(days=30))
    try:
        response = requests.post(url + "/api/" + version + "/tokens", data=data)
        if response.status_code == 201:
            token = response.json()["Authorization"]
            return token.replace("Bearer ", "")
        elif response.status_code == 404:
            description = "Authentication error"
            raise AuthenticationError(description, response)
        else:
            description = "Error while generating new token"
            raise FossologyApiError(description, response)
    except requests.exceptions.ConnectionError as error:
        sys.exit(f"Server {url} does not seem to be running or is unreachable: {error}")


class Fossology(
    Folders, Groups, Items, LicenseEndpoint, Uploads, Jobs, Report, Users, Search
):
    """Main Fossology API class

    Authentication against a running Fossology instance is performed using an API token.

    :Example:

    >>> from fossology import Fossology
    >>> foss = Fossology(FOSS_URL, FOSS_TOKEN) # doctest: +SKIP

    :param url: URL of the Fossology instance
    :param token: The API token generated using the Fossology UI
    :param version: the version of the API to use (default: "v1")
    :type url: str
    :type token: str
    :type version: str
    :raises FossologyApiError: if a REST call failed
    :raises AuthenticationError: if the user couldn't be authenticated
    """

    def __init__(self, url, token, version="v1"):
        self.host = url
        self.token = token
        self.users = list()
        self.folders = list()
        self.api = f"{self.host}/api/{version}"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.info = self.get_info()
        self.health = self.get_health()
        self.user = self.get_self()
        self.name = self.user.name
        self.rootFolder = self.detail_folder(self.user.rootFolderId)
        self.folders = self.list_folders()

        logger.info(
            f"Authenticated as {self.user.name} against {self.host} using API version {self.info.version}"
        )

    def get_self(self):
        """Perform the first API request and populate user variables

        API Endpoint: GET /users/self

        :return: the authenticated user's details
        :rtype: User
        :raises FossologyApiError: if the REST call failed
        :raises AuthenticationError: if the user couldn't be found
        """
        response = self.session.get(f"{self.api}/users/self")
        if response.status_code == 200:
            user_agents = None
            user_details = response.json()
            if user_details.get("agents"):
                user_agents = Agents.from_json(user_details["agents"])
            user = User.from_json(user_details)
            user.agents = user_agents
            return user
        else:
            description = "Error while getting details about authenticated user"
            raise FossologyApiError(description, response)

    def close(self):
        self.session.close()

    def get_info(self) -> ApiInfo:
        """Get info from the server

        API endpoint: GET /info

        :return: the API information
        :rtype: ApiInfo
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/info")
        if response.status_code == 200:
            return ApiInfo.from_json(response.json())
        else:
            description = "Error while getting API info"
            raise FossologyApiError(description, response)

    def get_health(self) -> ApiInfo:
        """Get health from the server

        API endpoint: GET /health

        :return: the server health information
        :rtype: HealthInfo
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/health")
        if response.status_code == 200:
            return HealthInfo.from_json(response.json())
        else:
            description = "Error while getting health info"
            raise FossologyApiError(description, response)
