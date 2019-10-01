# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging

from .obj import Folder
from .exceptions import AuthorizationError, FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Folders:
    """Class dedicated to all "folders" related endpoints"""

    def list_folders(self):
        """List all folders accessible to the authenticated user

        API Endpoint: GET /folders

        :return: a list of folders - or None if the REST call failed
        :rtype: list()
        """
        try:
            response = self.session.get(self.api + "/folders")
            if response.status_code == 200:
                folders_list = list()
                response_list = response.json()
                for folder in response_list:
                    sub_folder = Folder.from_json(folder)
                    sub_folder.parent = self.rootFolder.id
                    folders_list.append(sub_folder)
                logger.debug(
                    f"{len(folders_list)} folders are accessible to {self.user.name}."
                )
                return folders_list
            else:
                description = f"Unable to get a list of folders for {self.user.name}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def detail_folder(self, folder_id):
        """Get details of folder.

        API Endpoint: GET /folders/{id}

        :param id: the ID of the folder to be analysed
        :type id: int
        :return: the requested folder - or None if the REST call failed
        :rtype: Folder() object
        """
        try:
            response = self.session.get(self.api + f"/folders/{folder_id}")
            if response.status_code == 200:
                for folder in self.folders:
                    if folder.id == folder_id:
                        return folder
                folder = Folder.from_json(response.json())
                logger.debug(f"Adding folder {folder} in the list of user's folders")
                self.folders.append(folder)
                return folder
            else:
                description = f"Error while getting details for folder {folder_id}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)
            return None

    def create_folder(self, parent, name, description=None):
        """Create a new (sub)folder

        The name of the new folder must be unique under the same parent.

        API Endpoint: POST /folders/{id}

        :param parent: the parent folder
        :param name: the name of the folder
        :param description: a meaningful description for the folder (optional)
        :type parent: Folder() object
        :type name: str
        :type description: str
        :return: the folder newly created (or already existing) - or None
        :rtype: Folder() object
        """
        headers = {
            "parentFolder": f"{parent.id}",
            "folderName": f"{name}",
            "folderDescription": f"{description}",
        }
        try:
            response = self.session.post(self.api + "/folders", headers=headers)

            if response.status_code == 200:
                logger.info(f"Folder '{name}' already exists")
                for folder in self.folders:
                    if folder.name == name:
                        return folder
                logger.error(
                    f"Folder exists but was not found in the user's folder list"
                )
                return None

            elif response.status_code == 201:
                logger.info(f"Folder {name} has been created")
                return self.detail_folder(response.json()["message"])

            elif response.status_code == 403:
                description = f"Folder creation in parent {parent} not authorized"
                raise AuthorizationError(description, response)
            else:
                description = f"Unable to create folder {name} under {parent}"
                raise FossologyApiError(description, response)

        except (AuthorizationError, FossologyApiError) as error:
            logger.error(error.message)

    def update_folder(self, folder, name=None, description=None):
        """Update a folder's name or description

        The name of the new folder must be unique under the same parent.

        API Endpoint: PATCH /folders/{id}

        :param name: the new name of the folder (optional)
        :param description: the new description for the folder (optional)
        :type name: str
        :type description: str
        :return: the updated folder - or None if the REST call failed
        :rtype: Folder() object
        """
        if not isinstance(folder, Folder):
            logger.error("You need to pass the Folder() object to call this method.")
            return None

        headers = dict()
        if name:
            headers["name"] = name
        if description:
            headers["description"] = description
        folders_api_path = self.api + f"/folders/{folder.id}"

        try:
            response = self.session.patch(folders_api_path, headers=headers)
            if response.status_code == 200:
                logger.info(f"{folder} has been updated")
                return self.detail_folder(folder.id)
            else:
                description = f"Unable to update folder {folder}"
                raise FossologyApiError(description, response)

        except FossologyApiError as error:
            logger.error(error.message)
            return None

    def delete_folder(self, folder):
        """Delete a folder

        API Endpoint: DELETE /folders/{id}

        :param folder: the Folder to be deleted
        :type folder: Folder() object
        """
        try:
            response = self.session.delete(self.api + f"/folders/{folder.id}")
            if response.status_code == 202:
                logger.info(f"Folder {folder.id} has been scheduled for deletion")
            else:
                description = f"Unable to delete folder {folder.id}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def _put_folder(self, action, folder, parent):
        """Copy or move a folder

        Internal function meant to be called by move_folder() or copy_folder()

        API Endpoint: PUT /folders/{id}

        FIXME: the endpoint doesn't work in the API version 1.0.3

        :param action: "move" or "copy"
        :param action: string
        :param folder: the Folder to be moved or copied
        :type folder: Folder() object
        :param parent: the new parent folder
        :type parent: Folder() object
        """
        headers = {"parent": str(parent.id), "action": action}
        try:
            response = self.session.put(
                self.api + f"/folders/{folder.id}", headers=headers
            )
            if response.status_code == 202:
                logger.info(
                    f"Folder {folder.name} has been {action}ed to {parent.name}"
                )
            else:
                description = (
                    f"Unable to {action} folder {folder.name} to {parent.name}"
                )
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def copy_folder(self, folder, parent):
        """Copy a folder

        :param folder: the Folder to be copied
        :type folder: Folder() object
        :param parent: the new parent folder
        :type parent: Folder() object
        """
        self._put_folder("copy", folder, parent)

    def move_folder(self, folder, parent):
        """Move a folder

        :param folder: the Folder to be moved
        :type folder: Folder() object
        :param parent: the new parent folder
        :type parent: Folder() object
        """
        self._put_folder("move", folder, parent)
