# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import mimetypes
import os
import secrets
from pathlib import Path

import pytest
import responses

from fossology import Fossology
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import ReportFormat, Upload


def test_report_nogroup(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.generate_report(upload, report_format=ReportFormat.SPDX2, group="test")
    assert (
        f"Generating report for upload {upload.id} for group test not authorized"
        in str(excinfo.value)
    )


def test_download_report_nogroup(foss: Fossology, upload: Upload):
    report_id = secrets.randbelow(1000)
    with pytest.raises(AuthorizationError) as excinfo:
        foss.download_report(report_id, group="test")
        assert f"Getting report {report_id} for group test not authorized" in str(
            excinfo.value
        )


def test_generate_report(foss: Fossology, upload: Upload):
    report_id = foss.generate_report(upload, report_format=ReportFormat.SPDX2)
    assert report_id

    # Plain text
    report, report_name = foss.download_report(report_id)
    report_path = Path.cwd() / "tests/files"
    with open(report_path / report_name, "w+") as report_file:
        report_file.write(report)

    filetype = mimetypes.guess_type(report_path / report_name)
    report_stat = os.stat(report_path / report_name)
    assert report_stat.st_size > 0
    assert "application/rdf+xml" or "application/xml" in filetype[0]
    Path(report_path / report_name).unlink()


@responses.activate
def test_report_error(foss_server: str, foss: Fossology, upload: Upload):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report",
        status=503,
        headers={"Retry-After": "1"},
    )
    responses.add(responses.GET, f"{foss_server}/api/v1/report", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.generate_report(upload)
    assert f"Report generation for upload {upload.uploadname} failed" in str(
        excinfo.value
    )


@responses.activate
def test_download_report_error(foss_server: str, foss: Fossology):
    report_id = secrets.randbelow(1000)
    responses.add(
        responses.GET, f"{foss_server}/api/v1/report/{report_id}", status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.download_report(report_id)
    assert f"Download of report {report_id} failed" in str(excinfo.value)
