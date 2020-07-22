# Copyright 2020 Siemens AG
# SPDX-License-Identifier: MIT

import json
import time
import logging

from tenacity import retry, retry_if_exception_type, stop_after_attempt, TryAgain
from fossology.obj import Upload, Summary, Licenses, get_options
from fossology.exceptions import AuthorizationError, FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Uploads:
    """Class dedicated to all "uploads" related endpoints"""

    # Retry until the unpack agent is finished
    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(10))
    def detail_upload(self, upload_id, wait_time=0):
        """Get detailled information about an upload

        API Endpoint: GET /uploads/{id}

        Get information about a given upload. If the upload is not ready wait another ``wait_time`` seconds or look at
        the ``Retry-After`` to determine how long the wait period shall be.

        If ``wait_time`` is 0, the time interval specified by the ``Retry-After`` header is used.

        The function stops trying after **10 attempts**.

        :Examples:

        >>> # Wait up to 20 minutes until the upload is ready
        >>> long_upload = detail_upload(1, 120)

        >>> # Wait up to 5 minutes until the upload is ready
        >>> long_upload = detail_upload(1, 30)

        :param upload_id: the id of the upload
        :param wait_time: use a customized upload wait time instead of Retry-After (in seconds, default: 0)
        :type upload_id: int
        :type wait_time: int
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/uploads/{upload_id}")
        if response.status_code == 200:
            logger.debug(f"Got details for upload {upload_id}")
            return Upload.from_json(response.json())
        elif response.status_code == 503:
            if not wait_time:
                wait_time = response.headers["Retry-After"]
            logger.debug(
                f"Retry GET upload {upload_id} after {wait_time} seconds: {response.json()['message']}"
            )
            time.sleep(int(wait_time))
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
        wait_time=0,
    ):
        """Upload a package to FOSSology

        API Endpoint: POST /uploads

        Perform a file, VCS or URL upload and get information about the upload using :func:`~fossology.uploads.Uploads.detail_upload` and passing the ``wait_time`` argument.

        See description of :func:`~fossology.uploads.Uploads.detail_upload` to configure how long the client shall wait for the upload to be ready.

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
        :param ignore_scm: ignore SCM files (Git, SVN, TFS) (default: True)
        :param group: the group name to chose while uploading the file (default: None)
        :param wait_time: use a customized upload wait time instead of Retry-After (in seconds, default: 0)
        :type folder: Folder
        :type file: string
        :type vcs: dict()
        :type url: dict()
        :type description: string
        :type access_level: AccessLevel
        :type ignore_scm: boolean
        :type group: string
        :type wait_time: int
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
            headers["ignoreScm"] = "false"
        if group:
            headers["groupName"] = group

        if file:
            headers["uploadType"] = "server"
            with open(file, "rb") as fp:
                files = {"fileInput": fp}
                response = self.session.post(
                    f"{self.api}/uploads", files=files, headers=headers
                )
        elif vcs or url:
            if vcs:
                headers["uploadType"] = "vcs"
                data = json.dumps(vcs)
            else:
                headers["uploadType"] = "url"
                data = json.dumps(url)
            headers["Content-Type"] = "application/json"
            response = self.session.post(
                f"{self.api}/uploads", data=data, headers=headers
            )
        else:
            logger.debug(
                "Neither VCS, or Url or filename option given, not uploading anything"
            )
            return

        if response.status_code == 201:
            try:
                upload = self.detail_upload(response.json()["message"], wait_time)
                logger.info(
                    f"Upload {upload.uploadname} ({upload.hash.size}) "
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
    def upload_licenses(self, upload, group: str = None, agent=None, containers=False):
        """Get clearing information about an upload

        API Endpoint: GET /uploads/{id}/licenses

        The response does not generate Python objects yet, the plain JSON data is simply returned.

        :param upload: the upload to gather data from
        :param agent: the license agent to use (default: LicenseAgent.MONK)
        :param containers: wether to show containers or not (default: False)
        :type upload: Upload
        :type agent: LicenseAgent
        :type containers: boolean
        :type group: string
        :return: the list of licenses findings for the specified agent
        :rtype: list of Licenses
        :raises FossologyApiError: if the REST call failed
        """
        headers = {}
        params = {}
        if agent:
            params["agent"] = agent.value
        else:
            params["agent"] = "nomos"
        if containers:
            params["containers"] = "true"
        if group:
            headers["groupName"] = group

        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/licenses", params=params, headers=headers
        )

        if response.status_code == 200:
            all_licenses = []
            scanned_files = response.json()
            for file_with_findings in scanned_files:
                file_licenses = Licenses.from_json(file_with_findings)
                all_licenses.append(file_licenses)
            return all_licenses

        elif response.status_code == 403:
            description = f"Getting license for upload {upload.id} {get_options(group)}not authorized"
            raise AuthorizationError(description, response)

        elif response.status_code == 412:
            description = f"Unable to get licenses from {agent} for {upload.uploadname} (id={upload.id})"
            raise FossologyApiError(description, response)

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
        :param group: the group name to chose while deleting the upload (default: None)
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

    def list_uploads(self, folder=None, group=None, recursive=True, page=1):
        """Get all uploads available to the registered user

        API Endpoint: GET /uploads

        :param folder: only list uploads from the given folder
        :param group: list uploads from a specific group (not only your own uploads)
        :param recursive: wether to list uploads from children folders or not (default: True)
        :param page: the number of the page to fetch uploads from (default: 1)
        :type folder: Folder
        :type group: string
        :type recursive: boolean
        :type page: int
        :return: a list of uploads
        :rtype: list of Upload
        :raises FossologyApiError: if the REST call failed
        """
        headers = {}
        if group:
            headers["groupName"] = group

        url = f"{self.api}/uploads"
        params = {}
        if page != 1:
            params["page"] = page
        if folder:
            params["folderId"] = folder.id
        if not recursive:
            params["recursive"] = "false"

        response = self.session.get(url, params=params)
        if response.status_code == 200:
            uploads_list = list()
            for upload in response.json():
                uploads_list.append(Upload.from_json(upload))
            logger.info(
                f"Retrieved page {page} of uploads, {response.headers.get('X-TOTAL-PAGES', 'Unknown')} pages are in total available"
            )
            return uploads_list
        else:
            description = "Unable to retrieve the list of uploads"
            raise FossologyApiError(description, response)

    def move_upload(self, upload, folder, group=None):
        """Move an upload to another folder

        API Endpoint: PATCH /uploads/{id}

        :param upload: the Upload to be copied in another folder
        :param folder: the destination Folder
        :param group: the group name to chose while deleting the upload (default: None)
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
