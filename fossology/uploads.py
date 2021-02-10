# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import json
import logging
import time

from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt

from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Licenses, Summary, Upload, get_options

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Uploads:
    """Class dedicated to all "uploads" related endpoints"""

    # Retry until the unpack agent is finished
    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(10))
    def detail_upload(
        self, upload_id: int, group: str = None, wait_time: int = 0
    ) -> Upload:
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
        :param group: the group the upload shall belong to
        :param wait_time: use a customized upload wait time instead of Retry-After (in seconds, default: 0)
        :type upload_id: int
        :type group: string
        :type wait_time: int
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        """
        headers = {}
        if group:
            headers["groupName"] = group
        response = self.session.get(f"{self.api}/uploads/{upload_id}", headers=headers)

        if response.status_code == 200:
            logger.debug(f"Got details for upload {upload_id}")
            return Upload.from_json(response.json())

        elif response.status_code == 403:
            description = f"Getting details for upload {upload_id} {get_options(group)}not authorized"
            raise AuthorizationError(description, response)

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
        server=None,
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

        :Example for a SERVER upload:

        >>> server = {
                "path": "/tmp/fossology-python",
                "name": "fossology-python",
            }
        >>> server_upload = foss.upload_file(
                foss.rootFolder,
                server=server,
                description="Upload from SERVER",
                access_level=AccessLevel.PUBLIC,
            )


        :param folder: the upload Fossology folder
        :param file: the local path of the file to be uploaded
        :param vcs: the VCS specification to upload from an online repository
        :param url: the URL specification to upload from a url
        :param server: the SERVER specification to upload from fossology server
        :param description: description of the upload (default: None)
        :param access_level: access permissions of the upload (default: protected)
        :param ignore_scm: ignore SCM files (Git, SVN, TFS) (default: True)
        :param group: the group name to chose while uploading the file (default: None)
        :param wait_time: use a customized upload wait time instead of Retry-After (in seconds, default: 0)
        :type folder: Folder
        :type file: string
        :type vcs: dict()
        :type url: dict()
        :type server: dict()
        :type description: string
        :type access_level: AccessLevel
        :type ignore_scm: boolean
        :type group: string
        :type wait_time: int
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
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
        elif vcs or url or server:
            if vcs:
                headers["uploadType"] = "vcs"
                data = json.dumps(vcs)
            elif url:
                headers["uploadType"] = "url"
                data = json.dumps(url)
            elif server:
                headers["uploadType"] = "server"
                data = json.dumps(server)
            headers["Content-Type"] = "application/json"
            response = self.session.post(
                f"{self.api}/uploads", data=data, headers=headers
            )
        else:
            logger.info(
                "Neither VCS, or Url or filename option given, not uploading anything"
            )
            return

        if file:
            source = f"{file}"
        elif vcs:
            source = vcs.get("vcsName")
        elif url:
            source = url.get("name")
        elif server:
            source = server.get("name")

        if response.status_code == 201:
            try:
                upload = self.detail_upload(response.json()["message"], wait_time)
                if upload.filesize:
                    logger.info(
                        f"Upload {upload.uploadname} ({upload.filesize}) "
                        f"has been uploaded on {upload.uploaddate}"
                    )
                else:
                    logger.info(
                        f"Upload {upload.uploadname} ({upload.hash.size}) "
                        f"has been uploaded on {upload.uploaddate}"
                    )
                return upload
            except TryAgain:
                description = f"Upload of {source} failed"
                raise FossologyApiError(description, response)

        elif response.status_code == 403:
            description = (
                f"Upload of {source} {get_options(group, folder)}not authorized"
            )
            raise AuthorizationError(description, response)

        elif server and response.status_code == 500:
            description = (
                f"Upload {description} could not be performed; "
                f"did you add a prefix for '{server['path']}' in Fossology config "
                f"variable 'Admin->Customize->Whitelist for serverupload'? "
                f"Has fossy user read access to {server['path']}?"
            )
            raise FossologyApiError(description, response)

        else:
            description = f"Upload {description} could not be performed"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def upload_summary(self, upload, group=None):
        """Get clearing information about an upload

        API Endpoint: GET /uploads/{id}/summary

        :param upload: the upload to gather data from
        :param group: the group name to chose while accessing an upload (default: None)
        :type: Upload
        :type group: string
        :return: the upload summary data
        :rtype: Summary
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        """
        headers = {}
        if group:
            headers["groupName"] = group
        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/summary", headers=headers
        )

        if response.status_code == 200:
            return Summary.from_json(response.json())

        elif response.status_code == 403:
            description = f"Getting summary of upload {upload.id} {get_options(group)}not authorized"
            raise AuthorizationError(description, response)

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
        :param agent: the license agents to use (e.g. "nomos,monk,ninka,ojo,reportImport", default: "nomos")
        :param containers: wether to show containers or not (default: False)
        :param group: the group name to chose while accessing the upload (default: None)
        :type upload: Upload
        :type agent: string
        :type containers: boolean
        :type group: string
        :return: the list of licenses findings for the specified agent
        :rtype: list of Licenses
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        """
        headers = {}
        params = {}
        headers = {}
        if group:
            headers["groupName"] = group
        if agent:
            params["agent"] = agent
        else:
            params["agent"] = agent = "nomos"
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
        :raises AuthorizationError: if the user can't access the group
        """
        headers = {}
        if group:
            headers["groupName"] = group
        response = self.session.delete(
            f"{self.api}/uploads/{upload.id}", headers=headers
        )

        if response.status_code == 202:
            logger.info(f"Upload {upload.id} has been scheduled for deletion")

        elif response.status_code == 403:
            description = (
                f"Deleting upload {upload.id} {get_options(group)}not authorized"
            )
            raise AuthorizationError(description, response)

        else:
            description = f"Unable to delete upload {upload.id}"
            raise FossologyApiError(description, response)

    def list_uploads(
        self,
        folder=None,
        group=None,
        recursive=True,
        page_size=100,
        page=1,
        all_pages=False,
    ):
        """Get all uploads available to the registered user

        API Endpoint: GET /uploads

        :param folder: only list uploads from the given folder
        :param group: list uploads from a specific group (not only your own uploads) (default: None)
        :param recursive: wether to list uploads from children folders or not (default: True)
        :param page_size: limit the number of uploads per page (default: 100)
        :param page: the number of the page to fetch uploads from (default: 1)
        :param all_pages: get all uploads (default: False)
        :type folder: Folder
        :type group: string
        :type recursive: boolean
        :type page_size: int
        :type page: int
        :type all_pages: boolean
        :return: a tuple containing the list of uploads and the total number of pages
        :rtype: Tuple(list of Upload, int)
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group
        """
        params = {}
        headers = {"limit": str(page_size)}
        if group:
            headers["groupName"] = group
        if folder:
            params["folderId"] = folder.id
        if not recursive:
            params["recursive"] = "false"

        uploads_list = list()
        if all_pages:
            # will be reset after the total number of pages has been retrieved from the API
            x_total_pages = 2
        else:
            x_total_pages = page
        while page <= x_total_pages:
            headers["page"] = str(page)
            response = self.session.get(
                f"{self.api}/uploads", headers=headers, params=params
            )
            if response.status_code == 200:
                for upload in response.json():
                    uploads_list.append(Upload.from_json(upload))
                x_total_pages = int(response.headers.get("X-TOTAL-PAGES", 0))
                if not all_pages or x_total_pages == 0:
                    logger.info(
                        f"Retrieved page {page} of uploads, {x_total_pages} pages are in total available"
                    )
                    return uploads_list, x_total_pages
                page += 1

            elif response.status_code == 403:
                description = f"Retrieving list of uploads {get_options(group, folder)}not authorized"
                raise AuthorizationError(description, response)

            else:
                description = f"Unable to retrieve the list of uploads from page {page}"
                raise FossologyApiError(description, response)
        logger.info(f"Retrieved all {x_total_pages} of uploads")
        return uploads_list, x_total_pages

    def move_upload(self, upload, folder, group=None):
        """Move an upload to another folder

        API Endpoint: PATCH /uploads/{id}

        :param upload: the Upload to be copied in another folder
        :param folder: the destination Folder
        :param group: the group name to chose while changing the upload (default: None)
        :type upload: Upload
        :type folder: Folder
        :type group: string
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the user can't access the group or folder
        """
        headers = {"folderId": str(folder.id)}
        if group:
            headers["groupName"] = group
        response = self.session.patch(
            f"{self.api}/uploads/{upload.id}", headers=headers
        )

        if response.status_code == 202:
            logger.info(f"Upload {upload.uploadname} has been moved to {folder.name}")

        elif response.status_code == 403:
            description = (
                f"Moving upload {upload.id} {get_options(group, folder)}not authorized"
            )
            raise AuthorizationError(description, response)

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

        elif response.status_code == 403:
            description = f"Copy upload {upload.id} {get_options(folder)}not authorized"
            raise AuthorizationError(description, response)

        else:
            description = f"Unable to copy upload {upload.uploadname} to {folder.name}"
            raise FossologyApiError(description, response)
