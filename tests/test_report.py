# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import mimetypes
import os
import secrets
from pathlib import Path

import pytest
import responses

from fossology import Fossology
from fossology.enums import ReportFormat
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Upload


def test_report_nogroup(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.generate_report(upload, report_format=ReportFormat.SPDX3JSON, group="test")
    assert f"Report generation for upload {upload.id} not authorized" in str(
        excinfo.value
    )


def test_download_report_nogroup(foss: Fossology, upload: Upload):
    report_id = secrets.randbelow(1000)
    with pytest.raises(AuthorizationError) as excinfo:
        foss.download_report(report_id, group="test")
    assert f"Download of report {report_id} not authorized" in str(excinfo.value)


def test_generate_report(foss: Fossology, upload: Upload):
    report_id = foss.generate_report(upload, report_format=ReportFormat.SPDX3JSON)
    assert report_id

    # Plain text
    report, report_name = foss.download_report(report_id)
    report_path = Path.cwd() / "tests/files"
    with open(report_path / report_name, "wb") as report_file:
        report_file.write(report)

    filetype = mimetypes.guess_type(report_path / report_name)
    report_stat = os.stat(report_path / report_name)
    assert report_stat.st_size > 0
    assert filetype[0] in ("application/rdf+xml", "application/xml", "application/json")
    Path(report_path / report_name).unlink()


def test_import_report(foss: Fossology, upload: Upload, tmp_path: Path):
    # `ReportFormat.SPDX3JSON` generates SPDX 3.x in JSON, which is the same on-wire
    # format the import endpoint's default "spdx3json" accepts. Round-trip the
    # report file: generate → download → import.
    report_id = foss.generate_report(upload, report_format=ReportFormat.SPDX3JSON)
    report_content, report_name = foss.download_report(report_id)
    report_file = tmp_path / report_name
    report_file.write_bytes(report_content)

    job_id = foss.import_report(upload, str(report_file))
    assert isinstance(job_id, int)
    assert job_id > 0


@responses.activate
def test_import_report_nogroup(
    foss_server: str, foss: Fossology, upload: Upload, tmp_path: Path
):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v1/report/import",
        status=403,
    )
    report_file = tmp_path / "dummy.rdf"
    report_file.write_bytes(b"<rdf></rdf>")
    with pytest.raises(AuthorizationError) as excinfo:
        foss.import_report(upload, str(report_file), group="test")
    assert (
        f"Report import for upload {upload.uploadname} (id={upload.id}) "
        f"is not authorized"
    ) in str(excinfo.value)


@responses.activate
def test_import_report_error(
    foss_server: str, foss: Fossology, upload: Upload, tmp_path: Path
):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v1/report/import",
        status=500,
    )
    report_file = tmp_path / "dummy.rdf"
    report_file.write_bytes(b"<rdf></rdf>")
    with pytest.raises(FossologyApiError) as excinfo:
        foss.import_report(upload, str(report_file))
    assert (
        f"Report import for upload {upload.uploadname} (id={upload.id}) failed"
    ) in str(excinfo.value)


@responses.activate
def test_generate_report_unparseable_message(
    foss_server: str, foss: Fossology, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report",
        status=201,
        json={"code": 201, "message": "Report has been queued."},
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.generate_report(upload)
    assert "report ID could not be parsed" in str(excinfo.value)


@responses.activate
def test_generate_report_malformed_response_body(
    foss_server: str, foss: Fossology, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report",
        status=201,
        body="<html>Internal Server Error</html>",
        content_type="text/html",
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.generate_report(upload)
    assert "response could not be parsed" in str(excinfo.value)


@responses.activate
def test_generate_report_missing_message_key(
    foss_server: str, foss: Fossology, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report",
        status=201,
        json={"code": 201, "type": "INFO"},
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.generate_report(upload)
    assert "response could not be parsed" in str(excinfo.value)


@responses.activate
def test_generate_report_non_string_message(
    foss_server: str, foss: Fossology, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report",
        status=201,
        json={"code": 201, "message": 42},
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.generate_report(upload)
    assert "response could not be parsed" in str(excinfo.value)


@responses.activate
def test_generate_report_returns_int(
    foss_server: str, foss: Fossology, upload: Upload
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report",
        status=201,
        json={
            "code": 201,
            "message": (
                "Report will be generated in the back ground, "
                "report id is 42"
            ),
        },
    )
    report_id = foss.generate_report(upload)
    assert report_id == 42
    assert isinstance(report_id, int)


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
        responses.GET,
        f"{foss_server}/api/v1/report/{report_id}",
        status=500,
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.download_report(report_id)
    assert f"Download of report {report_id} failed" in str(excinfo.value)


@responses.activate
def test_download_report_filename_without_quotes(foss_server: str, foss: Fossology):
    report_id = 1
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report/{report_id}",
        status=200,
        headers={"Content-Disposition": "attachment; filename=Report_FileName.docx"},
    )
    _, report_name = foss.download_report(report_id)
    assert report_name == "Report_FileName.docx"


@responses.activate
def test_download_report_filename_with_quotes(foss_server: str, foss: Fossology):
    report_id = 1
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report/{report_id}",
        status=200,
        headers={"Content-Disposition": 'attachment; filename="Report_FileName.docx"'},
    )
    _, report_name = foss.download_report(report_id)
    assert report_name == "Report_FileName.docx"


@responses.activate
def test_download_report_filename_with_single_quotes(foss_server: str, foss: Fossology):
    report_id = 1
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report/{report_id}",
        status=200,
        headers={"Content-Disposition": "attachment; filename='Report_FileName.docx'"},
    )
    _, report_name = foss.download_report(report_id)
    assert report_name == "Report_FileName.docx"


@responses.activate
def test_download_report_filename_with_extended_parameter(
    foss_server: str, foss: Fossology
):
    report_id = "1"
    filename = "CLIXML_cifs-utils_2%3A6.14-1ubuntu0.3-ubuntu-combined.tar.bz2.xml"
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/report/{report_id}",
        status=200,
        headers={
            "Content-Disposition": (
                f"attachment; filename={filename}; filename*=UTF-8''{filename}"
            )
        },
    )
    _, report_name = foss.download_report(report_id)
    assert report_name == filename
