# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import secrets
import time
from datetime import date, timedelta

import pytest
import responses

from fossology import Fossology, versiontuple
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import AccessLevel, ClearingStatus, Folder, SearchTypes, Upload


def test_upload_sha1(foss: Fossology, upload: Upload):
    assert upload.uploadname == "base-files_11.tar.xz"
    if versiontuple(foss.version) > versiontuple("1.0.16"):
        assert upload.hash.sha1 == "D4D663FC2877084362FB2297337BE05684869B00"
        assert str(upload) == (
            f"Upload '{upload.uploadname}' ({upload.id}, {upload.hash.size}B, {upload.hash.sha1}) "
            f"in folder {upload.foldername} ({upload.folderid})"
        )
        assert str(upload.hash) == (
            f"File SHA1: {upload.hash.sha1} MD5 {upload.hash.md5} "
            f"SH256 {upload.hash.sha256} Size {upload.hash.size}B"
        )
    else:
        assert upload.filesha1 == "D4D663FC2877084362FB2297337BE05684869B00"
        assert str(upload) == (
            f"Upload '{upload.uploadname}' ({upload.id}, {upload.filesize}B, {upload.filesha1}) "
            f"in folder {upload.foldername} ({upload.folderid})"
        )


def test_get_upload_unauthorized(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.detail_upload(
            upload.id,
            group="test",
        )
    assert (
        f"Getting details for upload {upload.id} for group test not authorized"
        in str(excinfo.value)
    )


@responses.activate
def test_get_upload_error(foss: Fossology, foss_server: str):
    upload_id = 100
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload_id}",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.detail_upload(upload_id)
    assert f"Error while getting details for upload {upload_id}" in str(excinfo.value)


def test_upload_nogroup(foss: Fossology, upload_folder: Folder, test_file_path: str):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_file(
            upload_folder,
            file=test_file_path,
            description="Test upload from github repository via python lib",
            group="test",
        )
    assert (
        f"Upload of {test_file_path} for group test in folder {upload_folder.id} not authorized"
        in str(excinfo.value)
    )

    # Get get upload unknown group
    with pytest.raises(AuthorizationError) as excinfo:
        foss.list_uploads(group="test")
    assert "Retrieving list of uploads for group test not authorized" in str(
        excinfo.value
    )


def test_get_uploads(foss: Fossology, upload_folder: Folder, test_file_path: str):
    name = "FossPythonTestUploadsSubfolder"
    desc = "Created via the Fossology Python API"
    upload_subfolder = foss.create_folder(upload_folder, name, description=desc)
    foss.upload_file(
        upload_folder,
        file=test_file_path,
        description="Test upload from github repository via python lib",
    )
    foss.upload_file(
        upload_subfolder,
        file=test_file_path,
        description="Test upload from github repository via python lib",
    )
    # Folder listing is still unstable in version 1.0.16
    # Let's skip it since it has been fixed in newest versions
    if versiontuple(foss.version) > versiontuple("1.0.16"):
        assert len(foss.list_uploads(folder=upload_folder)[0]) == 2
        assert len(foss.list_uploads(folder=upload_folder, recursive=False)[0]) == 1
        assert len(foss.list_uploads(folder=upload_subfolder)[0]) == 1


def test_filter_uploads(foss: Fossology, upload: Upload):
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    # Uploads filtering has been enhance with API version 1.3.4
    if versiontuple(foss.version) >= versiontuple("1.3.4"):
        assert len(foss.list_uploads(assignee="-me-")[0]) == 0
        assert len(foss.list_uploads(assignee="-unassigned-")[0]) >= 1
        assert len(foss.list_uploads(name="Non-existing upload")[0]) == 0
        assert len(foss.list_uploads(name="Test upload")[0]) >= 1
        assert len(foss.list_uploads(status=ClearingStatus.CLOSED)[0]) == 0
        assert len(foss.list_uploads(status=ClearingStatus.OPEN)[0]) >= 1
        assert len(foss.list_uploads(since=tomorrow)[0]) == 0
        assert len(foss.list_uploads(since=today)[0]) >= 1


