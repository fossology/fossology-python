# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import secrets

import pytest
import responses

import fossology
from fossology.exceptions import FossologyApiError, FossologyUnsupported
from fossology.obj import Group


@responses.activate
def test_list_groups_error(foss_server: str, foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) < fossology.versiontuple("1.2.1"):
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.list_groups()
            assert (
                "Endpoint /groups is not supported by your Fossology API version"
                in str(excinfo.value)
            )
    else:
        responses.add(responses.GET, f"{foss_server}/api/v1/groups", status=500)
        with pytest.raises(FossologyApiError) as excinfo:
            foss.list_groups()
        assert f"Unable to get a list of groups for {foss.user.name}" in str(
            excinfo.value
        )


def test_create_group(foss: fossology.Fossology):
    if fossology.versiontuple(foss.version) < fossology.versiontuple("1.2.1"):
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.create_group("FossGroupTest")
            assert (
                "Endpoint /groups is not supported by your Fossology API version"
                in str(excinfo.value)
            )
    else:
        name = secrets.token_urlsafe(8)
        foss.create_group(name)
        groups = foss.list_groups()
        assert groups
        assert type(groups[0]) == Group

        # Recreate group to test API response 400
        with pytest.raises(FossologyApiError) as excinfo:
            foss.create_group(name)
        assert (
            f"Group {name} already exists, failed to create group or no group name provided"
            in str(excinfo.value)
        )
