# mypy: disable-error-code="attr-defined"
# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import logging
import re
import time
from typing import Tuple

from tenacity import TryAgain, retry, retry_if_exception_type, stop_after_attempt

from fossology.enums import ReportFormat
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import Upload

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Report:
    """Class dedicated to all "report" related endpoints"""

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(3))
    def generate_report(
        self,
        upload: Upload,
        report_format: ReportFormat | None = None,
        group: str | None = None,
    ):
        """Generate a report for a given upload

        API Endpoint: GET /report

        :param upload: the upload which report will be generated
        :param format: the report format (default: ReportFormat.READMEOSS)
        :param group: the group name to choose while generating the report (default: None)
        :type upload: Upload
        :type format: ReportFormat
        :type group: string
        :return: the report id
        :rtype: int
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        headers = {"uploadId": str(upload.id)}
        if report_format:
            headers["reportFormat"] = report_format.value
        else:
            headers["reportFormat"] = "readmeoss"
        if group:
            headers["groupName"] = group

        response = self.session.get(f"{self.api}/report", headers=headers)

        if response.status_code == 201:
            report_id = re.search("[0-9]*$", response.json()["message"])
            return report_id[0]  # type: ignore

        elif response.status_code == 403:
            description = f"Report generation for upload {upload.id} not authorized"
            raise AuthorizationError(description, response)

        elif response.status_code == 503:
            wait_time = response.headers["Retry-After"]
            logger.debug(f"Retry generate report after {wait_time} seconds")
            time.sleep(int(wait_time))
            raise TryAgain

        else:
            description = f"Report generation for upload {upload.uploadname} failed"
            raise FossologyApiError(description, response)

    @retry(retry=retry_if_exception_type(TryAgain), stop=stop_after_attempt(10))
    def download_report(
        self, report_id: int, group: str | None = None, wait_time: int = 0
    ) -> Tuple[str, str]:
        """Download a report

        API Endpoint: GET /report/{id}

        Get report for a given upload. If the report is not ready wait another ``wait_time`` seconds or look at
        the ``Retry-After`` to determine how long the wait period shall be.

        If ``wait_time`` is 0, the time interval specified by the ``Retry-After`` header is used.

        The function stops trying after **10 attempts**.

        :Example:

        >>> from fossology import Fossology
        >>>
        >>> foss = Fossology(FOSS_URL, FOSS_TOKEN, username) # doctest: +SKIP
        >>>
        >>> # Generate a report for upload 1
        >>> report_id = foss.generate_report(foss.detail_upload(1)) # doctest: +SKIP
        >>> # Wait up to 20 Minutes until the report is ready
        >>> report_content, report_name = foss.download_report(report_id, wait_time=120) # doctest: +SKIP
        >>> with open(report_name, "wb") as report_file:
        ...     report_file.write(report_content) # doctest: +SKIP

        :param report_id: the id of the generated report
        :param group: the group name to choose while downloading a specific report (default: None)
        :param wait_time: use a customized upload wait time instead of Retry-After (in seconds, default: 0)
        :type report_id: int
        :type group: string
        :type wait_time: int
        :return: the report content and the report name
        :rtype: Tuple[str, str]
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        :raises TryAgain: if the report generation times out after 10 retries
        """
        headers = dict()
        if group:
            headers["groupName"] = group

        response = self.session.get(f"{self.api}/report/{report_id}", headers=headers)

        if response.status_code == 200:
            content = response.headers["Content-Disposition"]
            report_name_pattern = "(^attachment; filename=)(\"|')?([^\"|']*)(\"|'$)?"
            report_name = re.match(report_name_pattern, content).group(3)  # type: ignore
            return response.content, report_name

        elif response.status_code == 403:
            description = f"Download of report {report_id} not authorized"
            raise AuthorizationError(description, response)

        elif response.status_code == 503:
            if not wait_time:
                wait_time = response.headers["Retry-After"]
            logger.debug(
                f"Retry GET report {report_id} after {wait_time} seconds: {response.json()['message']}"
            )
            time.sleep(int(wait_time))
            raise TryAgain

        else:
            description = f"Download of report {report_id} failed"
            raise FossologyApiError(description, response)
