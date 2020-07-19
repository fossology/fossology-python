# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import time
import pytest
import secrets

from fossology import Fossology
from fossology.obj import Folder
from fossology.exceptions import AuthorizationError, FossologyApiError


def test_create_folder(foss: Fossology):
    name = "FossPythonTest"
    desc = "Created via the Fossology Python API"
    # Create folder for unknown group
    with pytest.raises(AuthorizationError) as excinfo:
        foss.create_folder(foss.rootFolder, name, description=desc, group="test")
    assert "Folder creation for group test in folder 1 not authorized" in str(
        excinfo.value
    )

    test_folder = foss.create_folder(foss.rootFolder, name, description=desc)
    assert test_folder.name == name
    assert test_folder.description == desc

    # Recreate folder to test API response 200
    test_folder = foss.create_folder(foss.rootFolder, name, description=desc)
    assert test_folder.name == name

    # Cleanup
    foss.delete_folder(test_folder)


def test_create_folder_no_parent(foss: Fossology):
    # Create folder in arbitrary parent
    parent = Folder(secrets.randbelow(1000), "Parent", "", 0)
    with pytest.raises(AuthorizationError) as excinfo:
        foss.create_folder(parent, "FossFolderNoParent")
    assert f"Folder creation in folder {parent.id} not authorized" in str(excinfo.value)


def test_update_folder(foss: Fossology):
    name = "FossPythonFolderUpdate"
    desc = "Created via the Fossology Python API"
    update_folder = foss.create_folder(foss.rootFolder, name, desc)

    name = "NewFolderName"
    desc = "Updated via the Fossology Python API"
    update_folder = foss.update_folder(update_folder, name=name, description=desc)
    assert update_folder.name == name
    assert update_folder.description == desc

    # Cleanup
    foss.delete_folder(update_folder)


def test_move_folder(foss: Fossology):
    move_copy_folder = foss.create_folder(
        foss.rootFolder, "MoveCopyTest", "Test move() and copy() functions"
    )
    test_folder = foss.create_folder(
        foss.rootFolder, "TestFolder", "Folder to be moved and copied via API"
    )
    test_folder = foss.move_folder(test_folder, move_copy_folder)
    assert test_folder.parent == move_copy_folder.id

    folder_copy = foss.copy_folder(test_folder, foss.rootFolder)
    folder_list = foss.list_folders()
    folder_copy = [
        folder
        for folder in folder_list
        if folder.parent == foss.rootFolder.id and folder.name == "TestFolder"
    ]
    assert folder_copy

    # Cleanup
    foss.delete_folder(move_copy_folder)
    foss.delete_folder(folder_copy[0])


def test_delete_folder(foss: Fossology):
    folder = foss.create_folder(
        foss.rootFolder, "ToBeDeleted", "Test folder deletion via API"
    )
    foss.delete_folder(folder)
    time.sleep(3)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.detail_folder(folder)
    assert f"Error while getting details for folder ToBeDeleted ({folder.id})" in str(
        excinfo.value
    )
