# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import logging
import os
import secrets
import time
from typing import Dict, Generator

import pytest
from click.testing import CliRunner

import fossology
from fossology.exceptions import AuthenticationError, FossologyApiError
from fossology.obj import AccessLevel, Agents, JobStatus, TokenScope, Upload

logger = logging.getLogger("fossology")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)


def jobs_lookup(foss: fossology.Fossology, upload: Upload):
    for job in foss.list_jobs(upload=upload)[0]:
        if job.status == JobStatus.FAILED.value:
            logger.debug(f"Job {job.name} failed to complete, checking next job")
            continue
        while job.status != JobStatus.COMPLETED.value:
            logger.debug(
                f"Waiting for job {job.name} with status {job.status} to complete (eta: {job.eta})"
            )
            job = foss.detail_job(job.id)
            time.sleep(5)


@pytest.fixture(scope="session")
def foss_server() -> str:
    return "http://fossology/repo"


@pytest.fixture(scope="session")
def foss_agents() -> Agents:
    additional_agent = {"TestAgent": True}
    return Agents(
        True,
        True,
        False,
        False,
        True,
        True,
        True,
        False,
        True,
        **additional_agent,
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
            "reuse_report": True,
            "reuse_copyright": True,
        },
    }


@pytest.fixture(scope="session")
def foss_user_agents() -> Dict:
    return {
        "bucket": True,
        "copyright_email_author": True,
        "ecc": True,
        "keyword": True,
        "mimetype": False,
        "monk": True,
        "mime": True,
        "monk": True,
        "nomos": True,
        "ojo": True,
        "package": True,
        "specific_agent": True,
    }


@pytest.fixture(scope="session")
def foss_user(foss_user_agents) -> Dict:
    return {
        "id": secrets.randbelow(1000),
        "name": "Test User",
        "description": "",
        "email": "test.user@example.com",
        "accessLevel": "read_write",
        "rootFolderId": 1,
        "emailNotification": "y",
        "agents": foss_user_agents,
    }


@pytest.fixture(scope="session")
def foss_token(foss_server: str) -> str:
    return fossology.fossology_token(
        foss_server, "fossy", "fossy", secrets.token_urlsafe(8), TokenScope.WRITE
    )


@pytest.fixture(scope="session")
def foss(foss_server: str, foss_token: str, foss_agents: Agents) -> fossology.Fossology:
    try:
        foss = fossology.Fossology(foss_server, foss_token, "fossy")
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
def upload_folder(foss: fossology.Fossology) -> Generator:
    name = "UploadFolderTest"
    desc = "Created via the Fossology Python API"
    folder = foss.create_folder(foss.rootFolder, name, description=desc)
    yield folder
    foss.delete_folder(folder)


@pytest.fixture(scope="session")
def move_folder(foss: fossology.Fossology) -> Generator:
    folder = foss.create_folder(
        foss.rootFolder, "MoveUploadTest", "Test move upload function"
    )
    yield folder
    foss.delete_folder(folder)


@pytest.fixture(scope="session")
def upload(
    foss: fossology.Fossology,
    test_file_path: str,
) -> Generator:
    upload = foss.upload_file(
        foss.rootFolder,
        file=test_file_path,
        description="Test upload via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
        wait_time=5,
    )
    jobs_lookup(foss, upload)
    yield upload
    foss.delete_upload(upload)
    time.sleep(5)


@pytest.fixture(scope="session")
def upload_with_jobs(
    foss: fossology.Fossology, test_file_path: str, foss_schedule_agents: dict
) -> Generator:
    upload = foss.upload_file(
        foss.rootFolder,
        file=test_file_path,
        description="Test upload_with_jobs via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
        wait_time=5,
    )
    jobs_lookup(foss, upload)
    foss.schedule_jobs(foss.rootFolder, upload, foss_schedule_agents)
    jobs_lookup(foss, upload)
    yield upload
    foss.delete_upload(upload)
    time.sleep(5)


@pytest.fixture(scope="session")
def created_foss_user(foss: fossology.Fossology, foss_user: dict) -> Generator:
    foss.create_user(foss_user)
    for user in foss.list_users():
        if user.name == foss_user["name"]:
            yield user
    foss.delete_user(user)


# foss_cli specific
@pytest.fixture(scope="session")
def click_test_file_path() -> str:
    return "tests/files"


@pytest.fixture(scope="session")
def click_test_file() -> str:
    return "zlib_1.2.11.dfsg-0ubuntu2.debian.tar.xz"


@pytest.fixture(scope="session")
def click_test_dict(foss_server) -> dict:
    d = dict()
    d["IS_REQUEST_FOR_HELP"] = False
    d["IS_REQUEST_FOR_CONFIG"] = False
    d["SERVER"] = foss_server
    d["USERNAME"] = "fossy"
    return d


@pytest.fixture(scope="session")
def runner(foss_token: str):
    os.environ["FOSS_TOKEN"] = foss_token
    the_runner = CliRunner()
    yield the_runner
    # cleanup
