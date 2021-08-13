# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

from unittest.mock import MagicMock

import pytest
import responses

import fossology
from fossology.exceptions import FossologyApiError, FossologyUnsupported
from fossology.obj import License, LicenseType, Obligation, ObligationClass

shortname = "GPL-2.0+"


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


@responses.activate
def test_detail_license_error(foss_server: str, foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) < fossology.versiontuple("1.3.0"):
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.detail_license(shortname)
            assert (
                "Endpoint /license is not supported by your Fossology API version"
                in str(excinfo.value)
            )
    else:
        responses.add(responses.GET, f"{foss_server}/api/v1/license/Blah", status=500)
        with pytest.raises(FossologyApiError) as excinfo:
            foss.detail_license("Blah")
        assert "Error while getting license Blah" in str(excinfo.value)


def test_detail_license_not_found(foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
        with pytest.raises(FossologyApiError) as excinfo:
            foss.detail_license("Unknown")
        assert "License Unknown not found" in str(excinfo.value)


def test_detail_license(foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) < fossology.versiontuple("1.3.0"):
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.detail_license(shortname)
            assert (
                "Endpoint /license is not supported by your Fossology API version"
                in str(excinfo.value)
            )
    else:
        license = foss.detail_license(shortname, group="fossy")
        assert license
        assert type(license) == License


@responses.activate
def test_list_licenses_error(foss_server: str, foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) < fossology.versiontuple("1.3.0"):
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.detail_license(shortname)
            assert (
                "Endpoint /license is not supported by your Fossology API version"
                in str(excinfo.value)
            )
    else:
        responses.add(responses.GET, f"{foss_server}/api/v1/license", status=500)
        with pytest.raises(FossologyApiError) as excinfo:
            foss.list_licenses()
        assert "Unable to retrieve the list of licenses from page 1" in str(
            excinfo.value
        )


def test_get_all_licenses(foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
        licenses, num_pages = foss.list_licenses(active=True, all_pages=True)
        assert licenses
        assert num_pages


def test_get_all_licenses_first_page(foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
        licenses, num_pages = foss.list_licenses()
        assert len(licenses) == 100
        assert num_pages


def test_get_all_candidate_licenses(foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
        licenses, num_pages = foss.list_licenses(kind=LicenseType.CANDIDATE)
        assert not licenses
        assert not num_pages


@responses.activate
def test_add_license_error(
    foss_server: str, foss: fossology.Fossology, test_license: License
):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
        responses.add(responses.POST, f"{foss_server}/api/v1/license", status=500)
        with pytest.raises(FossologyApiError) as excinfo:
            foss.add_license(test_license)
        assert f"Error while adding new license {test_license.shortName}" in str(
            excinfo.value
        )


@responses.activate
def test_add_license_already_exists(
    foss_server: str, foss: fossology.Fossology, monkeypatch, test_license: License,
):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
        mocked_logger = MagicMock()
        monkeypatch.setattr("fossology.license.logger", mocked_logger)
        responses.add(responses.POST, f"{foss_server}/api/v1/license", status=409)
        foss.add_license(test_license)
        mocked_logger.info.assert_called_once()


def test_add_license_and_get_by_shortname(
    foss: fossology.Fossology, test_license: License, monkeypatch
):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
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
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
        responses.add(
            responses.PATCH, f"{foss_server}/api/v1/license/License-1.0", status=500
        )
        with pytest.raises(FossologyApiError) as excinfo:
            foss.update_license(test_license.shortName)
        assert f"Unable to update license {test_license.shortName}" in str(
            excinfo.value
        )


def test_patch_license_and_get_by_shortname(
    foss: fossology.Fossology, test_another_license: License
):
    if fossology.versiontuple(foss.version) >= fossology.versiontuple("1.3.0"):
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
    assert type(json_license) == str


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
