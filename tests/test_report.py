# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import os
import mimetypes
import pytest

from pathlib import Path
from fossology import Fossology
from fossology.exceptions import AuthorizationError
from fossology.obj import Upload, ReportFormat


def test_report_nogroup(foss: Fossology, upload: Upload):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.generate_report(upload, report_format=ReportFormat.SPDX2, group="test")
    assert (
        f"Generating report for upload {upload.id} for group test not authorized"
        in str(excinfo.value)
    )


def test_generate_report(foss: Fossology, upload: Upload):
    report_id = foss.generate_report(upload, report_format=ReportFormat.SPDX2)
    assert report_id

    # Get report for unknown group
    with pytest.raises(AuthorizationError) as excinfo:
        foss.download_report(report_id, group="test")
    assert f"Getting report {report_id} for group test not authorized" in str(
        excinfo.value
    )

    # Plain text
    report = foss.download_report(report_id)
    report_path = Path.cwd() / "tests/files"
    report_name = upload.uploadname + ".spdx-report.rdf"
    with open(report_path / report_name, "w+") as report_file:
        report_file.write(report)

    filetype = mimetypes.guess_type(report_path / report_name)
    report_stat = os.stat(report_path / report_name)
    assert report_stat.st_size > 0
    assert "application/rdf+xml" or "application/xml" in filetype[0]
    Path(report_path / report_name).unlink()

    # Zip
    report = foss.download_report(report_id, as_zip=True)
    report_path = Path.cwd() / "tests/files"
    report_name = upload.uploadname + ".spdx-report.rdf.zip"
    with open(report_path / report_name, "w+") as report_file:
        report_file.write(report)

    filetype = mimetypes.guess_type(report_path / report_name)
    report_stat = os.stat(report_path / report_name)
    assert report_stat.st_size > 0
    assert filetype[0] == "application/zip"
    Path(report_path / report_name).unlink()
