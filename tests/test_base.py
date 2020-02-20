# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import secrets
import logging

from fossology import Fossology, fossology_token
from fossology.obj import TokenScope
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
