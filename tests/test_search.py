# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import secrets

import pytest
import responses

from fossology import Fossology, versiontuple
from fossology.exceptions import (
    AuthorizationError,
    FossologyApiError,
    FossologyUnsupported,
)
from fossology.obj import SearchTypes, Upload


def test_search_nogroup(foss: Fossology):
    with pytest.raises(AuthorizationError) as excinfo:
        foss.search(searchType=SearchTypes.ALLFILES, filename="GPL%", group="test")
    assert "Searching for group test not authorized" in str(excinfo.value)


def test_search(foss: Fossology, upload):
    search_result = foss.search(searchType=SearchTypes.ALLFILES, filename="GPL%")
    assert search_result


def test_search_nothing_found(foss: Fossology, upload):
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


def test_search_directory(foss: Fossology, upload):
    search_result = foss.search(searchType=SearchTypes.DIRECTORIES, filename="share",)
    assert search_result


def test_search_upload(foss: Fossology, upload):
    search_result = foss.search(
        searchType=SearchTypes.ALLFILES, upload=upload, filename="share",
    )
    assert search_result


def test_search_upload_does_not_exist(foss: Fossology):
    # Before 1.0.17 Fossology was not able to limit search to a specific upload
    if versiontuple(foss.version) > versiontuple("1.0.16"):
        hash = {"sha1": "", "md5": "", "sha256": "", "size": ""}
        fake_upload = Upload(
            secrets.randbelow(1000),
            "fake_folder",
            secrets.randbelow(1000),
            "",
            "fake_upload",
            "2020-12-30",
            hash=hash,
        )
        search_result = foss.search(
            searchType=SearchTypes.ALLFILES, upload=fake_upload, filename="share",
        )
        assert not search_result


@responses.activate
def test_search_error(foss_server: str, foss: Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/search", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.search()
    assert "Unable to get a result with the given search criteria" in str(excinfo.value)


def test_filesearch(foss: Fossology, scanned_upload: Upload):
    if versiontuple(foss.version) > versiontuple("1.0.16"):
        filelist = [
            {"md5": "F921793D03CC6D63EC4B15E9BE8FD3F8"},
            {"sha1": scanned_upload.hash.sha1},
        ]
        search_result = foss.filesearch(filelist=filelist)
        assert len(search_result) == 2
        assert (
            f"File with SHA1 {scanned_upload.hash.sha1} doesn't have any concluded license yet"
            in str(search_result[1])
        )

        filelist = [{"sha1": "FAKE"}]
        result = foss.filesearch(filelist=filelist)
        assert result == "Unable to get a result with the given filesearch criteria"
        assert foss.filesearch() == []
    else:
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.filesearch(filelist=[], group="test")
            assert (
                "Endpoint /filesearch is not supported by your Fossology API version"
                in str(excinfo.value)
            )


def test_filesearch_nogroup(foss: Fossology):
    if versiontuple(foss.version) > versiontuple("1.0.16"):
        with pytest.raises(AuthorizationError) as excinfo:
            foss.filesearch(filelist=[], group="test")
        assert "Searching for group test not authorized" in str(excinfo.value)
    else:
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.filesearch(filelist=[], group="test")
            assert (
                "Endpoint /filesearch is not supported by your Fossology API version"
                in str(excinfo.value)
            )


@responses.activate
def test_filesearch_error(foss_server: str, foss: Fossology):
    responses.add(responses.POST, f"{foss_server}/api/v1/filesearch", status=404)
    if versiontuple(foss.version) > versiontuple("1.0.16"):
        with pytest.raises(FossologyApiError) as excinfo:
            foss.filesearch()
        assert "Unable to get a result with the given filesearch criteria" in str(
            excinfo.value
        )
    else:
        with pytest.raises(FossologyUnsupported) as excinfo:
            foss.filesearch(filelist=[], group="test")
            assert (
                "Endpoint /filesearch is not supported by your Fossology API version"
                in str(excinfo.value)
            )
