# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import time
import json
import secrets
import logging
import unittest

from fossology import Fossology, fossology_token
from fossology.obj import AccessLevel, TokenScope, ReportFormat, SearchTypes
from fossology.exceptions import FossologyApiError, AuthenticationError

from pathlib import Path

test_files = "test_files"
upload_filename = "base-files_10.3-debian10-combined.tar.bz2"

logger = logging.getLogger("fossology")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(name)s: %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)


def get_upload():
    upload_list = foss.list_uploads()
    test_upload = None
    for upload in upload_list:
        if upload.uploadname == upload_filename:
            test_upload = upload
            break
    return test_upload


def generate_fossology_token(server):
    try:
        return fossology_token(
            server, "fossy", "fossy", secrets.token_urlsafe(8), TokenScope.WRITE
        )
    except (FossologyApiError, AuthenticationError) as error:
        exit(error.message)


# Get API handler
try:
    FOSSOLOGY_SERVER = "http://fossology/repo"
    FOSSOLOGY_TOKEN = generate_fossology_token(FOSSOLOGY_SERVER)
    foss = Fossology(FOSSOLOGY_SERVER, FOSSOLOGY_TOKEN, "fossy")
except (FossologyApiError, AuthenticationError) as error:
    exit(error.message)


class TestFossologyFolders(unittest.TestCase):
    def test_create_folder(self):
        name = "FossPythonTest"
        desc = "Created via the Fossology Python API"
        test_folder = foss.create_folder(foss.rootFolder, name, description=desc)
        self.assertEqual(
            test_folder.name, name, f"Main test {name} folder couldn't be created"
        )
        self.assertEqual(
            test_folder.description,
            desc,
            "Description of folder on the server is wrong",
        )
        foss.delete_folder(test_folder)

    def test_update_folder(self):
        name = "FossPythonFolderUpdate"
        desc = "Created via the Fossology Python API"
        update_folder = foss.create_folder(foss.rootFolder, name, desc)

        name = "NewFolderName"
        desc = "Updated via the Fossology Python API"
        update_folder = foss.update_folder(update_folder, name=name, description=desc)
        self.assertEqual(update_folder.name, name, f"Folder name couldn't be updated")
        self.assertEqual(
            update_folder.description, desc, f"Folder description couldn't be updated"
        )
        foss.delete_folder(update_folder)

    def test_move_folder(self):
        move_copy_folder = foss.create_folder(
            foss.rootFolder, "MoveCopyTest", "Test move() and copy() functions"
        )
        test_folder = foss.create_folder(
            foss.rootFolder, "TestFolder", "Folder to be moved and copied via API"
        )
        try:
            test_folder = foss.move_folder(test_folder, move_copy_folder)
            self.assertEqual(
                test_folder.parent,
                move_copy_folder.id,
                "Folder was not moved to the expected location",
            )
        except FossologyApiError as error:
            logger.error(error.message)

        try:
            folder_copy = foss.copy_folder(test_folder, foss.rootFolder)
            folder_list = foss.list_folders()
            folder_copy = [
                folder
                for folder in folder_list
                if folder.parent == foss.rootFolder.id and folder.name == "TestFolder"
            ]
            self.assertIsNotNone(
                folder_copy, "Folder was not copied to the expected location"
            )
        except FossologyApiError as error:
            logger.error(error.message)

        foss.delete_folder(move_copy_folder)
        foss.delete_folder(folder_copy[0])

    def test_delete_folder(self):
        folder = foss.create_folder(
            foss.rootFolder, "ToBeDeleted", "Test folder deletion via API"
        )
        foss.delete_folder(folder)
        time.sleep(3)
        try:
            deleted_folder = foss.detail_folder(folder)
            self.assertIsNotNone(deleted_folder, "Deleted folder still exists")
        except FossologyApiError as error:
            logger.error(error.message)


class TestFossologyUploads(unittest.TestCase):
    def test_upload_file(self):
        test_upload = get_upload()
        if not test_upload:
            try:
                test_upload = foss.upload_file(
                    upload_filename,
                    test_files,
                    foss.rootFolder,
                    description="Test upload via fossology-python lib",
                    access_level=AccessLevel.PUBLIC,
                )
                self.assertEqual(
                    test_upload.uploadname,
                    upload_filename,
                    "Uploadname on the server is wrong",
                )
            except FossologyApiError as error:
                logger.error(error.message)

    def test_move_upload(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = foss.upload_file(
                upload_filename,
                test_files,
                foss.rootFolder,
                description="Test upload via fossology-python lib",
                access_level=AccessLevel.PUBLIC,
            )

        move_folder = foss.create_folder(
            foss.rootFolder, "MoveUploadTest", "Test move upload function"
        )
        foss.move_upload(test_upload, move_folder)
        moved_upload = foss.detail_upload(test_upload.id)
        self.assertEqual(
            moved_upload.folderid, move_folder.id, "Upload couldn't be moved"
        )

        foss.copy_upload(test_upload, foss.rootFolder)
        list_uploads = foss.list_uploads()
        test_upload = None
        for upload in list_uploads:
            if upload.folderid == foss.rootFolder.id:
                test_upload = upload
        self.assertIsNotNone(test_upload, "Upload couldn't be copied")

        foss.delete_folder(move_folder)

    def test_delete_upload(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = foss.upload_file(
                upload_filename,
                test_files,
                foss.rootFolder,
                description="Test upload via fossology-python lib",
                access_level=AccessLevel.PUBLIC,
            )

        try:
            foss.delete_upload(test_upload)
            time.sleep(3)
        except FossologyApiError as error:
            logger.error(error.message)

        test_upload = get_upload()
        self.assertIsNone(test_upload, "Upload couldn't be deleted")


class TestFossologyJobs(unittest.TestCase):
    def test_schedule_jobs(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = foss.upload_file(
                upload_filename,
                test_files,
                foss.rootFolder,
                description="Test upload via fossology-python lib",
                access_level=AccessLevel.PUBLIC,
            )

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


class TestFossologyReport(unittest.TestCase):
    def test_generate_report(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = foss.upload_file(
                upload_filename,
                test_files,
                foss.rootFolder,
                description="Test upload via fossology-python lib",
                access_level=AccessLevel.PUBLIC,
            )

        try:
            report_id = foss.generate_report(test_upload, Format=ReportFormat.SPDX2)
        except FossologyApiError as error:
            logger.error(error.message)

        try:
            # Plain text
            report = foss.download_report(report_id)
            report_path = Path.cwd() / "test_files"
            report_name = upload_filename + ".spdx-report.rdf"
            with open(report_path / report_name, "w+") as report_file:
                report_file.write(report)
        except FossologyApiError as error:
            logger.error(error.message)


class TestFossologySearch(unittest.TestCase):
    def test_search(self):
        try:
            search_result = foss.search(
                searchType=SearchTypes.ALLFILES, filename="GPL%"
            )
            print(json.dumps(search_result, indent=4))
            self.assertIsNotNone(search_result, "Couldn't search Fossology")
        except FossologyApiError as error:
            logger.error(error.message)


if __name__ == "__main__":

    unittest.main()

    foss.close()
