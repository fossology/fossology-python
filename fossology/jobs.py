# mypy: disable-error-code="attr-defined"
# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import json
import logging
import time
from typing import Optional

from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Folder, Job, ShowJob, Upload

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Jobs:
    """Class dedicated to all "jobs" related endpoints"""

    def list_jobs(
        self,
        upload: Optional[Upload] = None,
        all: bool = False,
        page_size: int = 100,
        page: int = 1,
        all_pages: bool = False,
    ) -> tuple[list[Job], int]:
        """Get all jobs created by the logged in user

        API Endpoint: GET /jobs

        The answer is limited to the first page of 20 results by default

        :param upload: list only jobs of the given upload (default: None)
        :param all: list all jobs created by all users, only available for admins (default: False)
        :param page_size: the maximum number of results per page (default: 100)
        :param page: the number of pages to be retrieved (default: 1)
        :param all_pages: get all jobs (default: False)
        :type upload: Upload
        :type all: boolean
        :type page_size: int
        :type page: int
        :type all_pages: boolean
        :return: a tuple containing the list of jobs and the total number of pages
        :rtype: Tuple(list of Job, int)
        :raises FossologyApiError: if the REST call failed
        """
        params = {}
        headers = {"limit": str(page_size)}
        if upload:
            params["upload"] = upload.id

        jobs_list = list()
        jobs_endpoint = f"{self.api}/jobs"
        if all:
            jobs_endpoint += "/all"
        if all_pages:
            # will be reset after the total number of pages has been retrieved from the API
            x_total_pages = 2
        else:
            x_total_pages = page
        while page <= x_total_pages:
            headers["page"] = str(page)
            response = self.session.get(jobs_endpoint, params=params, headers=headers)
            if response.status_code == 200:
                for job in response.json():
                    jobs_list.append(Job.from_json(job))
                x_total_pages = int(response.headers.get("X-TOTAL-PAGES", 0))
                if not all_pages or x_total_pages == 0:
                    logger.info(
                        f"Retrieved page {page} of jobs, {x_total_pages} pages are in total available"
                    )
                    return jobs_list, x_total_pages
                page += 1
            elif response.status_code == 403:
                description = "Access denied to /jobs/all endpoint"
                raise FossologyApiError(description, response)
            else:
                description = f"Unable to retrieve the list of jobs from page {page}"
                raise FossologyApiError(description, response)
        logger.info(f"Retrieved all {x_total_pages} pages of jobs")
        return jobs_list, x_total_pages

    def detail_job(self, job_id: int, wait: bool = False, timeout: int = 10) -> Job:
        """Get detailed information about a job

        API Endpoint: GET /jobs/{id}

        :param job_id: the id of the job
        :param wait: wait until the job is finished (default: False)
        :param timeout: stop waiting after x seconds (default: 10)
        :type: int
        :type wait: boolean
        :type timeout: 10
        :return: the job data
        :rtype: Job
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/jobs/{job_id}")
        if wait:
            if response.status_code == 200:
                job = Job.from_json(response.json())
                if job.status == "Completed":
                    logger.debug(f"Job {job_id} has completed")
                    return job
            else:
                description = f"Error while getting details for job {job_id}"
                raise FossologyApiError(description, response)
            logger.debug(f"Waiting for job {job_id} to complete")
            time.sleep(timeout)
            response = self.session.get(f"{self.api}/jobs/{job_id}")

        if response.status_code == 200:
            logger.debug(f"Got details for job {job_id}")
            return Job.from_json(response.json())
        else:
            description = f"Error while getting details for job {job_id}"
            raise FossologyApiError(description, response)

    def jobs_history(self, upload: Upload) -> list[Job]:
        """Return jobs for the given upload id

        API Endpoint: GET /jobs/history

        :param upload_id: the id of the upload
        :type upload_id: int
        :return: the list of all the jobs scheduled for the upload
        :rtype: list of ShowJob
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(f"{self.api}/jobs/history?upload={upload.id}")
        jobs_list = list()
        if response.status_code == 200:
            logger.debug(f"Got jobs for upload {upload.id}")
            for job in response.json():
                jobs_list.append(ShowJob.from_json(job))
            return jobs_list
        elif response.status_code in [403, 404]:
            description = f"Upload {upload.id} is not accessible or does not exists"
            raise FossologyApiError(description, response)
        else:
            description = f"Error while getting jobs history for upload {upload.id}"
            raise FossologyApiError(description, response)

    def schedule_jobs(
        self,
        folder: Folder,
        upload: Upload,
        spec: dict,
        group: str | None = None,
        wait: bool = False,
        timeout: int = 10,
    ) -> Job:
        """Schedule jobs for a specific upload

        API Endpoint: POST /jobs

        Job specifications `spec` are added to the request body,
        following options are available:

        >>> job_spec = {
        ...     "analysis": {
        ...         "bucket": True,
        ...         "copyright_email_author": True,
        ...         "ecc": True,
        ...         "keyword": True,
        ...         "monk": True,
        ...         "mime": True,
        ...         "monk": True,
        ...         "nomos": True,
        ...         "ojo": True,
        ...         "package": True,
        ...         "specific_agent": True,
        ...     },
        ...     "decider": {
        ...         "nomos_monk": True,
        ...         "bulk_reused": True,
        ...         "new_scanner": True,
        ...         "ojo_decider": True
        ...     },
        ...     "reuse": {
        ...         "reuse_upload": 0,
        ...         "reuse_group": 0,
        ...         "reuse_main": True,
        ...         "reuse_enhanced": True,
        ...         "reuse_report": True,
        ...         "reuse_copyright": True,
        ...     }
        ... }

        :param folder: the upload folder
        :param upload: the upload for which jobs will be scheduled
        :param spec: the job specification
        :param group: the group name to choose while scheduling jobs (default: None)
        :param wait: wait for the scheduled job to finish (default: False)
        :param timeout: stop waiting after x seconds (default: 10)
        :type upload: Upload
        :type folder: Folder
        :type spec: dict
        :type group: string
        :type wait: boolean
        :type timeout: 10
        :return: the job id
        :rtype: Job
        :raises FossologyApiError: if the REST call failed
        """
        headers = {
            "folderId": str(folder.id),
            "uploadId": str(upload.id),
            "Content-Type": "application/json",
        }
        if group:
            headers["groupName"] = group

        response = self.session.post(
            f"{self.api}/jobs", headers=headers, data=json.dumps(spec)
        )

        if response.status_code == 201:
            detailled_job = self.detail_job(
                response.json()["message"], wait=wait, timeout=timeout
            )
            return detailled_job

        elif response.status_code == 403:
            description = "Scheduling job not authorized"
            raise AuthorizationError(description, response)

        else:
            description = f"Scheduling jobs for upload {upload.uploadname} failed"
            raise FossologyApiError(description, response)
