# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import pytest
import secrets
import logging

from datetime import date, timedelta
from fossology import Fossology, fossology_token
from fossology.obj import Agents
from fossology.exceptions import FossologyApiError, AuthenticationError

test_files = "tests/files"

logger = logging.getLogger("fossology-tests")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(name)s: %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)
logging.getLogger("").addHandler(console)


def test_generate_token(foss_server: str):
    with pytest.raises(FossologyApiError):
        fossology_token(
            foss_server,
            "fossy",
            "fossy",
            secrets.token_urlsafe(8),
            token_expire=str(date.today() - timedelta(days=1)),
        )


def test_wrong_user(foss_server, foss_token):
    with pytest.raises(AuthenticationError):
        Fossology(foss_server, foss_token, "nofossy")


def test_unknown_user(foss: Fossology):
    with pytest.raises(FossologyApiError):
        foss.detail_user(30)


def test_list_users(foss: Fossology):
    users = foss.list_users()
    assert len(users) == 1


def test_detail_user(foss: Fossology):
    assert foss.detail_user(foss.user.id)
    assert foss.user.email == "y"


def test_user_agents(foss: Fossology, foss_agents: Agents):
    assert foss.user.agents == foss_agents
    analysis_agents = foss.user.agents.to_dict()
    assert analysis_agents.get("TestAgent")
