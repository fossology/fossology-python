# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock

import pytest
import responses

import fossology
from fossology.enums import LicenseType, ObligationClass
from fossology.exceptions import FossologyApiError
from fossology.obj import License, Obligation


@pytest.fixture()
def test_license():
    shortname = "License-1.0"
    fullname = "Open source license 1.0"
    text = "This is the text for license 1.0"
    url = "https://licenses.org/license1.txt"
    risk = 2
    return License(shortname, fullname, text, url, risk, False)


@pytest.fixture()
def test_another_license():
    shortname = "License-2.0"
    fullname = "Open source license 2.0"
    text = "This is the text for license 2.0"
    url = "https://licenses.org/license2.txt"
    risk = 3
    return License(shortname, fullname, text, url, risk, False)


def test_import_licenses_csv(foss: fossology.Fossology, tmp_path):
    csv_path = tmp_path / "licenses.csv"
    csv_path.write_text(
        "shortname,fullname,text,parent,report,url,risk,group,notes\n"
        "CsvImportTestLic,Csv Import Test Lic,License text body,,white,"
        "http://example.com/csv,5,,\n"
    )
    message = foss.import_licenses_csv(str(csv_path))
    # Server returns multi-line summary; either freshly inserted or already
    # present from a prior run — both are valid outcomes for an idempotent import.
    assert "CsvImportTestLic" in message
    assert "Read csv: 1 licenses" in message


@responses.activate
def test_import_licenses_csv_error(
    foss_server: str, foss: fossology.Fossology, tmp_path
):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v1/license/import-csv",
        status=400,
    )
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("not really a csv\n")
    with pytest.raises(FossologyApiError) as excinfo:
        foss.import_licenses_csv(str(csv_path))
    assert f"Unable to import licenses from {csv_path}" in str(excinfo.value)


@responses.activate
def test_import_licenses_csv_request_payload(
    foss_server: str, foss: fossology.Fossology, tmp_path
):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v1/license/import-csv",
        status=200,
        json={"code": 200, "message": "head okay\nRead csv: 1 licenses", "type": "INFO"},
    )
    csv_path = tmp_path / "lic.csv"
    csv_path.write_text("shortname,fullname\nFoo,Foo License\n")

    message = foss.import_licenses_csv(str(csv_path), delimiter=";", enclosure="'")

    assert "Read csv: 1 licenses" in message
    assert len(responses.calls) == 1
    body = responses.calls[0].request.body.decode("utf-8", errors="ignore")
    assert 'name="file_input"' in body
    assert 'name="delimiter"' in body and "\r\n\r\n;\r\n" in body
    assert 'name="enclosure"' in body and "\r\n\r\n'\r\n" in body
    assert "shortname,fullname\nFoo,Foo License" in body


def test_export_import_licenses_csv_roundtrip(foss: fossology.Fossology, tmp_path):
    # Export the full license set, then re-import it. The export format matches
    # the import format, and re-importing existing licenses is idempotent.
    exported = foss.export_licenses_csv()
    assert isinstance(exported, str)
    assert exported
    csv_path = tmp_path / "exported.csv"
    csv_path.write_text(exported)
    message = foss.import_licenses_csv(str(csv_path))
    assert "Read csv" in message


@responses.activate
def test_export_licenses_csv_error(foss_server: str, foss: fossology.Fossology):
    responses.add(
        responses.GET, f"{foss_server}/api/v1/license/export-csv", status=403
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.export_licenses_csv()
    assert "Unable to export licenses as CSV (id=0)" in str(excinfo.value)


@responses.activate
def test_detail_license_error(foss_server: str, foss: fossology.Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/license/Blah", status=500)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.detail_license("Blah")
    assert "Error while getting license Blah" in str(excinfo.value)


def test_detail_license_not_found(foss: fossology.Fossology):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.detail_license("Unknown")
    assert "License Unknown not found" in str(excinfo.value)


@responses.activate
def test_list_licenses_error(foss_server: str, foss: fossology.Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/license", status=500)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.list_licenses()
    assert "Unable to retrieve the list of licenses from page 1" in str(excinfo.value)


def test_get_all_licenses(foss: fossology.Fossology):
    licenses, num_pages = foss.list_licenses(active=True, all_pages=True)
    assert licenses
    assert num_pages


def test_get_all_licenses_first_page(foss: fossology.Fossology):
    licenses, num_pages = foss.list_licenses()
    assert len(licenses) == 100
    assert num_pages


def test_get_all_candidate_licenses(foss: fossology.Fossology):
    licenses, num_pages = foss.list_licenses(kind=LicenseType.CANDIDATE)
    assert not licenses
    assert not num_pages


@responses.activate
def test_add_license_error(
    foss_server: str, foss: fossology.Fossology, test_license: License
):
    responses.add(responses.POST, f"{foss_server}/api/v1/license", status=500)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.add_license(test_license)
    assert f"Error while adding new license {test_license.shortName}" in str(
        excinfo.value
    )


@responses.activate
def test_add_license_already_exists(
    foss_server: str,
    foss: fossology.Fossology,
    monkeypatch,
    test_license: License,
):
    mocked_logger = MagicMock()
    monkeypatch.setattr("fossology.license.logger", mocked_logger)
    responses.add(responses.POST, f"{foss_server}/api/v1/license", status=409)
    foss.add_license(test_license)
    mocked_logger.info.assert_called_once()


def test_add_license_and_get_by_shortname(
    foss: fossology.Fossology, test_license: License, monkeypatch
):
    mocked_logger = MagicMock()
    monkeypatch.setattr("fossology.license.logger", mocked_logger)
    foss.add_license(test_license)
    license_found = foss.detail_license(test_license.shortName)
    assert license_found.shortName == "License-1.0"
    expected_license_repr = (
        f"License {license_found.fullName} - {license_found.shortName} "
    )
    expected_license_repr += (
        f"({license_found.id}) with risk level {license_found.risk}"
    )
    assert str(license_found) == expected_license_repr

    foss.add_license(test_license, merge_request=True)
    mocked_logger.info.assert_called_with(
        f"License {test_license.shortName} already exists"
    )


@responses.activate
def test_patch_license_error(
    foss_server: str, foss: fossology.Fossology, test_license: License
):
    responses.add(
        responses.PATCH, f"{foss_server}/api/v1/license/License-1.0", status=500
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.update_license(test_license.shortName)
    assert f"Unable to update license {test_license.shortName}" in str(excinfo.value)


def test_patch_license_and_get_by_shortname(
    foss: fossology.Fossology, test_another_license: License
):
    foss.add_license(test_another_license)
    foss.update_license(
        test_another_license.shortName, fullname="Inner Source license 2.0", risk=1
    )
    license_found = foss.detail_license(test_another_license.shortName)
    assert license_found.shortName == "License-2.0"
    assert license_found.fullName == "Inner Source license 2.0"
    assert license_found.risk == 1


def test_license_to_json(test_license: License):
    json_license = test_license.to_json()
    assert isinstance(json_license, str)


def test_obligation_object():
    obligation = Obligation(
        1,
        "do not modify",
        "Obligation",
        "do not modify files licensed under this license",
        ObligationClass.YELLOW.value,
        "",
    )
    expected_obligation_repr = (
        "Obligation do not modify, Obligation (1) is classified yellow"
    )
    assert str(obligation) == expected_obligation_repr
