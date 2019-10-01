# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging

from pathlib import Path
from .obj import Upload, Job
from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Uploads:
    """Class dedicated to all "uploads" related endpoints"""

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
