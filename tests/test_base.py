# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import secrets
import logging
import unittest

from datetime import date, timedelta
from fossology import Fossology, fossology_token
from fossology.obj import TokenScope, Agents
from fossology.exceptions import FossologyApiError, AuthenticationError

test_files = "tests/files"

logger = logging.getLogger("fossology-tests")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(name)s: %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)
logging.getLogger("").addHandler(console)


def generate_fossology_token(server):
    try:
        return fossology_token(
            server, "fossy", "fossy", secrets.token_urlsafe(8), TokenScope.WRITE
        )
    except (FossologyApiError, AuthenticationError) as error:
        exit(error.message)


# Get API handler
try:
    FOSSOLOGY_SERVER = "http://fossology/repo"
    FOSSOLOGY_TOKEN = generate_fossology_token(FOSSOLOGY_SERVER)
    foss = Fossology(FOSSOLOGY_SERVER, FOSSOLOGY_TOKEN, "fossy")
except (FossologyApiError, AuthenticationError) as error:
    exit(error.message)


class TestFossologyToken(unittest.TestCase):
    def test_generate_token(self):
        self.assertRaises(
            FossologyApiError,
            fossology_token,
            FOSSOLOGY_SERVER,
            "fossy",
            "fossy",
            secrets.token_urlsafe(8),
            token_expire=str(date.today() - timedelta(days=1)),
        )


class TestFossologyUser(unittest.TestCase):
    def test_get_user(self):
        self.assertRaises(
            AuthenticationError, Fossology, FOSSOLOGY_SERVER, FOSSOLOGY_TOKEN, "nofossy"
        )
        self.assertRaises(FossologyApiError, foss.detail_user, 30)

        foss.detail_user(foss.user.id)
        self.assertEqual(foss.user.email, "fossy", "Wrong email set for default user")

        additional_agent = {"TestAgent": True}
        agents = Agents(
            True, True, False, False, True, True, True, True, True, **additional_agent,
        )
        foss.user.agents = agents
        analysis_agents = foss.user.agents.to_dict()
        self.assertEqual(
            analysis_agents.get("TestAgent"),
            True,
            "Specific agent could not be configured for Fossology instance",
        )

        foss.detail_user(foss.user.id)
        self.assertEqual(
            foss.user.agents, agents, "Wrong agents configured for default user"
        )

        users = foss.list_users()
        self.assertEqual(len(users), 1, "Wrong number of users on the test server")
