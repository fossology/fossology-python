# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging

from .obj import Job
from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Jobs:
    def list_jobs(self, page_size=20, pages=1):
        """Get all available jobs

        API Endpoint: GET /jobs

        The answer is limited to the first page of 20 results by default

        :param page_size: the maximum number of results per page
        :param pages: the number of pages to be retrieved
        :type page_size: int (default to "20")
        :type pages: int (default to "1")
        :return: the jobs data - or None if the REST call failed
        :rtype: list() of Job objects
        """
        headers = {"limit": str(page_size), "pages": str(pages)}
        try:
            response = self.session.get(self.api + "/jobs", headers=headers)
            if response.status_code == 200:
                jobs_list = list()
                for job in response.json():
                    jobs_list.append(Job.from_json(job))
                return jobs_list
            else:
                description = "Getting the list of jobs failed"
                raise FossologyApiError(description, response)
        except FossologyApiError as error:
            logger.error(error.message)
            return None
