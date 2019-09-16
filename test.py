# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import os
import time

from fossology.api import Fossology
from fossology.obj import AccessLevel

FOSS_URL = os.getenv("FOSS_URL") or exit("Environment variable FOSS_URL doesn't exists")
FOSS_TOKEN = os.getenv("FOSS_TOKEN") or exit(
    "Environment variable FOSS_TOKEN doesn't exists"
)


def create_folder_test(foss):
    # create_folder
    main_folder = foss.create_folder(
        foss.rootFolder.id, "Marion", "Folder used for API testing"
    )
    assert main_folder.name == "Marion", "Marion folder couldn't be created"

    test_folder = foss.create_folder(main_folder.id, "API-Test", "API Test Folder")
    assert test_folder.name == "API-Test", "Test folder couldn't be created"
    assert (
        test_folder.description == "API Test Folder"
    ), "Description of folder on the server is wrong"

    return test_folder


def update_folder_test(foss, test_folder):
    # update_folder
    test_folder = foss.update_folder(test_folder, name="APITest")
    assert test_folder.name == "APITest", "New name of folder on the server is wrong"
    assert (
        test_folder.description == "API Test Folder"
    ), "Description of folder on the server is wrong"

    test_folder = foss.update_folder(
        test_folder, description="Folder used for testing the API"
    )
    assert test_folder.name == "APITest", "Name of folder on the server is wrong"
    assert (
        test_folder.description == "Folder used for testing the API"
    ), "New description of folder on the server is wrong"

    test_folder = foss.update_folder(
        test_folder, name="API-Test", description="API Test Folder"
    )
    assert (
        test_folder.name == "API-Test"
    ), "New old name of folder on the server is wrong"
    assert (
        test_folder.description == "API Test Folder"
    ), "New old description of folder on the server is wrong"

    return test_folder


def delete_folder_test(foss, test_folder):
    foss.delete_folder(test_folder.id)
    time.sleep(3)
    deleted_folder = foss.detail_folder(test_folder.id, test_folder.parent)
    assert not deleted_folder, "Deleted folder still exists"


if __name__ == "__main__":

    foss = Fossology(FOSS_URL, FOSS_TOKEN)
    assert foss, "Client session could not be established"

    test_folder = create_folder_test(foss)
    # test_folder = update_folder_test(foss, test_folder)
    # delete_folder_test(test_folder)

    test_file_path = "/home/marion/code/linux/fossology-python/test_files"
    foss.upload_file(
        "base-files_10.3-debian10-combined.tar.bz2",
        test_file_path,
        test_folder,
        description="Test upload base-files combined",
        access_level=AccessLevel.PUBLIC,
    )
