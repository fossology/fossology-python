# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import requests
import json

from .obj import Agents, User, Folder


class Fossology:

    """Main FOSSology API class

    Authentication against a running FOSSology instance is performed using an API token.

    :Example:

    >>> from fossology.api import Fossology 
    >>> foss = Fossology(FOSS_URL, FOSS_TOKEN)

    .. note: The class instantiation exits if the session with the Fossology server can't be established

    :param url: URL of the FOSSology instance
    :type url: str
    :param token: The API token generated using the FOSSology UI
    :type token: str
    """
    def __init__(self, url, token):
        self.token = token
        self.host = url
        self.api = self.host + "/api/v1"
        self.auth()
        print(self.user)

    def auth(self):
        self.auth_header = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(self.api + "/users", headers=self.auth_header)
        if response.status_code == 200:
            response_list = response.json()
            if response_list[0]["agents"]:
                agents_obj = Agents.from_json(response_list[0]["agents"])
                response_list[0]["agents"] = agents_obj
            self.user = User.from_json(response_list[0])
            print(f"Authenticated as {self.user.name} against {self.api}.")
            return self.user
        else:
            exit(f"Unable to establish a sessions with {self.host} (Status code: {response.status_code})")

    def list_folders(self):
        """List all (sub)folder accessible to the authenticated user

        :return: the list of user's folders - or None if the REST call failed
        :rtype: list of Folder() objects
        """
        self.folders = list()
        response = requests.get(self.api + "/folders", headers=self.auth_header)
        if response.status_code == 200:
            response_list = response.json()
            for folder in response_list:
                self.folders.append(Folder.from_json(folder))
            print(f"{len(self.folders)} folders are accessible to {self.user.name}.")
            return self.folders
        else:
            print(f"Unable to get a list of folders from {self.host} (Status code: {response.status_code})")
            return None

    def detail_folder(self, folder_id):
        """Get details of folder.

        :param id: the ID of the folder to be analysed
        :type id: int
        :return: the requested folder - or None if the REST call failed
        :rtype: Folder() object
        """
        response = requests.get(self.api + f"/folders/{folder_id}", headers=self.auth_header)
        if response.status_code == 200:
            folder = Folder.from_json(response.json())
            return folder
        else:
            print(f"Error while getting details for folder {folder_id}")
            return None

    def create_folder(self, parent, name, description=None):
        """Create a new (sub)folder

        The name of the new folder must be unique under the same parent.

        :param parent: the ID of the parent folder
        :param name: the name of the folder
        :param description: a meaningful description for the folder (optional)
        :type parent: int
        :type name: str
        :type description: str
        :return: the folder newly created (or already existing) - or None if the REST call failed
        :rtype: Folder() object
        """
        if not self.folders:
            self.list_folders()

        headers = self.auth_header
        headers.update({"parentFolder": f"{parent}", "folderName": f"{name}", "folderDescription": f"{description}"})
        response = requests.post(self.api + "/folders", headers=headers)
        if response.status_code == 200:
            returned_folder = response.json()
            for folder in self.folders:
                if folder.name == name:
                    print(f"{folder} already exists!")
                    return folder

        if response.status_code == 201:
            response_list = response.json()
            for folder in response_list:
                new_folder = Folder.from_json(folder)
                self.folders.append(new_folder)
            print(f"{new_folder} has been created.")
            return new_folder
        else:
            print(f"Unable to create folder {name} under {parent} (Status code: {response.status_code})")
            return None
