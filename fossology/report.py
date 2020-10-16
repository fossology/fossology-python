# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import re
import time
import logging
from typing import Tuple

from tenacity import retry, TryAgain, stop_after_attempt, retry_if_exception_type
from .obj import ReportFormat, Upload
from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Report:
    """Class dedicated to all "report" related endpoints"""

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def generate_report(self, upload: Upload, report_format: ReportFormat = None):
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
            description = f"Report generation for upload {upload.uploadname} failed"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def download_report(self, report_id: int) -> Tuple[str, str]:
        """Download a report

        API Endpoint: GET /report/{id}

        :Example:

        >>> from fossology.api import Fossology
        >>>
        >>> foss = Fossology(FOSS_URL, FOSS_TOKEN, username)
        >>>
        >>> # Generate a report for upload 1
        >>> report_id = foss.generate_report(foss.detail_upload(1))
        >>> report_content, report_name = foss.download_report(report_id)
        >>> with open(report_name, "w+") as report_file:
        >>>     report_file.write(report_content)

        :param report_id: the id of the generated report
        :type report_id: int
        :return: the report content and the report name
        :rtype: Tuple[str, str]
        :raises FossologyApiError: if the REST call failed
        :raises TryAgain: if the report generation timed out after 3 retries
        """
        response = self.session.get(f"{self.api}/report/{report_id}")
        if response.status_code == 200:
            content = response.headers["Content-Disposition"]
            report_name_pattern = '(^attachment; filename=")(.*)("$)'
            report_name = re.match(report_name_pattern, content).group(2)
            return response.text, report_name
        elif response.status_code == 503:
            wait_time = response.headers["Retry-After"]
            logger.debug(f"Retry get report after {wait_time} seconds")
            time.sleep(int(wait_time))
            raise TryAgain
        else:
            description = f"Download of report {report_id} failed"
            raise FossologyApiError(description, response)
