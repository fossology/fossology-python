# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import os
import time

from fossology.api import Fossology
from fossology.obj import AccessLevel

FOSS_URL = os.getenv("FOSS_URL") or exit("Environment variable FOSS_URL doesn't exists")
FOSS_EMAIL = os.getenv("FOSS_EMAIL") or exit(
    "Environment variable FOSS_EMAIL doesn't exists"
)
FOSS_TOKEN = os.getenv("FOSS_TOKEN") or exit(
    "Environment variable FOSS_TOKEN doesn't exists"
)

test_file_path = "/home/marion/code/linux/fossology-python/test_files"


def create_folder_test(foss):
    name = "Marion"
    desc = "Folder used for API testing"
    main_folder = foss.create_folder(foss.rootFolder.id, name, desc)
    assert main_folder.name == name, f"{name} folder couldn't be created"

    name = "API-Test"
    desc = "API Test Folder"
    test_folder = foss.create_folder(main_folder.id, name, desc)
    assert test_folder.name == name, f"{name} folder couldn't be created"
    assert (
        test_folder.description == desc
    ), "Description of folder on the server is wrong"

    return test_folder


def update_folder_test(foss, test_folder):
    new_name = "APITest"
    test_folder = foss.update_folder(test_folder, name=new_name)
    assert test_folder.name == new_name, "New name of folder on the server is wrong"

    new_desc = "Folder used for testing the API"
    test_folder = foss.update_folder(test_folder, description=new_desc)
    assert (
        test_folder.description == new_desc
    ), "New description of folder on the server is wrong"

    old_name = "API-Test"
    old_desc = "API Test Folder"
    test_folder = foss.update_folder(test_folder, name=old_name, description=old_desc)
    assert test_folder.name == old_name, "New old name of folder on the server is wrong"
    assert (
        test_folder.description == old_desc
    ), "New old description of folder on the server is wrong"

    return test_folder


def upload_file_test(filename):
    test_upload = foss.upload_file(
        filename,
        test_file_path,
        test_folder,
        description="Test upload base-files combined",
        access_level=AccessLevel.PUBLIC,
    )
    return test_upload


def delete_folder_test(foss, test_folder):
    foss.delete_folder(test_folder.id)
    time.sleep(3)
    deleted_folder = foss.detail_folder(test_folder.id)
    assert not deleted_folder, "Deleted folder still exists"


def delete_upload_test(foss, test_upload):
    foss.delete_upload(test_upload.id)
    time.sleep(3)
    deleted_upload = foss.detail_upload(test_upload.id)
    assert not deleted_upload, "Deleted upload still exists"


if __name__ == "__main__":
    # def test_fossology_api():

    foss = Fossology(FOSS_URL, FOSS_TOKEN, FOSS_EMAIL)
    assert foss, "Client session could not be established"

    test_folder = create_folder_test(foss)
    # test_folder = update_folder_test(foss, test_folder)
    # delete_folder_test(foss, test_folder)

    # test_upload = upload_file_test("base-files_10.3-debian10-combined.tar.bz2")
    # delete_upload_test(foss, test_upload)

    all_uploads = foss.list_uploads()
    for upload in all_uploads:
        print(upload)

    test_upload = foss.detail_upload(12)

    all_jobs = foss.jobs(page_size=1)
    print(all_jobs)

    # foss.start_jobs(test_folder, test_upload)
