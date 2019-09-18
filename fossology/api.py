# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import logging
import requests

from pathlib import Path
from .obj import Agents, User, Folder, Upload, Job
from .exceptions import AuthenticationError, AuthorizationError, FossologyApiError

logger = logging.getLogger("fossology")
logger.setLevel(logging.DEBUG)


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

    def __init__(self, url, token, email):
        self.token = token
        self.host = url
        self.api = self.host + "/api/v1"
        self.session = requests.Session()
        self.email = email
        self.user = None
        self.agents = None
        self.auth()
        self.rootFolder = self.detail_folder(self.user.rootFolderId)
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
                for user in response_list:
                    if user["email"] == self.email:
                        self.user = User.from_json(user)
                        if user["agents"]:
                            self.agents = Agents.from_json(user["agents"])
                        logger.info(
                            f"Authenticated as {self.user.name} against {self.host}."
                        )
                        return self.user
                logger.error(f"User with email {self.email} was not found")
                raise AuthenticationError(self.host)
            else:
                if response.status_code == 403:
                    raise AuthenticationError(self.host)
                else:
                    description = f"Unable to establish a session with {self.host}"
                    raise FossologyApiError(description, response)
        except (AuthenticationError, FossologyApiError) as error:
            logger.error(error.message)

    def _list_folders(self):
        """List all folders accessible to the authenticated user

        This method is private and is called only during authentication.
        """
        try:
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
                description = f"Unable to get a list of folders for {self.user.name}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def detail_folder(self, folder_id):
        """Get details of folder.

        :param id: the ID of the folder to be analysed
        :type id: int
        :return: the requested folder - or None if the REST call failed
        :rtype: Folder() object
        """
        try:
            response = self.session.get(self.api + f"/folders/{folder_id}")
            if response.status_code == 200:
                folder = Folder.from_json(response.json())
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
        try:
            response = self.session.post(self.api + "/folders", headers=headers)

            if response.status_code == 200:
                logger.info(f"Folder '{name}' already exists")
                for folder in self.folders:
                    if folder.name == name:
                        return folder
                # FIXME https://github.com/fossology/fossology/issues/1475
                logger.error(f"Can't retrieve folders outside the root folder")
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

    def delete_folder(self, folder_id):
        """Delete a folder

        :param folder_id: the ID of the folder to be deleted
        :type folder_id: int
        """
        try:
            response = self.session.delete(self.api + f"/folders/{folder_id}")
            if response.status_code == 202:
                logger.info(f"Folder {folder_id} has been scheduled for deletion")
            else:
                description = f"Unable to delete folder {folder_id}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def detail_upload(self, upload_id):
        """Get detailled information about an upload

        :param: upload_id
        :type: int
        :return: the upload data - or None if the REST call failed
        :rtype: Upload() object
        """
        try:
            response = self.session.get(self.api + f"/uploads/{upload_id}")
            if response.status_code == 200 and response.json():
                logger.debug(f"Got details for upload {upload_id}")
                return Upload.from_json(response.json())
            else:
                if response.json():
                    description = f"Error while getting details for upload {upload_id}"
                    raise FossologyApiError(description, response)
                else:
                    logger.error(f"Missing response from API: {response.text}")
                    return None
        except FossologyApiError as error:
            logger.error(error.message)
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
        :return: the upload data - or None if the REST call failed
        :rtype: Upload() object

        """
        file_path = Path(path) / upload_file
        files = {"fileInput": (upload_file, open(file_path, "rb"))}
        headers = {"folderId": str(folder.id)}
        if description:
            headers["uploadDescription"] = description
        if access_level:
            headers["public"] = access_level.value

        try:
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
                return upload
            else:
                description = f"Upload of {upload_file} failed"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)
            return None

    def delete_upload(self, upload_id):
        """Delete an upload

        :param upload_id: the ID of the upload to be deleted
        :type upload_id: int
        """
        try:
            response = self.session.delete(self.api + f"/uploads/{upload_id}")
            if response.status_code == 202:
                logger.info(f"Upload {upload_id} has been scheduled for deletion")
            else:
                description = f"Unable to delete upload {upload_id}"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def list_uploads(self):
        """Get all uploads available to the registered user

        :return: a list of uploads - or None if the REST call failed
        :rtype: list()
        """
        try:
            response = self.session.get(self.api + f"/uploads")
            if response.status_code == 200:
                uploads_list = list()
                for upload in response.json():
                    uploads_list.append(Upload.from_json(upload))
                logger.info(f"{len(uploads_list)} uploads are accessible")
                return uploads_list
            else:
                description = f"Unable to retrieve the list of uploads"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)
            return None

    def list_jobs(self, page_size=20, pages=1):
        """Get all available jobs

        The answer is limited to the first page of 20 results by default

        :param page_size: the maximum number of results per page
        :param pages: the number of pages to be retrieved
        :type page_size: int (default to "20")
        :type pages: int (default to "1")
        :return: the jobs data - or None if the REST call failed
        :rtype: list() of Job objects
        """
        headers = {"limit": str(page_size), "pages": str(pages)}
        try:
            response = self.session.get(self.api + "/jobs", headers=headers)
            if response.status_code == 200:
                jobs_list = list()
                for job in response.json():
                    jobs_list.append(Job.from_json(job))
                return jobs_list
            else:
                description = "Getting the list of jobs failed"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)
            return None
