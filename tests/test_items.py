# Copyright 2023 Siemens AG
# SPDX-License-Identifier: MIT

import pytest
import responses

from fossology import Fossology
from fossology.enums import CopyrightStatus, PrevNextSelection
from fossology.exceptions import FossologyApiError
from fossology.obj import FileInfo, Upload


def test_item_info(foss: Fossology, upload_with_jobs: Upload):
    files, _ = foss.search(license="BSD")
    info: FileInfo = foss.item_info(upload_with_jobs, files[0].uploadTreeId)
    assert info.meta_info


def test_item_info_v1(foss_v1: Fossology, upload_with_jobs: Upload):
    files, _ = foss_v1.search(license="BSD")
    info: FileInfo = foss_v1.item_info(upload_with_jobs, files[0].uploadTreeId)
    assert info.meta_info


def test_item_info_with_unknown_item_raises_api_error(
    foss: Fossology, upload_with_jobs: Upload
):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.item_info(upload_with_jobs, 1)
    assert f"Upload {upload_with_jobs.id} or item 1 not found" in str(excinfo.value)


@responses.activate
def test_item_info_500_error(
    foss: Fossology, foss_server: str, upload_with_jobs: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v2/uploads/{upload_with_jobs.id}/item/1/info",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.item_info(upload_with_jobs, 1)
    assert (
        f"API error while getting info for item 1 from upload {upload_with_jobs.uploadname}"
        in excinfo.value.message
    )


def test_item_copyrights(foss: Fossology, upload_with_jobs: Upload):
    files, _ = foss.search(license="BSD")
    num_copyrights = foss.item_copyrights(
        upload_with_jobs, files[0].uploadTreeId, CopyrightStatus.ACTIVE
    )
    assert num_copyrights == 0


def test_item_copyrights_with_unknown_item_raises_api_error(
    foss: Fossology, upload_with_jobs: Upload
):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.item_copyrights(upload_with_jobs, 1, CopyrightStatus.ACTIVE)
    assert f"Upload {upload_with_jobs.id} or item 1 not found" in str(excinfo.value)


@responses.activate
def test_item_copyrights_500_error(
    foss: Fossology, foss_server: str, upload_with_jobs: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v2/uploads/{upload_with_jobs.id}/item/1/totalcopyrights",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.item_copyrights(upload_with_jobs, 1, CopyrightStatus.ACTIVE)
    assert (
        f"API error while getting total copyrights for item 1 from upload {upload_with_jobs.uploadname}"
        in excinfo.value.message
    )


def test_upload_get_clearing_history(foss: Fossology, upload_with_jobs: Upload):
    files, _ = foss.search(license="BSD")
    history = foss.get_clearing_history(upload_with_jobs, files[0].uploadTreeId)
    assert not history


def test_upload_get_clearing_history_with_unknown_item_raises_api_error(
    foss: Fossology, upload_with_jobs: Upload
):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.get_clearing_history(upload_with_jobs, 1)
    assert f"Upload {upload_with_jobs.id} or item 1 not found" in str(excinfo.value)


@responses.activate
def test_upload_get_clearing_history_500_error(
    foss: Fossology, foss_server: str, upload_with_jobs: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v2/uploads/{upload_with_jobs.id}/item/1/clearing-history",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.get_clearing_history(upload_with_jobs, 1)
    assert (
        f"API error while getting clearing history for item 1 from upload {upload_with_jobs.uploadname}."
        in excinfo.value.message
    )


def test_upload_get_bulk_history(foss: Fossology, upload_with_jobs: Upload):
    files, _ = foss.search(license="BSD")
    history = foss.get_bulk_history(upload_with_jobs, files[0].uploadTreeId)
    assert not history


def test_upload_get_bulk_history_with_unknown_item_raises_api_error(
    foss: Fossology, upload_with_jobs: Upload
):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.get_bulk_history(upload_with_jobs, 1)
    assert f"Upload {upload_with_jobs.id} or item 1 not found" in str(excinfo.value)


@responses.activate
def test_upload_get_bulk_history_500_error(
    foss: Fossology, foss_server: str, upload_with_jobs: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v2/uploads/{upload_with_jobs.id}/item/1/clearing-history",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.get_clearing_history(upload_with_jobs, 1)
    assert (
        f"API error while getting clearing history for item 1 from upload {upload_with_jobs.uploadname}."
        in excinfo.value.message
    )


def test_upload_schedule_bulk_scan(
    foss: Fossology, upload_with_jobs: Upload, foss_bulk_scan_spec: dict
):
    files, _ = foss.search(license="BSD")
    history = foss.get_bulk_history(upload_with_jobs, files[0].uploadTreeId)
    assert not history
    foss.schedule_bulk_scan(
        upload_with_jobs, files[0].uploadTreeId, foss_bulk_scan_spec
    )
    history = foss.get_bulk_history(upload_with_jobs, files[0].uploadTreeId)
    assert history[0].addedLicenses == ["MIT"]


def test_schedule_bulk_scan_with_unknown_item_raises_api_error(
    foss: Fossology, upload_with_jobs: Upload, foss_bulk_scan_spec: dict
):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.schedule_bulk_scan(upload_with_jobs, 1, foss_bulk_scan_spec)
    assert f"Upload {upload_with_jobs.id} or item 1 not found" in str(excinfo.value)


@responses.activate
def test_schedule_bulk_scan_500_error(
    foss: Fossology,
    foss_server: str,
    upload_with_jobs: Upload,
    foss_bulk_scan_spec: dict,
):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v2/uploads/{upload_with_jobs.id}/item/1/bulk-scan",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.schedule_bulk_scan(upload_with_jobs, 1, foss_bulk_scan_spec)
    assert (
        f"API error while scheduling bulk scan for item 1 from upload {upload_with_jobs.uploadname}."
        in excinfo.value.message
    )


def test_upload_get_prev_next(foss: Fossology, upload_with_jobs: Upload):
    files, _ = foss.search(license="BSD")
    prev_next = foss.get_prev_next(upload_with_jobs, files[0].uploadTreeId)
    assert prev_next


def test_upload_get_prev_next_with_licenses(foss: Fossology, upload_with_jobs: Upload):
    files, _ = foss.search(license="BSD")
    prev_next = foss.get_prev_next(
        upload_with_jobs, files[0].uploadTreeId, PrevNextSelection.WITHLICENSES.value
    )
    assert prev_next


def test_upload_get_prev_next_no_clearing(foss: Fossology, upload_with_jobs: Upload):
    files, _ = foss.search(license="BSD")
    prev_next = foss.get_prev_next(
        upload_with_jobs, files[0].uploadTreeId, PrevNextSelection.NOCLEARING.value
    )
    assert prev_next


def test_upload_get_prev_next_with_unknown_item_raises_api_error(
    foss: Fossology, upload_with_jobs: Upload
):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.get_prev_next(upload_with_jobs, 1)
    assert f"Upload {upload_with_jobs.id} or item 1 not found" in str(excinfo.value)


@responses.activate
def test_upload_get_prev_next_500_error(
    foss: Fossology, foss_server: str, upload_with_jobs: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v2/uploads/{upload_with_jobs.id}/item/1/prev-next",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.get_prev_next(upload_with_jobs, 1)
    assert (
        f"API error while getting prev-next items for 1 from upload {upload_with_jobs.uploadname}."
        in excinfo.value.message
    )
