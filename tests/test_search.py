# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import pytest
import responses

from fossology import Fossology
from fossology.obj import SearchTypes
from fossology.exceptions import AuthorizationError, FossologyApiError


def test_search_nogroup(foss: Fossology):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.search(searchType=SearchTypes.ALLFILES, filename="GPL%", group="test")
    assert "Searching for group test not authorized" in str(excinfo.value)


def test_search(foss: Fossology):
    search_result = foss.search(searchType=SearchTypes.ALLFILES, filename="GPL%")
    assert search_result
    search_result = foss.search(
        searchType=SearchTypes.ALLFILES,
        filename="test%",
        tag="test",
        filesizemin="0",
        filesizemax="1024",
        license="Artistic",
        copyright="Debian",
    )
    assert search_result == []


@responses.activate
def test_search_error(foss_server: str, foss: Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/search", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.search()
    assert "Unable to get a result with the given search criteria" in str(excinfo.value)
