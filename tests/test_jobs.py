# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import unittest

from test_base import foss, logger
from test_uploads import get_upload, do_upload, upload_filename
from fossology.exceptions import FossologyApiError


class TestFossologyJobs(unittest.TestCase):
    def test_schedule_jobs(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        analysis_agents = foss.user.agents.to_dict()
        jobs_spec = {
            "analysis": analysis_agents,
            "decider": {
                "nomos_monk": True,
                "bulk_reused": True,
                "new_scanner": True,
                "ojo_decider": True,
            },
            "reuse": {
                "reuse_upload": 0,
                "reuse_group": 0,
                "reuse_main": True,
                "reuse_enhanced": True,
            },
        }

        try:
            job = foss.schedule_jobs(foss.rootFolder, test_upload, jobs_spec)
            self.assertEqual(
                job.name,
                upload_filename,
                "Job {job_id} does not relate to the correct upload",
            )
        except FossologyApiError as error:
            logger.error(error.message)


if __name__ == "__main__":
    unittest.main()
    foss.close()
