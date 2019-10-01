# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import os
import time
import logging

from fossology import Fossology
from fossology.obj import AccessLevel

logger = logging.getLogger("fossology")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)s\t%(name)s: %(message)s")
console.setFormatter(formatter)
logger.addHandler(console)


FOSSOLOGY_SERVER = os.getenv("FOSSOLOGY_SERVER") or exit(
    "Environment variable FOSSOLOGY_SERVER doesn't exists"
)
FOSSOLOGY_TOKEN = os.getenv("FOSSOLOGY_TOKEN") or exit(
    "Environment variable FOSSOLOGY_TOKEN doesn't exists"
)
FOSSOLOGY_USER = os.getenv("FOSSOLOGY_EMAIL") or exit(
    "Environment variable FOSSOLOGY_EMAIL doesn't exists"
)

test_file_path = "/home/marion/code/linux/fossology-python/test_files"


def create_folder_test(foss):
    name = "MarionAPI"
    desc = "Folder used for API testing"
    main_folder = foss.create_folder(foss.rootFolder, name, desc)
    assert main_folder.name == name, f"{name} folder couldn't be created"

    name = "API-Test"
    desc = "API Test Folder"
    test_folder = foss.create_folder(main_folder, name, desc)
    assert test_folder.name == name, f"{name} folder couldn't be created"
    assert (
        test_folder.description == desc
    ), "Description of folder on the server is wrong"

    return main_folder, test_folder


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
    foss.delete_folder(test_folder)
    time.sleep(3)
    deleted_folder = foss.detail_folder(test_folder)
    assert not deleted_folder, "Deleted folder still exists"


if __name__ == "__main__":
    foss = Fossology(FOSSOLOGY_SERVER, FOSSOLOGY_TOKEN, FOSSOLOGY_USER)
    assert foss, "Client session could not be established"

    # Test folder endpoints
    main_folder, test_folder = create_folder_test(foss)
    # PATCH /folders/{id} seems broken on the server side
    # PUT /folders/{id} seems broken on the server side
    # update_folder_test(foss, test_folder)
    # other_folder = foss.create_folder(
    #    test_folder, "MoveCopyTest", "Test move() and copy() functions"
    # )
    # foss.move_folder(other_folder, main_folder)
    # assert (
    #    foss.detail_folder(other_folder.id).parent == main_folder.id
    # ), "Folder was not moved to the right location"
    # foss.copy_folder(other_folder, test_folder)
    # foss.detail_folder(
    #    other_folder.id
    # ).parent == test_folder.id, "Folder was not copied to the right location"

    test_upload = upload_file_test(
        "base-files_10.3-debian10-combined.tar.bz2", main_folder
    )
    print(test_upload)
    assert (
        test_upload.uploadname == "base-files_10.3-debian10-combined.tar.bz2"
    ), "File could not be uploaded"

    foss.move_upload(test_upload, test_folder)
    test_upload = foss.detail_upload(test_upload.id)
    assert test_upload.folderid == test_folder.id, "Upload couldn't be moved"

    foss.copy_upload(test_upload, main_folder)
    test_upload = foss.detail_upload(test_upload.id)

    # Cleanup
    foss.delete_upload(test_upload.id)
    delete_folder_test(foss, test_folder)
    delete_folder_test(foss, main_folder)
