# Copyright 2023 Siemens AG
# SPDX-License-Identifier: MIT

import secrets

import pytest
import responses

from fossology import Fossology
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Permission, Upload


def test_change_upload_permissions(foss: Fossology, upload: Upload):
    group_name = secrets.token_urlsafe(8)
    foss.create_group(group_name)
    for group in foss.list_groups():
        if group.name == group_name:
            break
    foss.change_upload_permissions(
        upload,
        group=group,
        new_permission=Permission.READ_WRITE,
        public_permission=Permission.READ_ONLY,
    )
    permissions = foss.upload_permissions(upload)
    assert permissions.publicPerm == Permission.READ_ONLY
    permissions_results = list()
    for permission in permissions.permGroups:
        permissions_results.append(str(permission))
    assert (
        f"Group {group.name} ({group.id}) with {Permission.READ_WRITE.name} permission"
    ) in permissions_results
    # Cleanup
    foss.delete_group(group.id)


def test_get_upload_permissions_if_upload_does_not_exists_raise_api_error(
    foss: Fossology, fake_hash: dict
):
    upload = Upload(
        1,
        "non-existing-folder",
        secrets.randbelow(1092),
        "non-existing upload",
        "none",
        "2023-08-07",
        hash=fake_hash,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_permissions(upload)
    assert f"Upload {upload.id} does not exists." in str(excinfo.value)


@responses.activate
def test_get_upload_permissions_if_api_returns_403_raises_authorization_error(
    foss: Fossology, foss_server: str, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v2/uploads/{upload.id}/perm-groups",
        status=403,
    )
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_permissions(upload)
    assert f"Getting permissions for upload {upload.id} is not authorized" in str(
        excinfo.value.message
    )


@responses.activate
def test_get_upload_permissions_if_api_returns_500_raises_fossology_error(
    foss: Fossology, foss_server: str, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v2/uploads/{upload.id}/perm-groups",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_permissions(upload)
    assert (
        f"API error while getting permissions for upload {upload.uploadname}."
        in str(excinfo.value.message)
    )


def test_change_upload_permissions_if_upload_does_not_exists_raise_api_error(
    foss: Fossology, fake_hash: dict
):
    upload = Upload(
        1,
        "non-existing-folder",
        secrets.randbelow(192),
        "non-existing upload",
        "none",
        "2023-08-07",
        hash=fake_hash,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.change_upload_permissions(upload)
    assert f"Upload {upload.id} does not exists" in str(excinfo.value)


@responses.activate
def test_change_upload_permissions_if_api_returns_400_raises_fossology_error(
    foss: Fossology, foss_server: str, upload: Upload
):
    responses.add(
        responses.PUT,
        f"{foss_server}/api/v2/uploads/{upload.id}/permissions",
        status=400,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.change_upload_permissions(upload)
    assert f"Permissions for upload {upload.uploadname} not updated." in str(
        excinfo.value.message
    )


@responses.activate
def test_change_upload_permissions_if_api_returns_403_raises_authorization_error(
    foss: Fossology, foss_server: str, upload: Upload
):
    responses.add(
        responses.PUT,
        f"{foss_server}/api/v2/uploads/{upload.id}/permissions",
        status=403,
    )
    with pytest.raises(AuthorizationError) as excinfo:
        foss.change_upload_permissions(upload)
    assert f"Updating permissions for upload {upload.id} is not authorized" in str(
        excinfo.value.message
    )


@responses.activate
def test_change_upload_permissions_if_api_returns_500_raises_fossology_error(
    foss: Fossology, foss_server: str, upload: Upload
):
    responses.add(
        responses.PUT,
        f"{foss_server}/api/v2/uploads/{upload.id}/permissions",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.change_upload_permissions(upload)
    assert (
        f"API error while updating permissions for upload {upload.uploadname}."
        in str(excinfo.value.message)
    )


@responses.activate
def test_change_upload_permissions_if_api_returns_503_raises_fossology_error(
    foss: Fossology, foss_server: str, upload: Upload
):
    responses.add(
        responses.PUT,
        f"{foss_server}/api/v2/uploads/{upload.id}/permissions",
        status=503,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.change_upload_permissions(upload)
    assert "Scheduler is not running." in str(excinfo.value.message)
