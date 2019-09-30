# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import logging
import requests

from pathlib import Path
from .obj import Agents, User, Folder, Upload, Job
from .exceptions import AuthenticationError, AuthorizationError, FossologyApiError

logger = logging.getLogger(__name__)
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

    def detail_upload(self, upload_id):
        """Get detailled information about an upload

        API Endpoint: GET /uploads/{id}

        :param upload_id: the id for the upload
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

        API Endpoint: POST /uploads

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

        API Endpoint: DELETE /uploads/{id}

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

        API Endpoint: GET /uploads

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

    def move_upload(self, upload, folder):
        """Move an upload to another folder

        API Endpoint: PATCH /uploads/{id}

        :param upload: the Upload() to be copied in another folder
        :type upload: Upload() object
        :param folder: the destination Folder
        :type folder: Folder() object
        """
        headers = {"folderId": str(folder.id)}
        try:
            response = self.session.patch(
                self.api + f"/uploads/{upload.id}", headers=headers
            )
            if response.status_code == 202:
                logger.info(
                    f"Upload {upload.uploadname} has been moved to {folder.name}"
                )
            else:
                description = (
                    f"Unable to move upload {upload.uploadname} to {folder.name}"
                )
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def copy_upload(self, upload, folder):
        """Copy an upload in another folder

        API Endpoint: PUT /uploads/{id}

        :param upload: the Upload() to be copied in another folder
        :type upload: Upload() object
        :param folder: the destination Folder
        :type folder: Folder() object
        """
        headers = {"folderId": str(folder.id)}
        try:
            response = self.session.put(
                self.api + f"/uploads/{upload.id}", headers=headers
            )
            if response.status_code == 202:
                logger.info(
                    f"Upload {upload.uploadname} has been copied to {folder.name}"
                )
            else:
                description = (
                    f"Unable to copy upload {upload.uploadname} to {folder.name}"
                )
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)

    def list_jobs(self, page_size=20, pages=1):
        """Get all available jobs

        API Endpoint: GET /jobs

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
