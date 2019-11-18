# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import json
import time
import logging

from .obj import Upload
from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Uploads:
    """Class dedicated to all "uploads" related endpoints"""

    def detail_upload(self, upload_id):
        """Get detailled information about an upload

        API Endpoint: GET /uploads/{id}

        :param upload_id: the id of the upload
        :type: int
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        """
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

    def upload_file(
        self, folder, file=None, vcs=None, description=None, access_level=None
    ):
        """Upload a file to FOSSology

        API Endpoint: POST /uploads

        :param folder: the upload Fossology folder
        :param file: the local path of the file to be uploaded
        :param vcs: the VCS specification to upload from an online repository
        :param access_level: access permissions of the upload (default: protected)
        :type folder: Folder
        :type file: string
        :type vcs: dict()
        :type description: string
        :type access_level: AccessLevel
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"folderId": str(folder.id)}
        if file:
            fp = open(file, "rb")
            files = {"fileInput": fp}
        if vcs:
            data = json.dumps(vcs)
            headers["Content-Type"] = "application/json"
        if description:
            headers["uploadDescription"] = description
        if access_level:
            headers["public"] = access_level.value

        if file:
            response = self.session.post(
                self.api + "/uploads", files=files, headers=headers
            )
            fp.close()
        if vcs:
            response = self.session.post(
                self.api + "/uploads", data=data, headers=headers
            )
        if response.status_code == 201:
            upload_id = response.json()["message"]
            time.sleep(3)
            upload = self.detail_upload(upload_id)
            logger.info(
                f"Upload {upload.uploadname} ({upload.filesize}) "
                f"has been uploaded on {upload.uploaddate}"
            )
            return upload
        else:
            source = f"{file}" if file else f"{vcs['vcsUrl']}"
            description = f"Upload of {source} failed"
            raise FossologyApiError(description, response)

    def delete_upload(self, upload):
        """Delete an upload

        API Endpoint: DELETE /uploads/{id}

        :param upload: the upload to be deleted
        :type upload: Upload
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.delete(self.api + f"/uploads/{upload.id}")
        if response.status_code == 202:
            logger.info(f"Upload {upload.id} has been scheduled for deletion")
        else:
            description = f"Unable to delete upload {upload.id}"
            raise FossologyApiError(description, response)

    def list_uploads(self):
        """Get all uploads available to the registered user

        API Endpoint: GET /uploads

        :return: a list of uploads
        :rtype: list of Upload
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(self.api + f"/uploads")
        if response.status_code == 200:
            uploads_list = list()
            for upload in response.json():
                uploads_list.append(Upload.from_json(upload))
            return uploads_list
        else:
            description = f"Unable to retrieve the list of uploads"
            raise FossologyApiError(description, response)

    def move_upload(self, upload, folder):
        """Move an upload to another folder

        API Endpoint: PATCH /uploads/{id}

        :param upload: the Upload to be copied in another folder
        :type upload: Upload
        :param folder: the destination Folder
        :type folder: Folder
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"folderId": str(folder.id)}
        response = self.session.patch(
            self.api + f"/uploads/{upload.id}", headers=headers
        )
        if response.status_code == 202:
            logger.info(f"Upload {upload.uploadname} has been moved to {folder.name}")
        else:
            description = f"Unable to move upload {upload.uploadname} to {folder.name}"
            raise FossologyApiError(description, response)

    def copy_upload(self, upload, folder):
        """Copy an upload in another folder

        API Endpoint: PUT /uploads/{id}

        :param upload: the Upload to be copied in another folder
        :type upload: Upload
        :param folder: the destination Folder
        :type folder: Folder
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"folderId": str(folder.id)}
        response = self.session.put(self.api + f"/uploads/{upload.id}", headers=headers)
        if response.status_code == 202:
            logger.info(f"Upload {upload.uploadname} has been copied to {folder.name}")
        else:
            description = f"Unable to copy upload {upload.uploadname} to {folder.name}"
            raise FossologyApiError(description, response)
