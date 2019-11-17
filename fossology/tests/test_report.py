# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import os
import unittest

from test_base import foss, logger
from test_uploads import get_upload, do_upload, upload_filename
from fossology.exceptions import FossologyApiError
from fossology.obj import ReportFormat

from pathlib import Path


class TestFossologyReport(unittest.TestCase):
    def test_generate_report(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        try:
            report_id = foss.generate_report(test_upload, Format=ReportFormat.SPDX2)
        except FossologyApiError as error:
            logger.error(error.message)

        try:
            # Plain text
            report = foss.download_report(report_id)
            report_path = Path.cwd() / "fossology/tests/files"
            report_name = upload_filename + ".spdx-report.rdf"
            with open(report_path / report_name, "w+") as report_file:
                report_file.write(report)

            report_stat = os.stat(report_path / report_name)
            self.assertGreater(report_stat.st_size, 0, "Downloaded report is empty")
        except FossologyApiError as error:
            logger.error(error.message)


if __name__ == "__main__":
    unittest.main()
    foss.close()
