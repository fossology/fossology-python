# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import logging
import re
from datetime import date, timedelta
from typing import Dict, List

import requests

from fossology.exceptions import (
    AuthenticationError,
    AuthorizationError,
    FossologyApiError,
    FossologyUnsupported,
)
from fossology.folders import Folders
from fossology.groups import Groups
from fossology.jobs import Jobs
from fossology.license import LicenseEndpoint
from fossology.obj import (
    Agents,
    ApiInfo,
    File,
    HealthInfo,
    SearchTypes,
    TokenScope,
    Upload,
    User,
    get_options,
)
from fossology.report import Report
from fossology.uploads import Uploads

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def versiontuple(v):
    return tuple(map(int, (v.split("."))))


def search_headers(
    searchType: SearchTypes = SearchTypes.ALLFILES,
    upload: Upload = None,
    filename: str = None,
    tag: str = None,
    filesizemin: int = None,
    filesizemax: int = None,
    license: str = None,
    copyright: str = None,
    group: str = None,
) -> Dict:
    headers = {"searchType": searchType.value}
    if upload:
        headers["uploadId"] = str(upload.id)
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
    if group:
        headers["groupName"] = group
    return headers


def fossology_token(
    url, username, password, token_name, token_scope=TokenScope.READ, token_expire=None
):
    """Generate an API token using username/password

    API endpoint: POST /tokens

    :Example:

    >>> from fossology import fossology_token # doctest: +SKIP
    >>> from fossology.obj import TokenScope # doctest: +SKIP
    >>> token = fossology_token("https://fossology.example.com", "Me", "MyPassword", "MyToken") # doctest: +SKIP


    :param url: the URL of the Fossology server
    :param username: name of the user the token will be generated for
    :param password: the password of the user
    :param name: the name of the token
    :param scope: the scope of the token (default: TokenScope.READ)
    :param expire: the expire date of the token, e.g. 2019-12-25 (default: max. 30 days)
    :type url: string
    :type username: string
    :type password: string
    :type name: string
    :type scope: TokenScope
    :type expire: string
    :return: the new token
    :rtype: string
    :raises AuthenticationError: if the username or password is incorrect
    :raises FossologyApiError: if another error occurs
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
        elif response.status_code == 404:
            description = "Authentication error"
            raise AuthenticationError(description, response)
        else:
            description = "Error while generating new token"
            raise FossologyApiError(description, response)
    except requests.exceptions.ConnectionError as error:
        exit(f"Server {url} does not seem to be running or is unreachable: {error}")


class Fossology(Folders, Groups, LicenseEndpoint, Uploads, Jobs, Report):

    """Main Fossology API class

    Authentication against a running Fossology instance is performed using an API token.

    :Example:

    >>> from fossology import Fossology
    >>> foss = Fossology(FOSS_URL, FOSS_TOKEN, username) # doctest: +SKIP

    :param url: URL of the Fossology instance
    :param token: The API token generated using the Fossology UI
    :param name: The name of the token owner (deprecated since API version 1.2.3)
    :type url: str
    :type token: str
    :type name: str (deprecated since API version 1.2.3)
    :raises FossologyApiError: if a REST call failed
    :raises AuthenticationError: if the user couldn't be authenticated
    """

    def __init__(self, url, token, name=None):
        self.host = url
        self.token = token
        self.users = list()
        self.folders = list()

        self.api = f"{self.host}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.version = self.get_version()
        if versiontuple(self.version) >= versiontuple("1.3.3"):
            self.info = self.get_info()
            self.health = self.get_health()

        self.user = self.get_self(name)
        self.name = self.user.name
        self.rootFolder = self.detail_folder(self.user.rootFolderId)
        self.folders = self.list_folders()

        logger.info(
            f"Authenticated as {self.user.name} against {self.host} using API version {self.version}"
        )

    def get_self(self, name=None):
        """Perform the first API request and populate user variables

        API Endpoint: GET /users/self

        :return: the authenticated user's details
        :rtype: User
        :raises FossologyApiError: if the REST call failed
        :raises AuthenticationError: if the user couldn't be found
        """
        if versiontuple(self.version) >= versiontuple("1.2.3"):
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
        else:
            if not name:
                description = "You need to provide a username to create an API session"
                raise AuthenticationError(description)
            self.users = self.list_users()
            for user in self.users:
                if user.name == name:
                    self.user = user
                    return self.user
            description = f"User {name} was not found on {self.host}"
            raise AuthenticationError(description)

    def close(self):
        self.session.close()

    def get_version(self):
        """Get API version from the server

        API endpoint: GET /version (deprecated since API version 1.3.3)

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

    def search(
        self,
        searchType: SearchTypes = SearchTypes.ALLFILES,
        upload: Upload = None,
        filename: str = None,
        tag: str = None,
        filesizemin: int = None,
        filesizemax: int = None,
        license: str = None,
        copyright: str = None,
        group: str = None,
    ):
        """Search for a specific file

        API Endpoint: GET /search

        :param searchType: Limit search to: directory, allfiles (default), containers
        :param upload: Limit search to a specific upload
        :param filename: Filename to find, can contain % as wild-card
        :param tag: tag to find
        :param filesizemin: Min filesize in bytes
        :param filesizemax: Max filesize in bytes
        :param license: License search filter
        :param copyright: Copyright search filter
        :param group: the group name to choose while performing search (default: None)
        :type searchType: one of SearchTypes Enum
        :type upload: Upload
        :type filename: string
        :type tag: string
        :type filesizemin: int
        :type filesizemax: int
        :type license: string
        :type copyright: string
        :type group: string
        :return: list of items corresponding to the search criteria
        :rtype: JSON
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        """
        headers = search_headers(
            searchType,
            upload,
            filename,
            tag,
            filesizemin,
            filesizemax,
            license,
            copyright,
            group,
        )
        response = self.session.get(f"{self.api}/search", headers=headers)

        if response.status_code == 200:
            return response.json()

        elif response.status_code == 403:
            description = f"Searching {get_options(group)}not authorized"
            raise AuthorizationError(description, response)

        else:
            description = "Unable to get a result with the given search criteria"
            raise FossologyApiError(description, response)

    def filesearch(
        self,
        filelist: List = [],
        group: str = None,
    ):
        """Search for files from hash sum

        API Endpoint: POST /filesearch

        The response does not generate Python objects yet, the plain JSON data is simply returned.

        :param filelist: the list of files (or containers) hashes to search for (default: [])
        :param group: the group name to choose while performing search (default: None)
        :type filelist: list
        :return: list of items corresponding to the search criteria
        :type group: string
        :rtype: JSON
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        """
        if versiontuple(self.version) <= versiontuple("1.0.16"):
            description = f"Endpoint /filesearch is not supported by your Fossology API version {self.version}"
            raise FossologyUnsupported(description)

        headers = {}
        if group:
            headers["groupName"] = group

        response = self.session.post(
            f"{self.api}/filesearch", headers=headers, json=filelist
        )

        if response.status_code == 200:
            all_files = []
            for hash_file in response.json():
                if hash_file.get("findings"):
                    all_files.append(File.from_json(hash_file))
                else:
                    return "Unable to get a result with the given filesearch criteria"
            return all_files

        elif response.status_code == 403:
            description = f"Searching {get_options(group)}not authorized"
            raise AuthorizationError(description, response)

        else:
            description = "Unable to get a result with the given filesearch criteria"
            raise FossologyApiError(description, response)
