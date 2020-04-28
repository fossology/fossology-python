# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import os
import unittest
import mimetypes

from pathlib import Path
from test_base import foss, logger
from test_uploads import get_upload, do_upload, upload_filename
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

        try:
            # Plain text
            report = foss.download_report(report_id)
            report_path = Path.cwd() / "tests/files"
            report_name = upload_filename + ".spdx-report.rdf"
            with open(report_path / report_name, "w+") as report_file:
                report_file.write(report)

            filetype = mimetypes.guess_type(report_path / report_name)
            report_stat = os.stat(report_path / report_name)
            self.assertGreater(report_stat.st_size, 0, "Downloaded report is empty")
            self.assertIn(
                filetype[0],
                ("application/rdf+xml", "application/xml"),
                "Downloaded report is not a RDF/XML file",
            )
            Path(report_path / report_name).unlink()
        except FossologyApiError as error:
            logger.error(error.message)

        try:
            # Zip
            report = foss.download_report(report_id, as_zip=True)
            report_path = Path.cwd() / "tests/files"
            report_name = upload_filename + ".spdx-report.rdf.zip"
            with open(report_path / report_name, "w+") as report_file:
                report_file.write(report)

            filetype = mimetypes.guess_type(report_path / report_name)
            report_stat = os.stat(report_path / report_name)
            self.assertGreater(report_stat.st_size, 0, "Downloaded report is empty")
            self.assertEqual(
                filetype[0], "application/zip", "Downloaded report is not a ZIP file"
            )
            Path(report_path / report_name).unlink()
        except FossologyApiError as error:
            logger.error(error.message)


if __name__ == "__main__":
    unittest.main()
    foss.close()