def test_upload_from_vcs(foss: Fossology):
    vcs = {
        "vcsType": "git",
        "vcsUrl": "https://github.com/fossology/fossology-python",
        "vcsName": "fossology-python-github-master",
        "vcsUsername": "",
        "vcsPassword": "",
    }
    vcs_upload = foss.upload_file(
        foss.rootFolder,
        vcs=vcs,
        description="Test upload from github repository via python lib",
        access_level=AccessLevel.PUBLIC,
    )
    assert vcs_upload.uploadname == vcs["vcsName"]
    search_result = foss.search(
        searchType=SearchTypes.DIRECTORIES,
        filename=".git",
    )
    assert not search_result
    foss.delete_upload(vcs_upload)


def test_upload_ignore_scm(foss: Fossology):
    vcs = {
        "vcsType": "git",
        "vcsUrl": "https://github.com/fossology/fossology-python",
        "vcsName": "fossology-python-github-master",
        "vcsUsername": "",
        "vcsPassword": "",
    }
    vcs_upload = foss.upload_file(
        foss.rootFolder,
        vcs=vcs,
        description="Test upload with ignore_scm flag",
        ignore_scm=False,
        access_level=AccessLevel.PUBLIC,
    )
    assert vcs_upload.uploadname == vcs["vcsName"]
    # FIXME: shall be fixed in the next release
    # assert foss.search(
    #    searchType=SearchTypes.DIRECTORIES, filename=".git",
    # ) == $something

    # Cleanup
    foss.delete_upload(vcs_upload)


def test_upload_from_url(foss: Fossology):
    url = {
        "url": "https://github.com/fossology/fossology-python/archive/master.zip",
        "name": "fossology-python-master.zip",
        "accept": "zip",
        "reject": "",
        "maxRecursionDepth": "1",
    }
    url_upload = foss.upload_file(
        foss.rootFolder,
        url=url,
        description="Test upload from url via python lib",
        access_level=AccessLevel.PUBLIC,
    )
    assert url_upload.uploadname == url["name"]

    # Cleanup
    foss.delete_upload(url_upload)


def test_upload_from_server(foss: Fossology):
    server = {
        "path": "/tmp/base-files-11",
        "name": "base-files-11",
    }
    server_upload = foss.upload_file(
        foss.rootFolder,
        server=server,
        description="Test upload from server via python lib",
        access_level=AccessLevel.PUBLIC,
    )
    assert server_upload.uploadname == server["name"]

    # Cleanup
    foss.delete_upload(server_upload)


def test_empty_upload(foss: Fossology):
    empty_upload = foss.upload_file(
        foss.rootFolder,
        description="Test empty upload",
        access_level=AccessLevel.PUBLIC,
    )
    assert not empty_upload


@responses.activate
def test_upload_error(foss: Fossology, foss_server: str, test_file_path: str):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v1/uploads",
        status=500,
    )
    description = "Test upload API error"
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_file(
            foss.rootFolder,
            file=test_file_path,
            description=description,
        )
    assert f"Upload {description} could not be performed" in str(excinfo.value)


def test_move_upload_nogroup(foss: Fossology, upload: Upload, move_folder: Folder):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.move_upload(upload, move_folder, group="test")
    assert (
        f"Moving upload {upload.id} for group test in folder {move_folder.id} not authorized"
        in str(excinfo.value)
    )


def test_move_upload(foss: Fossology, upload: Upload, move_folder: Folder):
    foss.move_upload(upload, move_folder)
    moved_upload = foss.detail_upload(upload.id)
    assert moved_upload.folderid == move_folder.id


def test_copy_upload(foss: Fossology, upload: Upload):
    copy_upload_folder = foss.create_folder(foss.rootFolder, "CopyUploadFolder")
    foss.copy_upload(upload, copy_upload_folder)
    copied_upload = foss.detail_upload(upload.id)
    assert copied_upload
    # Upload should be visible twice but it isn't
    # Bug or Feature?
    # Cleanup
    foss.delete_folder(copy_upload_folder)


