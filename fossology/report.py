# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import re
import time
import logging

from tenacity import retry, TryAgain, stop_after_attempt, retry_if_exception_type
from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Report:
    """Class dedicated to all "report" related endpoints"""

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def generate_report(self, upload, report_format=None):
        """Generate a report for a given upload

        API Endpoint: GET /report

        :param upload: the upload which report will be generated
        :param format: the report format (default ReportFormat.READMEOSS)
        :type upload: Upload
        :type format: ReportFormat
        :return: the report id
        :rtype: int
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"uploadId": str(upload.id)}
        if report_format:
            headers["reportFormat"] = report_format.value
        else:
            headers["reportFormat"] = "readmeoss"

        response = self.session.get(f"{self.api}/report", headers=headers)
        if response.status_code == 201:
            report_id = re.search("[0-9]*$", response.json()["message"])
            return report_id[0]
        elif response.status_code == 503:
            wait_time = response.headers["Retry-After"]
            logger.debug(f"Retry generate report after {wait_time} seconds")
            time.sleep(int(wait_time))
            raise TryAgain
        else:
            description = f"Report generation for upload {upload.name} failed"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def download_report(self, report_id, as_zip=False):
        """Download a report

        API Endpoint: GET /report/{id}

        :Example:

        >>> from fossology.api import Fossology
        >>>
        >>> foss = Fossology(FOSS_URL, FOSS_TOKEN, username)
        >>>
        >>> # Generate a report for upload 1
        >>> report_id = foss.generate_report(foss.detail_upload(1))
        >>> report_content = foss.download_report(report_id, as_zip=True)
        >>> with open(filename, "w+") as report_file:
        >>>     report_file.write(report_content)

        :param report_id: the id of the generated report
        :param as_zip: control if the report should be generated as ZIP file (default False)
        :type report_id: int
        :type as_zip: boolean
        :raises FossologyApiError: if the REST call failed
        """
        if as_zip:
            headers = {"Accept": "application/zip"}
        else:
            headers = {"Accept": "text/plain"}

        response = self.session.get(f"{self.api}/report/{report_id}", headers=headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 503:
            wait_time = response.headers["Retry-After"]
            logger.debug(f"Retry get report after {wait_time} seconds")
            time.sleep(int(wait_time))
            raise TryAgain
        else:
            description = "Download of report {report_id} failed"
            raise FossologyApiError(description, response)
