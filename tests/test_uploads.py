# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import time
import unittest

from test_base import foss, logger, test_files
from fossology.obj import AccessLevel
from fossology.exceptions import FossologyApiError

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
    try:
        file_path = f"{test_files}/{upload_filename}"
        test_upload = foss.upload_file(
            foss.rootFolder,
            file=file_path,
            description="Test upload via fossology-python lib",
            access_level=AccessLevel.PUBLIC,
        )
        time.sleep(3)
        return test_upload
    except FossologyApiError as error:
        logger.error(error.message)
        return None


class TestFossologyUploads(unittest.TestCase):
    def test_upload_file(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        self.assertEqual(
            test_upload.uploadname, upload_filename, "Uploadname on the server is wrong"
        )

    def test_upload_from_vcs(self):
        try:
            vcs = {
                "vcsType": "git",
                "vcsUrl": "https://github.com/fossology/fossdriver",
                "vcsName": "fossdriver-github-master",
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
                vcs_upload.uploadname,
                vcs["vcsName"],
                "Uploadname on the server is wrong",
            )
        except FossologyApiError as error:
            logger.error(error.message)

        logger.info(f"Delete VCS test upload {vcs_upload.id}")
        foss.delete_upload(vcs_upload)

    def test_move_upload(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()
            logger.debug(f"{test_upload.id} uploaded from test 'test_move_upload'")

        move_folder = foss.create_folder(
            foss.rootFolder, "MoveUploadTest", "Test move upload function"
        )
        foss.move_upload(test_upload, move_folder)
        moved_upload = foss.detail_upload(test_upload.id)
        self.assertEqual(
            moved_upload.folderid, move_folder.id, "Upload couldn't be moved"
        )

        foss.copy_upload(moved_upload, foss.rootFolder)
        list_uploads = foss.list_uploads()
        test_upload = None
        for upload in list_uploads:
            if upload.folderid == foss.rootFolder.id:
                test_upload = upload
        self.assertIsNotNone(test_upload, "Upload couldn't be copied")

        # Clean up
        foss.delete_folder(move_folder)

    def test_upload_summary(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        summary = foss.upload_summary(test_upload.id)
        # FIXME: getting the summary without accessing the upload from the UI
        # currently doesn't work, it returns a 500
        if summary:
            self.assertEqual(
                summary.uploadName, upload_filename, "Uploadname on the server is wrong"
            )
            self.assertEqual(
                summary.clearingStatus, "Open", "Clearing status should be 'Open'"
            )

    def test_delete_upload(self):
        test_upload = get_upload()
        if not test_upload:
            test_upload = do_upload()

        try:
            foss.delete_upload(test_upload)
            logger.debug(f"Waiting 5 second after scheduling {test_upload.id} deletion")
            time.sleep(5)
        except FossologyApiError as error:
            logger.error(error.message)

        verify_uploads = foss.list_uploads()
        print(f"{len(verify_uploads)} are still available")
        for upload in verify_uploads:
            print(upload)
        self.assertEqual(len(verify_uploads), 0, "Upload couldn't be deleted")


if __name__ == "__main__":
    unittest.main()
    foss.close()
