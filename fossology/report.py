# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import re
import time
import logging

from .exceptions import FossologyApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Report:
    """Class dedicated to all "report" related endpoints"""

    def generate_report(self, upload, Format=None):
        """Generate a report for a given upload

        API Endpoint: GET /report

        :param upload: the upload which report will be generated
        :param Format: the report format
        :type upload: Upload
        :type Format: ReportFormat
        :return: the report download url
        :rtype: list of Job
        :raises FossologyApiError: if the REST call failed
        """
        headers = {"uploadId": str(upload.id)}
        if Format:
            headers["reportFormat"] = Format.value
        else:
            headers["reportFormat"] = "readmeoss"

        response = self.session.get(self.api + "/report", headers=headers)
        if response.status_code == 201:
            report_id = re.search("[0-9]*$", response.json()["message"])
            return report_id[0]
        else:
            description = "Report generation for upload {upload.name} failed"
            raise FossologyApiError(description, response)

    def download_report(self, report_id, as_zip=False):
        """Download a report

        API Endpoint: GET /report/{id}

        FIXME: Accept header "application/zip" does not work in version 1.0.6

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
        while True:
            response = self.session.get(
                self.api + f"/report/{report_id}", headers=headers
            )
            if response.status_code == 200:
                return response.text
            elif response.status_code == 503:
                logger.debug(
                    f"Retry download in {response.headers['Retry-After']} seconds"
                )
                time.sleep(int(response.headers["Retry-After"]))
            else:
                description = "Download of report {report_id} failed"
                raise FossologyApiError(description, response)
                return None
