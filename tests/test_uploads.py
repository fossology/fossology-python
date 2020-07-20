# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import time
import secrets
import unittest

from test_base import foss, logger, test_files
from fossology.obj import AccessLevel, Folder, Upload, SearchTypes
from fossology.exceptions import AuthorizationError, FossologyApiError

upload_filename = "base-files_11.tar.xz"


def get_upload():
    upload_list = foss.list_uploads()
    test_upload = None
    for upload in upload_list:
        if upload.uploadname == upload_filename:
            test_upload = upload
            break
    return test_upload


def do_upload():
    file_path = f"{test_files}/{upload_filename}"
    test_upload = foss.upload_file(
        foss.rootFolder,
        file=file_path,
        description="Test upload via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
    )
    time.sleep(3)
    return test_upload


class TestFossologyUploads(unittest.TestCase):
    def test_upload_file(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        self.assertEqual(
            test_upload.uploadname, upload_filename, "Uploadname on the server is wrong"
        )
        self.assertEqual(
            test_upload.filesha1,
            "D4D663FC2877084362FB2297337BE05684869B00",
            "Filesha1 on the server is wrong",
        )

    def test_get_uploads(self):
        name = "FossPythonTestUploads"
        desc = "Created via the Fossology Python API"
        test_folder = foss.create_folder(foss.rootFolder, name, description=desc)
        name = "FossPythonTestUploadsSubfolder"
        test_subfolder = foss.create_folder(test_folder, name, description=desc)
        test_file = f"{test_files}/{upload_filename}"

        # Upload file for unknown group
        with self.assertRaises(AuthorizationError) as cm:
            foss.upload_file(
                test_folder,
                file=test_file,
                description="Test upload from github repository via python lib",
                group="test",
            )
        self.assertIn(
            "Provided group:test does not exist (403)",
            cm.exception.message,
            "Exception message does not match requested group",
        )

        foss.upload_file(
            test_folder,
            file=test_file,
            description="Test upload from github repository via python lib",
        )
        foss.upload_file(
            test_subfolder,
            file=test_file,
            description="Test upload from github repository via python lib",
        )

        # Get uploads from unknown group
        with self.assertRaises(AuthorizationError) as cm:
            foss.list_uploads(group="test")
        self.assertIn(
            "Provided group:test does not exist (403)",
            cm.exception.message,
            "Exception message does not match requested group",
        )

        folder_uploads = foss.list_uploads(folder=test_folder)
        no_subfolder_uploads = foss.list_uploads(folder=test_folder, recursive=False)
        self.assertEqual(len(folder_uploads), 2, "Too many uploads listed")
        self.assertEqual(len(no_subfolder_uploads), 1, "Too many uploads listed")

        # Cleanup
        foss.delete_folder(test_folder)

    def test_upload_from_vcs(self):
        vcs = {
            "vcsType": "git",
            "vcsUrl": "https://github.com/fossology/fossology-python",
            "vcsName": "fossology-python-github-master",
            "vcsUsername": "",
            "vcsPassword": "",
        }
        vcs_upload = foss.upload_file(
            foss.rootFolder,
            vcs=vcs,
            description="Test upload from github repository via python lib",
            access_level=AccessLevel.PUBLIC,
        )
        self.assertEqual(
            vcs_upload.uploadname, vcs["vcsName"], "Uploadname on the server is wrong",
        )
        search_result = foss.search(
            searchType=SearchTypes.DIRECTORIES, filename=".git",
        )
        self.assertEqual(search_result, [], "Search result should be empty")
        foss.delete_upload(vcs_upload)

    def test_upload_ignore_scm(self):
        vcs = {
            "vcsType": "git",
            "vcsUrl": "https://github.com/fossology/fossology-python",
            "vcsName": "fossology-python-github-master",
            "vcsUsername": "",
            "vcsPassword": "",
        }
        vcs_upload = foss.upload_file(
            foss.rootFolder,
            vcs=vcs,
            description="Test upload with ignore_scm flag",
            ignore_scm=False,
            access_level=AccessLevel.PUBLIC,
        )
        self.assertEqual(
            vcs_upload.uploadname, vcs["vcsName"], "Uploadname on the server is wrong",
        )
        search_result = foss.search(
            searchType=SearchTypes.DIRECTORIES, filename=".git",
        )
        self.assertEqual(search_result, [], "A .git directory has been found by search")

        # FIXME: shall be fixed in the next release
        # self.assertEqual(search_result, $something, "Search result should be empty")

        foss.delete_upload(vcs_upload)

    def test_upload_from_url(self):
        url = {
            "url": "https://github.com/fossology/fossology-python/archive/master.zip",
            "name": "fossology-python-master.zip",
            "accept": "zip",
            "reject": "",
            "maxRecursionDepth": "1",
        }
        url_upload = foss.upload_file(
            foss.rootFolder,
            url=url,
            description="Test upload from url via python lib",
            access_level=AccessLevel.PUBLIC,
        )
        self.assertEqual(
            url_upload.uploadname, url["name"], "Uploadname on the server is wrong",
        )
        foss.delete_upload(url_upload)

    def test_empty_upload(self):
        empty_upload = foss.upload_file(
            foss.rootFolder,
            description="Test empty upload",
            access_level=AccessLevel.PUBLIC,
        )
        self.assertIsNone(
            empty_upload, "Something has been uploaded for empty upload test"
        )

    def test_move_upload(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()
            logger.debug(f"{test_upload.id} uploaded from test 'test_move_upload'")

        move_folder = foss.create_folder(
            foss.rootFolder, "MoveUploadTest", "Test move upload function"
        )
        # Move upload for unknown group
        with self.assertRaises(AuthorizationError) as cm:
            foss.move_upload(test_upload, move_folder, group="test")
        self.assertIn(
            "Provided group:test does not exist (403)",
            cm.exception.message,
            "Exception message does not match requested group",
        )

        foss.move_upload(test_upload, move_folder)
        moved_upload = foss.detail_upload(test_upload.id)
        self.assertEqual(
            moved_upload.folderid, move_folder.id, "Upload couldn't be moved"
        )

        # Move/Copy to arbitrary folder
        non_folder = Folder(secrets.randbelow(1000), "Non folder", "", foss.rootFolder)
        self.assertRaises(AuthorizationError, foss.move_upload, test_upload, non_folder)
        self.assertRaises(AuthorizationError, foss.copy_upload, test_upload, non_folder)

        # FIXME: recursion due to https://github.com/fossology/fossology/pull/1748?
        foss.copy_upload(moved_upload, foss.rootFolder)
        list_uploads = foss.list_uploads()
        test_upload = None
        for upload in list_uploads:
            if upload.folderid == foss.rootFolder.id:
                test_upload = upload
        if not test_upload:
            logger.error("Coyping uploads didn't work")
        else:
            logger.info("Copying uploads works again, replace log output with assert")
        # self.assertIsNotNone(test_upload, "Upload couldn't be copied")

        # Clean up
        foss.delete_folder(move_folder)

    def test_upload_summary(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        summary = foss.upload_summary(test_upload)
        self.assertEqual(summary.clearingStatus, "Open")
        self.assertEqual(summary.mainLicense, None)

        # Get upload summary for unknown group
        with self.assertRaises(AuthorizationError) as cm:
            foss.upload_summary(test_upload, group="test")
        self.assertIn(
            "Provided group:test does not exist (403)",
            cm.exception.message,
            "Exception message does not match requested group",
        )

    def test_upload_licenses(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        licenses = foss.upload_licenses(test_upload)
        self.assertEqual(
            len(licenses),
            56,
            "Unexpected licenses were found for upload {test_upload.uploadname}",
        )

        # Get licenses with containers
        licenses = foss.upload_licenses(test_upload, containers=True)
        self.assertEqual(
            len(licenses),
            56,
            "Unexpected licenses were found for upload {test_upload.uploadname}",
        )

        # Get licenses from unscheduled agent 'ojo'
        licenses = foss.upload_licenses(test_upload, agent="ojo")
        self.assertIsNone(
            licenses[0].get("agentFindings"),
            "Unexpected ojo licenses were found for upload {test_upload.uploadname}",
        )

        # Get licenses from another agent 'monk'
        licenses = foss.upload_licenses(test_upload, agent="monk")
        self.assertEqual(
            len(licenses),
            23,
            "Unexpected licenses were found for upload {test_upload.uploadname}",
        )

        # Get license from upload for unknown group
        with self.assertRaises(AuthorizationError) as cm:
            foss.upload_licenses(test_upload, group="test")
        self.assertIn(
            "Provided group:test does not exist (403)",
            cm.exception.message,
            "Exception message does not match requested group",
        )

    def test_delete_unknown_upload(self):
        non_upload = Upload(
            foss.rootFolder,
            "Root Folder",
            secrets.randbelow(1000),
            "",
            "Non Upload",
            "2020-05-05",
            "0",
            "sha",
        )
        self.assertRaises(FossologyApiError, foss.delete_upload, non_upload)

    def test_delete_upload(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        # Delete upload for unknown group
        with self.assertRaises(AuthorizationError) as cm:
            foss.delete_upload(test_upload, group="test")
        self.assertIn(
            "Provided group:test does not exist (403)",
            cm.exception.message,
            "Exception message does not match requested group",
        )

        foss.delete_upload(test_upload)

        verify_uploads = foss.list_uploads()
        self.assertEqual(len(verify_uploads), 0, "Upload couldn't be deleted")


if __name__ == "__main__":
    unittest.main()
    foss.close()
