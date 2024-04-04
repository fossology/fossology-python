# mypy: disable-error-code="attr-defined"
# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT
import json
import logging
import re
import time
from typing import Tuple

import requests
from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt

from fossology.enums import AccessLevel, ClearingStatus
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import (
    Folder,
    Group,
    Permission,
    Summary,
    Upload,
    UploadCopyrights,
    UploadLicenses,
    UploadPermGroups,
    User,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def list_uploads_parameters(
    folder: Folder | None = None,
    recursive: bool = True,
    name: str | None = None,
    status: ClearingStatus | None = None,
    assignee: str | None = None,
    since: str | None = None,
    group: str | None = None,
    limit: str | None = None,
) -> dict:
    """Helper function to list of query parameters for GET /uploads endpoint"""
    date_pattern = re.compile("^[0-9]{4}-[0-9]{2}-[0-9]{2}")
    params = {}
    if folder:
        params["folderId"] = folder.id
    if not recursive:
        params["recursive"] = "false"
    if name:
        params["name"] = name
    if status:
        params["status"] = status.value
    if assignee:
        params["assignee"] = assignee
    if since:
        if not date_pattern.match(since):
            logger.error(
                f"Date format for 'since' query parameter {since} does not match expected format YYYY-MM-DD"
            )
        else:
            params["since"] = since
    if group:
        params["groupName"] = group
    if limit:
        params["limit"] = limit
    return params


class Uploads:
    """Class dedicated to all "uploads" related endpoints"""

    # Retry until the unpack agent is finished
    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(10))
    def detail_upload(
        self, upload_id: int, group: str | None = None, wait_time: int = 0
    ) -> Upload:
        """Get detailed information about an upload

        API Endpoint: GET /uploads/{id}

        Get information about a given upload. If the upload is not ready wait another ``wait_time`` seconds or look at
        the ``Retry-After`` to determine how long the wait period shall be.

        If ``wait_time`` is 0, the time interval specified by the ``Retry-After`` header is used.

        The function stops trying after **10 attempts**.

        :Examples:

        >>> # Wait up to 20 minutes until the upload is ready
        >>> long_upload = detail_upload(1, wait_time=120) # doctest: +SKIP

        >>> # Wait up to 5 minutes until the upload is ready
        >>> long_upload = detail_upload(1, wait_time=30) # doctest: +SKIP

        :param upload_id: the id of the upload
        :param group: the group the upload shall belong to
        :param wait_time: use a customized upload wait time instead of Retry-After (in seconds, default: 0)
        :type upload_id: int
        :type group: string
        :type wait_time: int
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        :raises TryAgain: if the upload times out after 10 retries
        """
        headers = {}
        if group:
            headers["groupName"] = group
        response = self.session.get(f"{self.api}/uploads/{upload_id}", headers=headers)

        if response.status_code == 200:
            logger.debug(f"Got details for upload {upload_id}")
            return Upload.from_json(response.json())

        elif response.status_code == 403:
            description = f"Getting details for upload {upload_id} is not authorized"
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

    def upload_file(
        self,
        folder: Folder,
        file: str | None = None,
        vcs: dict | None = None,
        url: dict | None = None,
        server: dict | None = None,
        description: str | None = None,
        access_level: AccessLevel | None = None,
        apply_global: bool = False,
        ignore_scm: bool = False,
        group: str | None = None,
        wait_time: int = 0,
    ):
        """Upload a package to FOSSology

        API Endpoint: POST /uploads

        Perform a file, VCS or URL upload and get information about the upload using :func:`~fossology.uploads.Uploads.detail_upload` and passing the ``wait_time`` argument.

        See description of :func:`~fossology.uploads.Uploads.detail_upload` to configure how long the client shall wait for the upload to be ready.

        :Example for a file upload:

        >>> from fossology import Fossology
        >>> from fossology.enums import AccessLevel
        >>> foss = Fossology(FOSS_URL, FOSS_TOKEN) # doctest: +SKIP
        >>> my_upload = foss.upload_file(
        ...        foss.rootFolder,
        ...        file="my-package.zip",
        ...        description="My product package",
        ...        access_level=AccessLevel.PUBLIC,
        ...    )  # doctest: +SKIP

        :Example for a VCS upload:

        >>> vcs = {
        ...        "vcsType": "git",
        ...        "vcsUrl": "https://github.com/fossology/fossology-python",
        ...        "vcsName": "fossology-python-github-master",
        ...        "vcsUsername": "",
        ...        "vcsPassword": "",
        ...    }
        >>> vcs_upload = foss.upload_file(
        ...        foss.rootFolder,
        ...        vcs=vcs,
        ...        description="Upload from VCS",
        ...        access_level=AccessLevel.PUBLIC,
        ...    )  # doctest: +SKIP

        :Example for a URL upload:

        >>> url = {
        ...        "url": "https://github.com/fossology/fossology-python/archive/master.zip",
        ...        "name": "fossology-python-master.zip",
        ...        "accept": "zip",
        ...        "reject": "",
        ...        "maxRecursionDepth": "1",
        ...    }
        >>> url_upload = foss.upload_file(
        ...        foss.rootFolder,
        ...        url=url,
        ...        description="Upload from URL",
        ...        access_level=AccessLevel.PUBLIC,
        ...    )  # doctest: +SKIP

        :Example for a SERVER upload:

        >>> server = {
        ...        "path": "/tmp/fossology-python",
        ...        "name": "fossology-python",
        ...    }
        >>> server_upload = foss.upload_file(
        ...        foss.rootFolder,
        ...        server=server,
        ...        description="Upload from SERVER",
        ...        access_level=AccessLevel.PUBLIC,
        ...    )  # doctest: +SKIP


        :param folder: the upload Fossology folder
        :param file: the local path of the file to be uploaded
        :param vcs: the VCS specification to upload from an online repository
        :param url: the URL specification to upload from a url
        :param server: the SERVER specification to upload from fossology server
        :param description: description of the upload (default: None)
        :param access_level: access permissions of the upload (default: protected)
        :param apply_global: apply global decisions for current upload (default: False)
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
        :type apply_global: boolean
        :type ignore_scm: boolean
        :type group: string
        :type wait_time: int
        :return: the upload data
        :rtype: Upload
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        data: dict = {
            "folderId": str(folder.id),
            "uploadDescription": description,
            "public": access_level.value
            if access_level
            else AccessLevel.PROTECTED.value,
            "applyGlobal": apply_global,
            "ignoreScm": ignore_scm,
            "uploadType": "file",
        }

        headers = {}
        if "v1" in self.api:
            headers = {
                k: str(v).lower() if isinstance(v, bool) else v for k, v in data.items()
            }  # Needed for API v1.x
            headers["groupName"] = group
            endpoint = f"{self.api}/uploads"
        else:
            if group:
                endpoint = f"{self.api}/uploads?groupName={group}"
            else:
                endpoint = f"{self.api}/uploads"

        if file:
            data["uploadType"] = headers["uploadType"] = "file"
            with open(file, "rb") as fp:
                files = {"fileInput": fp}
                response = self.session.post(
                    endpoint, files=files, headers=headers, data=data
                )
        elif vcs or url or server:
            if vcs:
                data["location"] = vcs  # type: ignore
                data["uploadType"] = headers["uploadType"] = "vcs"
            elif url:
                data["location"] = url  # type: ignore
                data["uploadType"] = headers["uploadType"] = "url"
            elif server:
                data["location"] = server  # type: ignore
                data["uploadType"] = headers["uploadType"] = "server"
            headers["Content-Type"] = "application/json"
            response = self.session.post(
                endpoint,
                data=json.dumps(data),
                headers=headers,
            )
        else:
            logger.info(
                "Neither VCS, or Url or filename option given, not uploading anything"
            )
            return

        if file:
            source = f"{file}"
        elif vcs:
            source = vcs.get("vcsName")  # type: ignore
        elif url:
            source = url.get("name")  # type: ignore
        elif server:
            source = server.get("name")  # type: ignore

        if response.status_code == 201:
            try:
                upload = self.detail_upload(
                    response.json()["message"], group, wait_time
                )
                logger.info(
                    f"Upload {upload.uploadname} ({upload.hash.size}) "
                    f"has been uploaded on {upload.uploaddate}"
                )
                return upload
            except TryAgain:
                description = f"Upload of {source} failed"
                raise FossologyApiError(description, response)

        elif response.status_code == 403:
            description = f"Upload {description} is not authorized"
            raise AuthorizationError(description, response)

        else:
            description = f"Upload {description} could not be performed"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def upload_summary(self, upload: Upload, group=None):
        """Get clearing information about an upload

        API Endpoint: GET /uploads/{id}/summary

        :param upload: the upload to gather data from
        :param group: the group name to chose while accessing an upload (default: None)
        :type: Upload
        :type group: string
        :return: the upload summary data
        :rtype: Summary
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
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
            description = f"Getting summary of upload {upload.id} is not authorized"
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
    def upload_licenses(
        self,
        upload: Upload,
        group: str | None = None,
        agent: str | None = None,
        containers: bool = False,
        license: bool = True,
        copyright: bool = False,
    ) -> list[UploadLicenses] | None:
        """Get clearing information about an upload

        API Endpoint: GET /uploads/{id}/licenses

        :param upload: the upload to gather data from
        :param group: the group name to chose while accessing the upload (default: None)
        :param agent: the license agents to use (e.g. "nomos,monk,ninka,ojo,reportImport", default: "nomos")
        :param containers: wether to show containers or not (default: False)
        :param license: wether to expose license matches (default: True)
        :param copyright: wether to expose copyright matches (default: False)
        :type upload: Upload
        :type group: string
        :type agent: string
        :type containers: boolean
        :type license: boolean
        :type copyright: boolean
        :return: the list of UploadLicenses for the specified agent
        :rtype: list of UploadLicenses
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        params = {
            "containers": containers,
            "license": license,
            "copyright": copyright,
        }
        if agent:
            params["agent"] = agent  # type: ignore
        else:
            params["agent"] = agent = "nomos"  # type: ignore

        headers = {}
        if group:
            headers["groupName"] = group
            params["groupName"] = group  # type: ignore

        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/licenses", params=params, headers=headers
        )

        if response.status_code == 200:
            all_licenses = []
            scanned_files = response.json()
            for file_with_findings in scanned_files:
                file_licenses = UploadLicenses.from_json(file_with_findings)
                all_licenses.append(file_licenses)
            return all_licenses

        elif response.status_code == 403:
            description = f"Getting licenses for upload {upload.id} is not authorized"
            raise AuthorizationError(description, response)

        elif response.status_code == 412:
            description = f"The agent {agent} has not been scheduled for upload {upload.uploadname} (id={upload.id})"
            raise FossologyApiError(description, response)

        elif response.status_code == 503:
            logger.debug("The ununpack agent or queried agents have not started yet.")
            time.sleep(3)
            raise TryAgain

        else:
            description = f"API error while returning license findings for upload {upload.uploadname} (id={upload.id})"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def upload_copyrights(
        self,
        upload: Upload,
    ):
        """Get copyright matches from an upload

        API Endpoint: GET /uploads/{id}/copyrights

        :param upload: the upload to gather data from
        :type upload: Upload
        :return: the list of copyrights findings
        :rtype: list of Licenses
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        response = self.session.get(f"{self.api}/uploads/{upload.id}/copyrights")

        if response.status_code == 200:
            all_copyrights = []
            for copyright in response.json():
                all_copyrights.append(UploadCopyrights.from_json(copyright))
            return all_copyrights

        elif response.status_code == 403:
            description = f"Getting copyrights for upload {upload.id} is not authorized"
            raise AuthorizationError(description, response)

        elif response.status_code == 412:
            description = f"The agent has not been scheduled for upload {upload.uploadname} (id={upload.id})"
            raise FossologyApiError(description, response)

        elif response.status_code == 503:
            logger.debug("The ununpack agent or queried agents have not started yet.")
            time.sleep(3)
            raise TryAgain

        else:
            description = f"API error while returning copyright findings for upload {upload.uploadname} (id={upload.id})"
            raise FossologyApiError(description, response)

    def delete_upload(self, upload, group=None):
        """Delete an upload

        API Endpoint: DELETE /uploads/{id}

        :param upload: the upload to be deleted
        :param group: the group name to chose while deleting the upload (default: None)
        :type upload: Upload
        :type group: string
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        headers = {}
        if group:
            headers["groupName"] = group
        response = self.session.delete(
            f"{self.api}/uploads/{upload.id}", headers=headers, timeout=5
        )

        if response.status_code == 202:
            logger.info(f"Upload {upload.id} has been scheduled for deletion")

        elif response.status_code == 403:
            description = f"Not authorized to delete upload {upload.id}"
            raise AuthorizationError(description, response)

        else:
            description = f"Unable to delete upload {upload.id}"
            raise FossologyApiError(description, response)

    def list_uploads(
        self,
        folder: Folder | None = None,
        group: str | None = None,
        recursive: bool = True,
        name: str | None = None,
        status: ClearingStatus | None = None,
        assignee: str | None = None,
        since: str | None = None,
        page_size=100,
        page=1,
        all_pages=False,
    ):
        """Get uploads according to filtering criteria (or all available)

        API Endpoint: GET /uploads

        :param folder: only list uploads from the given folder
        :param group: list uploads from a specific group (not only your own uploads) (default: None)
        :param recursive: wether to list uploads from children folders or not (default: True)
        :param name: filter pattern for name and description
        :param status: status of uploads
        :param assignee: user name to which uploads are assigned to or "-me-" or "-unassigned-"
        :param since: uploads since given date in YYYY-MM-DD format
        :param page_size: limit the number of uploads per page (default: 100)
        :param page: the number of the page to fetch uploads from (default: 1)
        :param all_pages: get all uploads (default: False)
        :type folder: Folder
        :type group: string
        :type recursive: boolean
        :type name: str
        :type status: ClearingStatus
        :type assignee: str
        :type since: str
        :type page_size: int
        :type page: int
        :type all_pages: boolean
        :return: a tuple containing the list of uploads and the total number of pages
        :rtype: Tuple(list of Upload, int)
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        headers = {"limit": str(page_size)}
        if group:
            headers["groupName"] = group

        params = list_uploads_parameters(
            folder=folder,
            recursive=recursive,
            name=name,
            status=status,
            assignee=assignee,
            since=since,
            group=group,
            limit=page_size,
        )
        uploads_list = list()
        if all_pages:
            # will be reset after the total number of pages has been retrieved from the API
            x_total_pages = 2
        else:
            x_total_pages = page
        while page <= x_total_pages:
            headers["page"] = str(page)
            params["page"] = str(page)
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
                description = "Retrieving list of uploads is not authorized"
                raise AuthorizationError(description, response)

            else:
                description = f"Unable to retrieve the list of uploads from page {page}"
                raise FossologyApiError(description, response)
        logger.info(f"Retrieved all {x_total_pages} of uploads")
        return uploads_list, x_total_pages

    def update_upload(
        self,
        upload: Upload,
        status: ClearingStatus | None = None,
        comment: str = "",
        assignee: User | None = None,
        group: str | None = None,
    ):
        """Update an upload information

        API Endpoint: PATCH /uploads/{id}

        :param upload: the Upload to be updated
        :param status: the new status of the upload (Open, InProgress, Closed, Rejected)
        :param comment: the comment on the status, required for Closed and Rejected states. Ignored for others. (default: empty)
        :param assignee: the user assigned to the upload (default: None)
        :param group: the group name to chose while changing the upload (default: None)
        :type upload: Upload
        :type status: ClearingStatus
        :type assignee: User
        :type comment: string
        :type group: string
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        params = dict()
        headers = dict()
        if status:
            params["status"] = status.value
        if assignee:
            params["assignee"] = assignee.id  # type: ignore
        if group:
            headers["groupName"] = group
        response = self.session.patch(
            f"{self.api}/uploads/{upload.id}",
            headers=headers,
            params=params,
            data=comment,
        )

        if response.status_code == 202:
            logger.info(f"Upload {upload.uploadname} has been updated")

        elif response.status_code == 403:
            description = f"Updating upload {upload.id} is not authorized"
            raise AuthorizationError(description, response)

        else:
            description = f"Unable to update upload {upload.uploadname}."
            raise FossologyApiError(description, response)

    def move_upload(self, upload: Upload, folder: Folder, action: str):
        """Copy or move an upload by id

        API Endpoint: PUT /uploads/{id}

        :param upload: the Upload to be copied or moved in another folder
        :param folder: the destination Folder
        :param action: the action to be performed, 'copy' or 'move'
        :type upload: Upload
        :type folder: Folder
        :type action: str
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        params = {"folderId": str(folder.id), "action": action}
        response = self.session.put(
            f"{self.api}/uploads/{upload.id}", headers=params, params=params
        )

        if response.status_code == 202:
            logger.info(
                f"Upload {upload.uploadname} has been {action} to {folder.name}"
            )

        elif response.status_code == 403:
            description = f"{action} upload {upload.id} is not authorized"
            raise AuthorizationError(description, response)

        else:
            description = (
                f"Unable to {action} upload {upload.uploadname} to {folder.name}"
            )
            raise FossologyApiError(description, response)

    def download_upload(self, upload: Upload) -> Tuple[str, str]:
        """Download an upload by its id

        API Endpoint: GET /uploads/{id}/download

        :param upload: the Upload to be downloaded
        :type upload: Upload
        :return: the upload content and the upload name
        :rtype: Tuple[str, str]
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        response = self.session.get(f"{self.api}/uploads/{upload.id}/download")

        if response.status_code == 200:
            content = response.headers["Content-Disposition"]
            upload_filename_pattern: str = (
                "(^attachment; filename=)(\"|')?([^\"|']*)(\"|'$)?"
            )
            upload_filename = re.match(upload_filename_pattern, content).group(3)  # type: ignore
            return response.content, upload_filename

        elif response.status_code == 403:
            description = f"Not authorized to download upload {upload.id}"
            raise AuthorizationError(description, response)

        else:
            description = f"Unable to download upload {upload.id}"
            raise FossologyApiError(description, response)

    def change_upload_permissions(
        self,
        upload: Upload,
        all_uploads: bool = False,
        group: Group | None = None,
        new_permission: Permission | None = None,
        public_permission: Permission | None = None,
    ):
        """Change the permission of an upload

        API Endpoint: PUT /uploads/{id}/permission

        :param upload: the upload to update
        :param group: the group you want to add or edit permission for this upload
        :param new_permission: the permission for the selected group
        :param public_permission: the public permission for this upload
        :type upload: Upload
        :type all_uploads: boolean (default: False)
        :type group: Group (default: None)
        :type new_permission: Permission (default: None)
        :type public_permission: Permission (default: None)
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        data = {
            "folderId": upload.folderid,
            "allUploadsPermission": all_uploads,
            "groupId": group.id if group else 0,
            "newPermission": new_permission.name.lower() if new_permission else "none",
            "publicPermission": public_permission.name.lower()
            if public_permission
            else "none",
        }
        response: requests.Response = self.session.put(
            f"{self.api}/uploads/{upload.id}/permissions", json=data
        )

        if response.status_code == 202:
            logger.info(
                f"Permissions for upload {upload.uploadname} have been updated."
            )

        elif response.status_code == 400:
            description = f"Permissions for upload {upload.uploadname} not updated."
            raise FossologyApiError(description, response)

        elif response.status_code == 403:
            description = (
                f"Updating permissions for upload {upload.id} is not authorized"
            )
            raise AuthorizationError(description, response)

        elif response.status_code == 404:
            description = f"Upload {upload.id} does not exists."
            raise FossologyApiError(description, response)

        elif response.status_code == 503:
            description = "Scheduler is not running."
            raise FossologyApiError(description, response)

        else:
            description = (
                f"API error while updating permissions for upload {upload.uploadname}."
            )
            raise FossologyApiError(description, response)

    def upload_permissions(
        self,
        upload: Upload,
    ):
        """Get all the groups with their respective permissions for an upload

        API Endpoint: GET /uploads/{id}/perm-groups

        :param upload: the upload to get permission from
        :type upload: Upload
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        response = self.session.get(f"{self.api}/uploads/{upload.id}/perm-groups")
        if response.status_code == 200:
            return UploadPermGroups.from_json(response.json())

        elif response.status_code == 403:
            description = (
                f"Getting permissions for upload {upload.id} is not authorized"
            )
            raise AuthorizationError(description, response)

        elif response.status_code == 404:
            description = f"Upload {upload.id} does not exists."
            raise FossologyApiError(description, response)
        else:
            description = (
                f"API error while getting permissions for upload {upload.uploadname}."
            )
            raise FossologyApiError(description, response)
