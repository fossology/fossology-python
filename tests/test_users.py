# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging
import secrets
from datetime import date, timedelta
from unittest.mock import Mock

import pytest
import requests
import responses

from fossology import Fossology, fossology_token
from fossology.exceptions import AuthenticationError, FossologyApiError

logger = logging.getLogger("fossology-tests")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(name)s: %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)
logging.getLogger("").addHandler(console)


def test_generate_token_wrong_date(foss_server: str):
    with pytest.raises(FossologyApiError) as excinfo:
        fossology_token(
            foss_server,
            "fossy",
            "fossy",
            secrets.token_urlsafe(8),
            token_expire=str(date.today() - timedelta(days=1)),
        )
    assert "Error while generating new token" in str(excinfo.value)


def test_generate_token_too_long(foss_server: str):
    with pytest.raises(FossologyApiError) as excinfo:
        fossology_token(
            foss_server,
            "fossy",
            "fossy",
            secrets.token_urlsafe(41),
            token_expire=str(date.today() + timedelta(days=1)),
        )
    assert "Error while generating new token" in str(excinfo.value)


@responses.activate
def test_generate_token_if_receiving_connection_error_exits(foss_server: str):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v1/tokens",
        body=requests.exceptions.ConnectionError("Test Exception"),
    )
    with pytest.raises(SystemExit) as excinfo:
        fossology_token(
            foss_server,
            "fossy",
            "fossy",
            secrets.token_urlsafe(8),
            token_expire=str(date.today() - timedelta(days=1)),
        )
    assert (
        f"Server {foss_server} does not seem to be running or is unreachable: Test Exception"
        in str(excinfo.value)
    )


@responses.activate
def test_generate_token_if_receiving_authentication_error_raises_api_error_(
    foss_server: str,
):
    responses.add(
        responses.POST,
        f"{foss_server}/api/v1/tokens",
        status=404,
    )
    with pytest.raises(AuthenticationError) as excinfo:
        fossology_token(
            foss_server,
            "fossy",
            "nofossy",
            secrets.token_urlsafe(8),
            token_expire=str(date.today() + timedelta(days=1)),
        )
    assert "Authentication error" in str(excinfo.value)


def test_unknown_user(foss: Fossology):
    with pytest.raises(FossologyApiError):
        foss.detail_user(30)


def test_list_users(foss: Fossology):
    users = foss.list_users()
    assert len(users) == 2
@responses.activate
def test_list_users_v2(foss_server: str, foss_user: dict, foss_user_agents: dict):
    """
    API v2 support test:
    Fossology(version="v2") triggers multiple calls during __init__.
    We must mock everything it touches:
      GET /api/v2/health
      GET /api/v2/info
      GET /api/v2/users/self
      GET /api/v2/folders
      GET /api/v2/folders/{rootFolderId}
    And then the actual call under test:
      GET /api/v2/users
    """
    base = foss_server.rstrip("/")

    health_info = {
        "status": "OK",
        "scheduler": {"status": "OK"},
        "db": {"status": "OK"},
    }

    api_info = {
        "name": "FOSSology API",
        "description": "Mocked API info for tests",
        "version": "v2",
        "security": ["api_key"],
        "contact": "fossology@example.com",
        "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        "fossology": {
            "version": "4.4.0",
            "branchName": "main",
            "commitHash": "deadbeef",
            "commitDate": "2025-01-01T00:00:00Z",
            "buildDate": "2025-01-02T00:00:00Z",
        },
    }

    root_id = foss_user.get("rootFolderId", 1)

    folder_info = {
        "id": root_id,
        "name": "Root",
        "description": "Root folder",
        "parent": 0,
    }

    responses.add(responses.GET, f"{base}/api/v2/health", status=200, json=health_info)
    responses.add(responses.GET, f"{base}/api/v2/info", status=200, json=api_info)
    responses.add(responses.GET, f"{base}/api/v2/users/self", status=200, json=foss_user)

    # ✅ Needed: init calls the folders collection endpoint
    responses.add(
        responses.GET,
        f"{base}/api/v2/folders",
        status=200,
        json=[folder_info],
    )

    # Some versions also call the single folder endpoint
    responses.add(
        responses.GET,
        f"{base}/api/v2/folders/{root_id}",
        status=200,
        json=folder_info,
    )

    responses.add(responses.GET, f"{base}/api/v2/users", status=200, json=[foss_user])

    foss = Fossology(foss_server, "test-token", version="v2")

    users_from_api = foss.list_users()

    assert len(users_from_api) == 1
    assert users_from_api[0].agents.to_dict() == foss_user_agents


@responses.activate
def test_get_self_error(foss_server: str, foss: Fossology):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/users/self",
        status=500,
    )
    with pytest.raises(FossologyApiError):
        foss.get_self()


@responses.activate
def test_get_self_with_agents(
    foss_server: str, foss: Fossology, foss_user: dict, foss_user_agents: dict
):
    responses.add(
        responses.GET, f"{foss_server}/api/v1/users/self", status=200, json=foss_user
    )
    user_from_api = foss.get_self()
    assert user_from_api.agents.to_dict() == foss_user_agents


@responses.activate
def test_detail_user_with_agents(
    foss_server: str, foss: Fossology, foss_user: dict, foss_user_agents: dict
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/users/{foss_user['id']}",
        status=200,
        json=foss_user,
    )
    user_from_api = foss.detail_user(foss_user["id"])
    assert user_from_api.agents.to_dict() == foss_user_agents


@responses.activate
def test_list_users_with_agents(
    foss_server: str, foss: Fossology, foss_user: dict, foss_user_agents: dict
):
    responses.add(
        responses.GET,
        f"{foss_server}/api/v1/users",
        status=200,
        json=[foss_user],
    )
    users_from_api = foss.list_users()
    assert users_from_api[0].agents.to_dict() == foss_user_agents


@responses.activate
def test_list_users_error(foss_server: str, foss: Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/users", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.list_users()
    assert f"Unable to get a list of users from {foss_server}" in str(excinfo.value)


def test_detail_user(foss: Fossology):
    assert foss.detail_user(foss.user.id)
    assert foss.user.email == "y"
    assert (
        f"User {foss.user.description} ({foss.user.id}), y, access level {foss.user.accessLevel}, root folder {foss.user.rootFolderId}"
    ) in str(foss.user)


@responses.activate
def test_delete_user(foss_server: str, foss: Fossology):
    user = Mock(name="Test User", id=secrets.randbelow(1000))
    responses.add(responses.DELETE, f"{foss_server}/api/v1/users/{user.id}", status=202)
    responses.add(responses.DELETE, f"{foss_server}/api/v1/users/{user.id}", status=404)
    assert not foss.delete_user(user)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.delete_user(user)
    assert f"Error while deleting user {user.name} ({user.id})" in str(excinfo.value)
