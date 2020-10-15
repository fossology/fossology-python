# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import os
import unittest
import mimetypes

from pathlib import Path
from test_base import foss, logger
from test_uploads import get_upload, do_upload
from fossology.exceptions import FossologyApiError
from fossology.obj import ReportFormat


class TestFossologyReport(unittest.TestCase):
    def test_generate_report(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        try:
            report_id = foss.generate_report(
                test_upload, report_format=ReportFormat.SPDX2
            )
        except FossologyApiError as error:
            logger.error(error.message)
            return

        try:
            # Plain text
            report, name = foss.download_report(report_id)
            report_path = Path.cwd() / "tests/files" / name
            with open(report_path, "w+") as report_file:
                report_file.write(report)

            filetype = mimetypes.guess_type(report_path)
            report_stat = os.stat(report_path)
            self.assertGreater(report_stat.st_size, 0, "Downloaded report is empty")
            self.assertIn(
                filetype[0],
                ("application/rdf+xml", "application/xml"),
                "Downloaded report is not a RDF/XML file",
            )
            Path(report_path).unlink()
        except FossologyApiError as error:
            logger.error(error.message)


if __name__ == "__main__":
    unittest.main()
    foss.close()
