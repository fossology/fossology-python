# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import mimetypes
import os
import secrets
import time
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import Mock

import pytest
import responses

from fossology import Fossology
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import AccessLevel, ClearingStatus, Folder, Upload


def test_upload_sha1(upload: Upload):
    assert upload.uploadname == "base-files_11.tar.xz"
    assert upload.hash.sha1 == "D4D663FC2877084362FB2297337BE05684869B00"
    assert str(upload) == (
        f"Upload '{upload.uploadname}' ({upload.id}, {upload.hash.size}B, {upload.hash.sha1}) "
        f"in folder {upload.foldername} ({upload.folderid})"
    )
    assert str(upload.hash) == (
        f"File SHA1: {upload.hash.sha1} MD5 {upload.hash.md5} "
        f"SH256 {upload.hash.sha256} Size {upload.hash.size}B"
    )


def test_get_upload_unauthorized(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.detail_upload(
            upload.id,
            group="test",
        )
    assert f"Getting details for upload {upload.id} is not authorized" in str(
        excinfo.value
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
        "Upload Test upload from github repository via python lib is not authorized"
        in str(excinfo.value)
    )


def test_list_upload_unknown_group(foss: Fossology):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.list_uploads(group="test")
    assert "Retrieving list of uploads is not authorized" in str(excinfo.value)


def test_get_uploads(
    foss: Fossology, upload: Upload, upload_folder: Folder, test_file_path: str
):
    name = "UploadSubfolderTest"
    desc = "Created via the Fossology Python API"
    upload_subfolder = foss.create_folder(upload_folder, name, description=desc)
    foss.upload_file(
        upload_subfolder,
        file=test_file_path,
        description="Test upload in subdirectory",
        wait_time=5,
    )
    assert len(foss.list_uploads()[0]) == 2
    assert len(foss.list_uploads(folder=foss.rootFolder)[0]) == 2
    assert len(foss.list_uploads(folder=foss.rootFolder, recursive=False)[0]) == 1
    assert len(foss.list_uploads(folder=upload_subfolder)[0]) == 1
    foss.delete_folder(upload_subfolder)


def test_filter_uploads(foss: Fossology, upload: Upload):
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert len(foss.list_uploads(assignee="-me-")[0]) == 0
    assert len(foss.list_uploads(assignee="-unassigned-")[0]) >= 1
    assert len(foss.list_uploads(name="Non-existing upload")[0]) == 0
    assert len(foss.list_uploads(name="Test upload")[0]) >= 1
    assert len(foss.list_uploads(status=ClearingStatus.CLOSED)[0]) == 0
    assert len(foss.list_uploads(status=ClearingStatus.OPEN)[0]) >= 1
    assert len(foss.list_uploads(since=tomorrow)[0]) == 0
    assert len(foss.list_uploads(since=today)[0]) >= 1


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


def test_move_upload(foss: Fossology, upload: Upload, move_folder: Folder):
    foss.move_upload(upload, move_folder, "move")
    moved_upload = foss.detail_upload(upload.id)
    assert moved_upload.folderid == move_folder.id


def test_copy_upload(foss: Fossology, upload: Upload):
    copy_upload_folder = foss.create_folder(foss.rootFolder, "CopyUploadFolder")
    foss.move_upload(upload, copy_upload_folder, "copy")
    copied_upload = foss.detail_upload(upload.id)
    assert copied_upload
    # Upload should be visible twice but it isn't
    # Bug or Feature?
    foss.delete_folder(copy_upload_folder)


def test_move_upload_to_non_existing_folder(foss: Fossology, upload: Upload):
    non_folder = Folder(secrets.randbelow(1000), "Non folder", "", foss.rootFolder)
    with pytest.raises(FossologyApiError):
        foss.move_upload(upload, non_folder, "move")


@responses.activate
def test_move_upload_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.PUT,
        f"{foss_server}/api/v1/uploads/{upload.id}",
        status=500,
    )
    with pytest.raises(FossologyApiError):
        foss.move_upload(upload, Mock(), "move")


def test_update_upload(foss: Fossology, upload: Upload):
    foss.update_upload(upload, ClearingStatus.INPROGRESS, "I am taking over", foss.user)
    summary = foss.upload_summary(upload)
    assert summary.clearingStatus == "InProgress"
    assert summary.additional_info["assignee"] == foss.user.id


def test_update_upload_with_unknown_group_raises_error(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.update_upload(upload, group="test")
    assert f"Updating upload {upload.id} is not authorized" in str(excinfo.value)


@responses.activate
def test_update_upload_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.PATCH,
        f"{foss_server}/api/v1/uploads/{upload.id}",
        status=500,
    )
    with pytest.raises(FossologyApiError):
        foss.update_upload(upload)


def test_upload_summary(foss: Fossology, upload: Upload):
    summary = foss.upload_summary(upload)
    assert summary.clearingStatus == "InProgress"
    assert not summary.mainLicense
    assert str(summary) == (
        f"Clearing status for '{summary.uploadName}' is '{summary.clearingStatus}',"
        f" main license = {summary.mainLicense}"
    )


@responses.activate
def test_upload_summary_500_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/summary",
        status=500,
    )
    with pytest.raises(FossologyApiError):
        foss.upload_summary(upload)


def test_upload_summary_with_unknown_group_raises_authorization_error(
    foss: Fossology, upload: Upload
):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_summary(upload, group="test")
    assert f"Getting summary of upload {upload.id} is not authorized" in str(
        excinfo.value
    )


def test_delete_unknown_upload_unknown_group(foss: Fossology, fake_hash: dict):
    upload = Upload(
        foss.rootFolder,
        "Root Folder",
        secrets.randbelow(1000),
        "",
        "Non Upload",
        "2020-05-05",
        hash=fake_hash,
    )
    with pytest.raises(FossologyApiError):
        foss.delete_upload(upload)

    with pytest.raises(AuthorizationError) as excinfo:
        foss.delete_upload(upload, group="test")
    assert f"Not authorized to delete upload {upload.id}" in str(excinfo.value)


def test_paginated_list_uploads(foss: Fossology, upload: Upload, test_file_path: str):
    # Add a second upload
    second_upload = foss.upload_file(
        foss.rootFolder,
        file=test_file_path,
        description="Test second upload via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
        wait_time=5,
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


@responses.activate
def test_list_uploads_500_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads",
        status=500,
    )
    with pytest.raises(FossologyApiError):
        foss.list_uploads()


def test_download_upload(foss: Fossology, upload: Upload):
    upload_content, upload_filename = foss.download_upload(upload)
    download_path = Path.cwd()
    with open(download_path / upload_filename, "wb") as upload_file:
        upload_file.write(upload_content)

    filetype = mimetypes.guess_type(download_path / upload_filename)
    upload_stat = os.stat(download_path / upload_filename)
    assert upload_stat.st_size > 0
    assert filetype == ("application/x-tar", "xz")
    Path(download_path / upload_filename).unlink()


@responses.activate
def test_download_upload_authorization_error(
    foss_server: str, foss: Fossology, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/download",
        status=403,
    )
    with pytest.raises(AuthorizationError) as excinfo:
        foss.download_upload(upload)
    assert f"Not authorized to download upload {upload.id}" in str(excinfo.value)


@responses.activate
def test_download_upload_error(foss_server: str, foss: Fossology, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/download",
        status=401,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.download_upload(upload)
    assert f"Unable to download upload {upload.id}" in str(excinfo.value)
