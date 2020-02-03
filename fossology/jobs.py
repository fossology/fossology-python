# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import json
import logging

from .obj import Job
from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Jobs:
    """Class dedicated to all "jobs" related endpoints"""

    def list_jobs(self, page_size=20, pages=1):
        """Get all available jobs

        API Endpoint: GET /jobs

        The answer is limited to the first page of 20 results by default

        :param page_size: the maximum number of results per page
        :param pages: the number of pages to be retrieved
        :type page_size: int (default to "20")
        :type pages: int (default to "1")
        :return: the jobs data
        :rtype: list of Job
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"limit": str(page_size), "pages": str(pages)}
        response = self.session.get(self.api + "/jobs", headers=headers)
        if response.status_code == 200:
            jobs_list = list()
            for job in response.json():
                jobs_list.append(Job.from_json(job))
            return jobs_list
        else:
            description = "Getting the list of jobs failed"
            raise FossologyApiError(description, response)

    def detail_job(self, job_id):
        """Get detailled information about a job

        API Endpoint: GET /jobs/{id}

        :param job_id: the id of the job
        :type: int
        :return: the job data
        :rtype: Job
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(self.api + f"/jobs/{job_id}")
        if response.status_code == 200 and response.json():
            logger.debug(f"Got details for job {job_id}")
            return Job.from_json(response.json())
        else:
            if response.json():
                description = f"Error while getting details for job {job_id}"
                raise FossologyApiError(description, response)
            else:
                logger.error(f"Missing response from API: {response.text}")
                return None

    def schedule_jobs(self, folder, upload, spec):
        """Schedule jobs for a specific upload

        API Endpoint: POST /jobs

        Job specifications `spec` are added to the request body,
        following options are available:

        >>> {
        >>>     "analysis": {
        >>>         "bucket": True,
        >>>         "copyright_email_author": True,
        >>>         "ecc": True,
        >>>         "keyword": True,
        >>>         "monk": True,
        >>>         "mime": True,
        >>>         "monk": True,
        >>>         "nomos": True,
        >>>         "ojo": True,
        >>>         "package": True
        >>>     },
        >>>     "decider": {
        >>>         "nomos_monk": True,
        >>>         "bulk_reused": True,
        >>>         "new_scanner": True,
        >>>         "ojo_decider": True
        >>>     },
        >>>     "reuse": {
        >>>         "reuse_upload": 0,
        >>>         "reuse_group": 0,
        >>>         "reuse_main": True,
        >>>         "reuse_enhanced": True
        >>>     }
        >>> }

        :param folder: the upload folder
        :param upload: the upload for which jobs will be scheduled
        :param spec: the job specification
        :type upload: Upload
        :type folder: Folder
        :type spec: dict
        :return: the job id
        :rtype: Job
        :raises FossologyApiError: if the REST call failed
        """
        headers = {
            "folderId": str(folder.id),
            "uploadId": str(upload.id),
            "Content-Type": "application/json",
        }
        response = self.session.post(
            self.api + "/jobs", headers=headers, data=json.dumps(spec)
        )
        if response.status_code == 201:
            detailled_job = self.detail_job(response.json()["message"])
            return detailled_job
        else:
            description = "Scheduling jobs for upload {upload.uploadname} failed"
            raise FossologyApiError(description, response)
