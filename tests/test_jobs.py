# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import unittest

from test_base import foss, logger
from test_uploads import get_upload, do_upload, upload_filename
from fossology.exceptions import FossologyApiError
from fossology.obj import Agents


class TestFossologyJobs(unittest.TestCase):
    def test_schedule_jobs(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        jobs = foss.list_jobs(upload=test_upload)
        self.assertEqual(
            len(jobs), 1, "Found more than 1 job for upload {test_upload.uploadname}: {jobs}"
        )

        if not foss.user.agents:
            additional_agent = {"TestAgent": True}
            foss.user.agents = Agents(
                True, True, False, False, True, True, True, True, True, **additional_agent
            )
        analysis_agents = foss.user.agents.to_dict()
        self.assertEqual(analysis_agents["TestAgent"], True, "Specific agent could not be configured for Fossology instance")
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

        jobs = foss.list_jobs(upload=test_upload)
        self.assertEqual(
            len(jobs), 2, f"Found {len(jobs)} jobs for upload {test_upload.uploadname}: {jobs}"
        )

        job = foss.detail_job(jobs[1].id, wait=True, timeout=30)
        self.assertEqual(
            job.status, "Completed", f"Job {job} not completed yet"
        )


if __name__ == "__main__":
    unittest.main()
    foss.close()
