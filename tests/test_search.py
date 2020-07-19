# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import pytest

from fossology import Fossology
from fossology.obj import SearchTypes
from fossology.exceptions import AuthorizationError


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
