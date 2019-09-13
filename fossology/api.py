# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import sys
import logging
import requests

from pathlib import Path
from .obj import Agents, User, Folder, Upload
from .exceptions import AuthenticationError

logger = logging.getLogger("fossology")
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)


class Fossology:

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

    def __init__(self, url, token):
        self.token = token
        self.host = url
        self.api = self.host + "/api/v1"
        self.session = requests.Session()
        self.auth()
        self.rootFolder = self.detail_folder(self.user.rootFolderId, 0)
        self.folders = list()
        self._list_folders()
        logger.debug(self.user)
        logger.debug(self.rootFolder)

    def auth(self):
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

        try:
            response = self.session.get(self.api + "/users")
            if response.status_code == 200:
                response_list = response.json()
                if response_list[0]["agents"]:
                    agents_obj = Agents.from_json(response_list[0]["agents"])
                    response_list[0]["agents"] = agents_obj
                self.user = User.from_json(response_list[0])
                logger.info(f"Authenticated as {self.user.name} against {self.host}.")
                return self.user
            else:
                if response.status_code == 403:
                    raise AuthenticationError(self.host)
                else:
                    sys.exit(
                        f"Unable to establish a session with {self.host} "
                        f"{response.text} (Status code: {response.status_code})"
                    )
        except AuthenticationError as error:
            sys.exit(error.message)

    def _list_folders(self):
        """List all folders accessible to the authenticated user

        This method is private and is called only during authentication.
        """
        response = self.session.get(self.api + "/folders")
        if response.status_code == 200:
            response_list = response.json()
            for folder in response_list:
                root_sub_folder = Folder.from_json(folder)
                root_sub_folder.parent = self.rootFolder.id
                self.folders.append(root_sub_folder)
            logger.debug(
                f"{len(self.folders)} folders are accessible to {self.user.name}."
            )
        else:
            logger.error(
                f"Unable to get a list of folders for {self.user.name} {response.text} "
                f"(Status code: {response.status_code})"
            )

    def detail_folder(self, folder_id, parent):
        """Get details of folder.

        :param id: the ID of the folder to be analysed
        :type id: int
        :return: the requested folder - or None if the REST call failed
        :rtype: Folder() object
        """
        response = self.session.get(self.api + f"/folders/{folder_id}")
        logger.debug(f"Getting detail for folder: {response.json()}")
        if response.status_code == 200:
            folder = Folder.from_json(response.json())
            # FIXME folder detail API call doesn't deliver parent id
            folder.parent = parent
            return folder
        else:
            logger.error(
                f"Error while getting details for folder {folder_id}: {response.text} "
                f"(Status code: {response.status_code})"
            )
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
        :return: the folder newly created (or already existing) - or None
        :rtype: Folder() object
        """
        headers = {
            "parentFolder": f"{parent}",
            "folderName": f"{name}",
            "folderDescription": f"{description}",
        }
        response = self.session.post(self.api + "/folders", headers=headers)

        if response.status_code == 200:
            logger.info(f"Folder '{name}' already exists")
            for folder in self.folders:
                if folder.name == name:
                    return folder
            # FIXME there is no mean to get a list of subfolders outside the top folder
            return Folder(response.json()["message"], name, description, parent)
        elif response.status_code == 201:
            new_folder = Folder(response.json()["message"], name, description, parent)
            logger.info(f"{new_folder} has been created ({response.json()}")
            return new_folder
        elif response.status_code == 403:
            logger.error(
                f"Folder creation is not authorized, "
                f"verify the scope of your token (needs to be R/W)"
            )
            return None
        else:
            logger.error(
                f"Unable to create folder {name} under {parent}: {response.text} "
                f"(Status Code: {response.status_code})"
            )
            return None

    def update_folder(self, folder, name=None, description=None):
        """Update a folder's name or description

        The name of the new folder must be unique under the same parent.

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

        if name and description:
            headers = {"name": f"{name}", "description": f"{description}"}
            logger.debug(f"Update name and description of folder {folder.id}")
        else:
            if name:
                headers = {"name": f"{name}"}
                logger.debug(f"Update name of folder {folder.id}")
            if description:
                headers = {"description": f"{description}"}
                logger.debug(f"Update description of folder {folder.id}")

        folders_api_path = self.api + f"/folders/{folder.id}"
        response = self.session.patch(folders_api_path, headers=headers)
        if response.status_code == 200:
            logger.info(f"{folder} has been updated")
            return self.detail_folder(folder.id, folder.parent)
        else:
            logger.error(
                f"Unable to update folder {folder}: {response.text} "
                f"(Status code: {response.status_code})"
            )
            return None

    def delete_folder(self, folder_id):
        """Delete a folder

        :param folder_id: the ID of the folder to be deleted
        :type folder_id: int
        """
        response = self.session.delete(self.api + f"/folders/{folder_id}")
        if response.status_code == 202:
            logger.info(f"Folder {folder_id} has been scheduled for deletion")
        else:
            logger.error(
                f"Unable to delete folder {id}: {response.text} "
                f"(Status code: {response.status_code})"
            )

    def detail_upload(self, upload_id):
        """Get detailled information about an upload

        :param: upload_id
        :type: int
        """
        response = self.session.get(self.api + f"/uploads/{upload_id}")
        if response.status_code == 200:
            logger.debug(response.json())
            return Upload.from_json(response.json())
        else:
            logger.error(
                f"Error while getting details for upload {upload_id} "
                f"{response.text} (Status code: {response.status_code}"
            )
            return None

    def upload_file(
        self, upload_file, path, folder, description=None, access_level=None
    ):
        """Upload a file to FOSSology

        :upload_file: the name of the file to be uploaded
        :path: the path of the file on the file system
        :folder: the folder where the file is updated
        :type upload_file: string
        :type path: string
        :type folder: Folder
        """
        file_path = Path(path) / upload_file
        files = {"fileInput": (upload_file, open(file_path, "rb"))}
        print(files)
        headers = {"folderId": str(folder.id)}
        if description:
            headers["uploadDescription"] = description
        if access_level:
            headers["public"] = access_level.value

        response = self.session.post(
            self.api + "/uploads", files=files, headers=headers
        )
        if response.status_code == 201:
            upload_id = response.json()["message"]
            upload = self.detail_upload(upload_id)
            logger.info(
                f"Upload {upload.uploadname} ({upload.filesize}) "
                f"has been uploaded on {upload.uploaddate}"
            )
        else:
            logger.error(
                f"Upload of {upload_file} failed: {response.text} "
                f"(Status code: {response.status_code})"
            )

    def delete_upload(self, upload_id):
        """Delete an upload

        :param upload_id: the ID of the upload to be deleted
        :type upload_id: int
        """
        response = self.session.delete(self.api + f"/uploads/{upload_id}")
        if response.status_code == 202:
            logger.info(f"Upload {upload_id} has been scheduled for deletion")
        else:
            logger.error(
                f"Unable to delete upload {upload_id} : {response.text}"
                f"(Status code: {response.status_code})"
            )
