# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import secrets
from typing import Dict

import pytest
import responses

from fossology import Fossology
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Upload


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
    assert (
        f"Job '{job.name}' ({job.id}) queued on {job.queueDate} (Status: {job.status} ETA: {job.eta})"
        in str(job)
    )

    # Use pagination
    jobs = foss.list_jobs(upload=upload, page_size=1, page=2)
    assert len(jobs) == 1
    assert jobs[0].id == job.id


@responses.activate
def test_schedule_job_error(foss_server: str, foss: Fossology, upload: Upload):
    responses.add(responses.POST, f"{foss_server}/api/v1/jobs", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.schedule_jobs(foss.rootFolder, upload, {})
    assert f"Scheduling jobs for upload {upload.uploadname} failed" in str(
        excinfo.value
    )


@responses.activate
def test_list_jobs_error(foss_server: str, foss: Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/jobs", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.list_jobs()
    assert "Getting the list of jobs failed" in str(excinfo.value)


@responses.activate
def test_detail_job_error(foss_server: str, foss: Fossology):
    job_id = secrets.randbelow(1000)
    responses.add(responses.GET, f"{foss_server}/api/v1/jobs/{job_id}", status=404)
    responses.add(responses.GET, f"{foss_server}/api/v1/jobs/{job_id}", status=404)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.detail_job(job_id, wait=True)
    assert f"Error while getting details for job {job_id}" in str(excinfo.value)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.detail_job(job_id)
    assert f"Error while getting details for job {job_id}" in str(excinfo.value)