def test_move_upload_to_non_existing_folder(foss: Fossology, upload: Upload):
    non_folder = Folder(secrets.randbelow(1000), "Non folder", "", foss.rootFolder)
    with pytest.raises(AuthorizationError):
        foss.move_upload(upload, non_folder)


def test_copy_upload_to_non_existing_folder(foss: Fossology, upload: Upload):
    non_folder = Folder(secrets.randbelow(1000), "Non folder", "", foss.rootFolder)
    with pytest.raises(AuthorizationError):
        foss.copy_upload(upload, non_folder)


def test_upload_summary(foss: Fossology, scanned_upload: Upload):
    summary = foss.upload_summary(scanned_upload)
    assert summary.clearingStatus == "Open"
    assert not summary.mainLicense
    assert str(summary) == (
        f"Clearing status for '{summary.uploadName}' is '{summary.clearingStatus}',"
        f" main license = {summary.mainLicense}"
    )

    # Unknown group
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_summary(scanned_upload, group="test")
    assert (
        f"Getting summary of upload {scanned_upload.id} for group test not authorized"
        in str(excinfo.value)
    )


def test_upload_licenses(foss: Fossology, scanned_upload: Upload):
    # Default agent "nomos"
    licenses = foss.upload_licenses(scanned_upload)
    assert len(licenses) == 56
    licenses = foss.upload_licenses(scanned_upload, containers=True)
    assert len(licenses) == 56

    # Specific agent "ojo"
    licenses = foss.upload_licenses(scanned_upload, agent="ojo")
    assert len(licenses) == 9

    # Specific agent "monk"
    licenses = foss.upload_licenses(scanned_upload, agent="monk")
    assert len(licenses) == 23

    # Unknown group
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_licenses(scanned_upload, group="test")
    assert (
        f"Getting license for upload {scanned_upload.id} for group test not authorized"
        in str(excinfo.value)
    )


def test_delete_unknown_upload_unknown_group(foss: Fossology):
    if versiontuple(foss.version) > versiontuple("1.0.16"):
        upload = Upload(
            foss.rootFolder,
            "Root Folder",
            secrets.randbelow(1000),
            "",
            "Non Upload",
            "2020-05-05",
            hash={"sha1": None, "md5": None, "sha256": None, "size": None},
        )
    else:
        upload = Upload(
            foss.rootFolder,
            "Root Folder",
            secrets.randbelow(1000),
            "",
            "Non Upload",
            "2020-05-05",
            filesize="1024",
            filesha1="597d209fd962f401866f12db9fa1f7301aee15a9",
        )
    with pytest.raises(FossologyApiError):
        foss.delete_upload(upload)

    with pytest.raises(AuthorizationError) as excinfo:
        foss.delete_upload(upload, group="test")
    assert f"Deleting upload {upload.id} for group test not authorized" in str(
        excinfo.value
    )


def test_paginated_list_uploads(foss: Fossology, upload: Upload, test_file_path: str):
    if versiontuple(foss.version) < versiontuple("1.1.1"):
        # Upload pagination not available yet
        return
    # Add a second upload
    second_upload = foss.upload_file(
        foss.rootFolder,
        file=test_file_path,
        description="Test second upload via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
    )
    time.sleep(3)
    uploads, _ = foss.list_uploads(page_size=1, page=1)
    assert len(uploads) == 1

    uploads, _ = foss.list_uploads(page_size=1, page=2)
    assert len(uploads) == 1

    uploads, _ = foss.list_uploads(page_size=2, page=1)
    assert len(uploads) == 2

    uploads, _ = foss.list_uploads(page_size=1, all_pages=True)
    num_known_uploads = 0
    for up in uploads:
        if up.description in (
            "Test upload via fossology-python lib",
            "Test second upload via fossology-python lib",
        ):
            num_known_uploads += 1
    assert num_known_uploads >= 2

    foss.delete_upload(second_upload)
