# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import pytest
import responses

import fossology
from fossology.exceptions import FossologyApiError, FossologyUnsupported
from fossology.obj import License

short = "GPL-2.0+"


@responses.activate
def test_detail_license_error(foss_server: str, foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) < fossology.versiontuple("1.1.3"):
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.detail_license(short)
            assert (
                "Endpoint /license is not supported by your Fossology API version"
                in str(excinfo.value)
            )
    else:
        responses.add(responses.GET, f"{foss_server}/api/v1/license", status=500)
        with pytest.raises(FossologyApiError) as excinfo:
            foss.detail_license(short)
        assert f"Unable to get license {short}" in str(excinfo.value)


def test_detail_license(foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) < fossology.versiontuple("1.1.3"):
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.detail_license(short)
            assert (
                "Endpoint /license is not supported by your Fossology API version"
                in str(excinfo.value)
            )
    else:
        license = foss.detail_license(short)
        assert license
        assert type(license) == License
