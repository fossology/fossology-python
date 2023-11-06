# Copyright 2023 Siemens AG
# SPDX-License-Identifier: MIT

import pytest
import responses
from tenacity import RetryError

from fossology import Fossology
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Upload


def test_upload_licenses(foss: Fossology, upload_with_jobs: Upload):
    # Default agent "nomos"
    licenses = foss.upload_licenses(upload_with_jobs)
    assert len(licenses) == 56


def test_upload_licenses_with_containers(foss: Fossology, upload_with_jobs: Upload):
    licenses = foss.upload_licenses(upload_with_jobs, containers=True)
    assert len(licenses) == 56


def test_upload_licenses_agent_ojo(foss: Fossology, upload_with_jobs: Upload):
    licenses = foss.upload_licenses(upload_with_jobs, agent="ojo")
    assert len(licenses) == 9


def test_upload_licenses_agent_monk(foss: Fossology, upload_with_jobs: Upload):
    licenses = foss.upload_licenses(upload_with_jobs, agent="monk")
    assert len(licenses) == 22


def test_upload_licenses_and_copyrights(foss: Fossology, upload_with_jobs: Upload):
    licenses = foss.upload_licenses(upload_with_jobs, copyright=True)
    assert len(licenses) == 56


def test_upload_licenses_with_unknown_group_raises_authorization_error(
    foss: Fossology, upload_with_jobs: Upload
):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_licenses(upload_with_jobs, group="test")
    assert (
        f"Getting licenses for upload {upload_with_jobs.id} is not authorized"
        in str(excinfo.value)
    )


@responses.activate
def test_upload_licenses_412_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/licenses",
        status=412,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_licenses(upload)
    assert (
        f"The agent nomos has not been scheduled for upload {upload.uploadname} (id={upload.id})"
        in excinfo.value.message
    )


@responses.activate
def test_upload_licenses_503_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/licenses",
        status=503,
    )
    with pytest.raises(RetryError):
        foss.upload_licenses(upload)


@responses.activate
def test_upload_licenses_500_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/licenses",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_licenses(upload)
    assert (
        f"API error while returning license findings for upload {upload.uploadname} (id={upload.id})"
        in excinfo.value.message
    )


def test_upload_copyrights(foss: Fossology, upload_with_jobs: Upload):
    copyrights = foss.upload_copyrights(upload_with_jobs)
    assert len(copyrights) == 79


@responses.activate
def test_upload_copyrights_403_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/copyrights",
        status=403,
    )
    with pytest.raises(AuthorizationError) as excinfo:
        foss.upload_copyrights(upload)
    assert (
        f"Getting copyrights for upload {upload.id} is not authorized"
        in excinfo.value.message
    )


@responses.activate
def test_upload_copyrights_412_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/copyrights",
        status=412,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_copyrights(upload)
    assert (
        f"The agent has not been scheduled for upload {upload.uploadname} (id={upload.id})"
        in excinfo.value.message
    )


@responses.activate
def test_upload_copyrights_503_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/copyrights",
        status=503,
    )
    with pytest.raises(RetryError):
        foss.upload_copyrights(upload)


@responses.activate
def test_upload_copyrights_500_error(foss: Fossology, foss_server: str, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/uploads/{upload.id}/copyrights",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.upload_copyrights(upload)
    assert (
        f"API error while returning copyright findings for upload {upload.uploadname} (id={upload.id})"
        in excinfo.value.message
    )
