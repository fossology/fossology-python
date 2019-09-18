# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import os
import time
import logging

from fossology.api import Fossology
from fossology.obj import AccessLevel

logger = logging.getLogger("fossology")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)


FOSSOLOGY_SERVER = os.getenv("FOSSOLOGY_SERVER") or exit(
    "Environment variable FOSSOLOGY_URL doesn't exists"
)
FOSSOLOGY_TOKEN = os.getenv("FOSSOLOGY_TOKEN") or exit(
    "Environment variable FOSSOLOGY_TOKEN doesn't exists"
)
FOSSOLOGY_USER = os.getenv("FOSSOLOGY_EMAIL") or exit(
    "Environment variable FOSSOLOGY_EMAIL doesn't exists"
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


def upload_file_test(filename, test_folder):
    test_upload = foss.upload_file(
        filename,
        test_file_path,
        test_folder,
        description="Test upload via fossology-python lib",
        access_level=AccessLevel.PUBLIC,
    )
    assert test_upload.uploadname == filename, "Uploadname on the server is wrong"

    return test_upload


def delete_folder_test(foss, test_folder):
    foss.delete_folder(test_folder.id)
    time.sleep(3)
    deleted_folder = foss.detail_folder(test_folder.id)
    assert not deleted_folder, "Deleted folder still exists"


if __name__ == "__main__":
    # def test_fossology_api():

    foss = Fossology(FOSSOLOGY_SERVER, FOSSOLOGY_TOKEN, FOSSOLOGY_USER)
    assert foss, "Client session could not be established"

    test_folder = create_folder_test(foss)
    test_folder = update_folder_test(foss, test_folder)
    test_upload = upload_file_test(
        "base-files_10.3-debian10-combined.tar.bz2", test_folder
    )

    all_uploads = foss.list_uploads()
    all_jobs = foss.list_jobs(page_size=1)

    # Cleanup
    foss.delete_upload(test_upload.id)
    delete_folder_test(foss, test_folder)
