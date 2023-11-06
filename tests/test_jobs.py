# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import secrets
from typing import Dict
from unittest.mock import Mock

import pytest
import responses

from fossology import Fossology
from fossology.enums import JobStatus
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Upload


def test_unpack_jobs(foss: Fossology, upload: Upload):
    jobs, _ = foss.list_jobs(upload=upload)
    assert len(jobs) == 1


def test_nogroup_jobs(foss: Fossology, upload: Upload, foss_schedule_agents: Dict):
    # Create jobs for unknown group
    with pytest.raises(AuthorizationError) as excinfo:
        foss.schedule_jobs(foss.rootFolder, upload, foss_schedule_agents, group="test")
    assert "Scheduling job not authorized" in str(excinfo.value)


def test_schedule_jobs(
    foss: Fossology, upload_with_jobs: Upload, foss_schedule_agents: Dict
):
    job = foss.schedule_jobs(foss.rootFolder, upload_with_jobs, foss_schedule_agents)
    assert job.name == upload_with_jobs.uploadname

    jobs, _ = foss.list_jobs(upload=upload_with_jobs)
    assert len(jobs) == 3

    job = foss.detail_job(jobs[1].id, wait=True, timeout=30)
    assert job.status == JobStatus.COMPLETED.value
    assert (
        f"Job '{job.name}' ({job.id}) queued on {job.queueDate} (Status: {job.status} ETA: {job.eta})"
        in str(job)
    )

    # Use pagination
    jobs, _ = foss.list_jobs(upload=upload_with_jobs, page_size=1, page=2)
    assert len(jobs) == 1
    assert jobs[0].id == job.id


def test_detail_job_wait_completed(
    foss: Fossology, upload_with_jobs: Upload, monkeypatch: pytest.MonkeyPatch
):
    mocked_logger = Mock()
    monkeypatch.setattr("fossology.jobs.logger", mocked_logger)
    jobs, _ = foss.list_jobs(upload=upload_with_jobs)
    job = foss.detail_job(jobs[0].id, wait=10)
    assert job.status == "Completed"
    mocked_logger.debug.assert_called_once_with((f"Job {job.id} has completed"))


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
    assert "Unable to retrieve the list of jobs from page 1" in str(excinfo.value)


@responses.activate
def test_list_all_jobs_access_denied(foss_server: str, foss: Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/jobs/all", status=403)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.list_jobs(all=True)
    assert "Access denied to /jobs/all endpoint" in str(excinfo.value)


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


def test_paginated_list_jobs(foss: Fossology, upload_with_jobs: Upload):
    jobs, total_pages = foss.list_jobs(
        upload=upload_with_jobs, page_size=1, all_pages=True
    )
    assert len(jobs) == 3
    assert total_pages == 3

    jobs, total_pages = foss.list_jobs(upload=upload_with_jobs, page_size=1, page=1)
    assert len(jobs) == 1
    assert total_pages == 3

    jobs, total_pages = foss.list_jobs(upload=upload_with_jobs, page_size=1, page=2)
    assert len(jobs) == 1
    assert total_pages == 3

    jobs, total_pages = foss.list_jobs(upload=upload_with_jobs, page_size=2, page=1)
    assert len(jobs) == 2
    assert total_pages == 2
