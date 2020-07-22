# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import time
import pytest
import secrets
import logging

from typing import Dict
from fossology import Fossology, fossology_token
from fossology.obj import Folder, TokenScope, AccessLevel, Agents, Upload
from fossology.exceptions import FossologyApiError, AuthenticationError

logger = logging.getLogger("fossology")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)


@pytest.fixture(scope="session")
def foss_server() -> str:
    return "http://fossology/repo"


@pytest.fixture(scope="session")
def foss_agents() -> Agents:
    additional_agent = {"TestAgent": True}
    return Agents(
        True, True, False, False, True, True, True, False, True, **additional_agent,
    )


@pytest.fixture(scope="session")
def foss_schedule_agents() -> Dict:
    return {
        "analysis": {
            "bucket": True,
            "copyright_email_author": True,
            "ecc": True,
            "keyword": True,
            "monk": True,
            "mime": True,
            "monk": True,
            "nomos": True,
            "ojo": True,
            "package": True,
            "specific_agent": True,
        },
        "decider": {
            "nomos_monk": True,
            "bulk_reused": True,
            "new_scanner": True,
            "ojo_decider": True,
        },
        "reuse": {
            "reuse_upload": 0,
            "reuse_group": 0,
            "reuse_main": True,
            "reuse_enhanced": True,
        },
    }


@pytest.fixture(scope="session")
def foss_token(foss_server: str) -> str:
    return fossology_token(
        foss_server, "fossy", "fossy", secrets.token_urlsafe(8), TokenScope.WRITE
    )


@pytest.fixture(scope="session")
def foss(foss_server: str, foss_token: str, foss_agents: Agents) -> Fossology:
    try:
        foss = Fossology(foss_server, foss_token, "fossy")
    except (FossologyApiError, AuthenticationError) as error:
        exit(error.message)

    # Configure all license agents besides 'ojo'
    foss.user.agents = foss_agents
    yield foss
    foss.close()


@pytest.fixture(scope="session")
def test_file_path() -> str:
    return "tests/files/base-files_11.tar.xz"


@pytest.fixture(scope="session")
def upload_folder(foss: Fossology) -> Folder:
    name = "FossPythonTestUploads"
    desc = "Created via the Fossology Python API"
    folder = foss.create_folder(foss.rootFolder, name, description=desc)
    yield folder
    foss.delete_folder(folder)


@pytest.fixture(scope="session")
def move_folder(foss: Fossology) -> Folder:
    folder = foss.create_folder(
        foss.rootFolder, "MoveUploadTest", "Test move upload function"
    )
    yield folder
    foss.delete_folder(folder)


@pytest.fixture(scope="session")
def upload(foss: Fossology, test_file_path: str) -> Upload:
    test_upload = foss.upload_file(
        foss.rootFolder,
        file=test_file_path,
        description="Test upload via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
    )
    time.sleep(3)
    yield test_upload
    foss.delete_upload(test_upload)


@pytest.fixture(scope="session")
def scanned_upload(
    foss: Fossology, test_file_path: str, foss_schedule_agents: Dict
) -> Upload:
    test_upload = foss.upload_file(
        foss.rootFolder,
        file=test_file_path,
        description="Test upload via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
    )
    time.sleep(3)
    foss.schedule_jobs(foss.rootFolder, test_upload, foss_schedule_agents)
    yield test_upload
    foss.delete_upload(test_upload)
