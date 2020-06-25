# Copyright 2020 Siemens AG
# SPDX-License-Identifier: MIT

import json
import time
import logging
from tenacity import retry, retry_if_exception_type, stop_after_attempt, TryAgain

from .obj import Upload, Summary
from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Uploads:
    """Class dedicated to all "uploads" related endpoints"""

    # Retry until the unpack agent is finished
    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(10))
    def detail_upload(self, upload_id):
        """Get detailled information about an upload

        API Endpoint: GET /uploads/{id}

        :param upload_id: the id of the upload
        :type: int
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/uploads/{upload_id}")
        if response.status_code == 200:
            logger.debug(f"Got details for upload {upload_id}")
            return Upload.from_json(response.json())
        elif response.status_code == 503:
            logger.debug(
                f"Unpack agent for {upload_id} didn't start yet, is the scheduler running?"
            )
            time.sleep(20)
            raise TryAgain
        else:
            description = f"Error while getting details for upload {upload_id}"
            raise FossologyApiError(description, response)

    def upload_file(  # noqa: C901
        self,
        folder,
        file=None,
        vcs=None,
        url=None,
        description=None,
        access_level=None,
        ignore_scm=False,
        group=None,
    ):
        """Upload a file to FOSSology

        API Endpoint: POST /uploads

        :Example for a file upload:

        >>> from fossology import Fossology
        >>> from fossology.obj import AccessLevel
        >>> foss = Fossology(FOSS_URL, FOSS_TOKEN, username)
        >>> my_upload = foss.upload_file(
                foss.rootFolder,
                file="my-package.zip",
                description="My product package",
                access_level=AccessLevel.PUBLIC,
            )

        :Example for a VCS upload:

        >>> vcs = {
                "vcsType": "git",
                "vcsUrl": "https://github.com/fossology/fossology-python",
                "vcsName": "fossology-python-github-master",
                "vcsUsername": "",
                "vcsPassword": "",
            }
        >>> vcs_upload = foss.upload_file(
                foss.rootFolder,
                vcs=vcs,
                description="Upload from VCS",
                access_level=AccessLevel.PUBLIC,
            )

        :Example for a URL upload:

        >>> url = {
                "url": "https://github.com/fossology/fossology-python/archive/master.zip",
                "name": "fossology-python-master.zip",
                "accept": "zip",
                "reject": "",
                "maxRecursionDepth": "1",
            }
        >>> url_upload = foss.upload_file(
                foss.rootFolder,
                url=url,
                description="Upload from URL",
                access_level=AccessLevel.PUBLIC,
            )

        :param folder: the upload Fossology folder
        :param file: the local path of the file to be uploaded
        :param vcs: the VCS specification to upload from an online repository
        :param url: the URL specification to upload from a url
        :param description: description of the upload (default: None)
        :param access_level: access permissions of the upload (default: protected)
        :param ignore_scm: ignore SCM files (Git, SVN, TFS) (default: False)
        :param group: the group name to chose while uploading the file (default: None)
        :type folder: Folder
        :type file: string
        :type vcs: dict()
        :type url: dict()
        :type description: string
        :type access_level: AccessLevel
        :type ignore_scm: boolean
        :type group: string
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"folderId": str(folder.id)}
        if description:
            headers["uploadDescription"] = description
        if access_level:
            headers["public"] = access_level.value
        if ignore_scm:
            headers["ignoreScm"] = "true"
        if group:
            headers["groupName"] = group

        if file:
            headers["uploadType"] = "server"
            with open(file, "rb") as fp:
                files = {"fileInput": fp}
                response = self.session.post(
                    f"{self.api}/uploads", files=files, headers=headers
                )
        elif vcs:
            headers["uploadType"] = "vcs"
            data = json.dumps(vcs)
            headers["Content-Type"] = "application/json"
            response = self.session.post(
                f"{self.api}/uploads", data=data, headers=headers
            )
        elif url:
            headers["uploadType"] = "url"
            data = json.dumps(url)
            headers["Content-Type"] = "application/json"
            response = self.session.post(
                f"{self.api}/uploads", data=data, headers=headers
            )
        else:
            logger.debug("Neither VCS or File option given, not uploading anything")
            return

        if response.status_code == 201:
            try:
                upload = self.detail_upload(response.json()["message"])
                logger.info(
                    f"Upload {upload.uploadname} ({upload.filesize}) "
                    f"has been uploaded on {upload.uploaddate}"
                )
                return upload
            except TryAgain:
                if file:
                    source = f"{file}"
                elif vcs:
                    source = vcs.get("vcsName")
                else:
                    source = url.get("name")
                description = f"Upload of {source} failed"
                raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def upload_summary(self, upload):
        """Get clearing information about an upload

        API Endpoint: GET /uploads/{id}/summary

        :param upload: the upload to gather data from
        :type: Upload
        :return: the upload summary data
        :rtype: Summary
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/uploads/{upload.id}/summary")
        if response.status_code == 200:
            return Summary.from_json(response.json())
        elif response.status_code == 503:
            logger.debug(
                f"Unpack agent for {upload.uploadname} (id={upload.id}) didn't start yet"
            )
            time.sleep(3)
            raise TryAgain
        else:
            description = f"No summary for upload {upload.uploadname} (id={upload.id})"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def upload_licenses(self, upload, agent=None, containers=False):
        """Get clearing information about an upload

        API Endpoint: GET /uploads/{id}/licenses

        :param upload: the upload to gather data from
        :param agent: the license agent to use (default: LicenseAgent.MONK)
        :param containers: wether to show containers or not (default: False)
        :type upload: Upload
        :type agent: LicenseAgent
        :type containers: boolean
        :return: the licenses found by the specified agent
        :rtype: list of licenses as JSON object
        :raises FossologyApiError: if the REST call failed
        """
        if agent:
            agent = agent.value
        else:
            agent = "nomos"
        if containers:
            containers = "true"
            response = self.session.get(
                f"{self.api}/uploads/{upload.id}/licenses?agent={agent}&containers={containers}"
            )
        else:
            response = self.session.get(
                f"{self.api}/uploads/{upload.id}/licenses?agent={agent}"
            )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 412:
            logger.info(
                f"Agent {agent} has not been scheduled for {upload.uploadname} (id={upload.id}): "
                f"{response.json()['message']}"
            )
            return
        elif response.status_code == 503:
            logger.debug(
                f"Unpack agent for {upload.uploadname} (id={upload.id}) didn't start yet"
            )
            time.sleep(3)
            raise TryAgain
        else:
            description = f"No licenses for upload {upload.uploadname} (id={upload.id})"
            raise FossologyApiError(description, response)

    def delete_upload(self, upload, group=None):
        """Delete an upload

        API Endpoint: DELETE /uploads/{id}

        :param upload: the upload to be deleted
        :param group: the group name to chose while deleting the upload (default None)
        :type upload: Upload
        :type group: string
        :raises FossologyApiError: if the REST call failed
        """
        headers = {}
        if group:
            headers["groupName"] = group
        response = self.session.delete(
            f"{self.api}/uploads/{upload.id}", headers=headers
        )
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
        response = self.session.get(f"{self.api}/uploads")
        if response.status_code == 200:
            uploads_list = list()
            for upload in response.json():
                uploads_list.append(Upload.from_json(upload))
            return uploads_list
        else:
            description = "Unable to retrieve the list of uploads"
            raise FossologyApiError(description, response)

    def move_upload(self, upload, folder, group=None):
        """Move an upload to another folder

        API Endpoint: PATCH /uploads/{id}

        :param upload: the Upload to be copied in another folder
        :param folder: the destination Folder
        :param group: the group name to chose while deleting the upload (default None)
        :type upload: Upload
        :type folder: Folder
        :type group: string
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"folderId": str(folder.id)}
        if group:
            headers["groupName"] = group
        response = self.session.patch(
            f"{self.api}/uploads/{upload.id}", headers=headers
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
        :param folder: the destination Folder
        :type upload: Upload
        :type folder: Folder
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"folderId": str(folder.id)}
        response = self.session.put(f"{self.api}/uploads/{upload.id}", headers=headers)
        if response.status_code == 202:
            logger.info(f"Upload {upload.uploadname} has been copied to {folder.name}")
        else:
            description = f"Unable to copy upload {upload.uploadname} to {folder.name}"
            raise FossologyApiError(description, response)
