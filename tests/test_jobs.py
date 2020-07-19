# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import pytest

from typing import Dict
from fossology import Fossology
from fossology.obj import Upload
from fossology.exceptions import AuthorizationError


def test_unpack_jobs(foss: Fossology, upload: Upload):
    jobs = foss.list_jobs(upload=upload)
    assert len(jobs) == 1


def test_nogroup_jobs(foss: Fossology, upload: Upload, foss_schedule_agents: Dict):
    # Create jobs for unknown group
    with pytest.raises(AuthorizationError) as excinfo:
        foss.schedule_jobs(foss.rootFolder, upload, foss_schedule_agents, group="test")
    assert "Scheduling job for group test not authorized" in str(excinfo.value)


def test_schedule_jobs(foss: Fossology, upload: Upload, foss_schedule_agents: Dict):
    job = foss.schedule_jobs(foss.rootFolder, upload, foss_schedule_agents)
    assert job.name == upload.uploadname

    jobs = foss.list_jobs(upload=upload)
    assert len(jobs) == 2

    job = foss.detail_job(jobs[1].id, wait=True, timeout=30)
    assert job.status == "Completed"

    # Use pagination
    jobs = foss.list_jobs(upload=upload, page_size=1, page=2)
    assert len(jobs) == 1
    assert jobs[0].id == job.id
