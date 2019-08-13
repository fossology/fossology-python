# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later

import os

from fossology.api import Fossology

FOSS_URL = os.getenv("FOSS_URL") or exit("Environment variable FOSS_URL doesn't exists")
FOSS_TOKEN = os.getenv("FOSS_TOKEN") or exit("Environment variable FOSS_TOKEN doesn't exists")

if __name__ == "__main__":

    foss = Fossology(FOSS_URL, FOSS_TOKEN)
    assert foss, "Client session could not be established"

    own_folders = foss.list_folders()
    assert own_folders, "Folders list couldn't be retrieved"

    test_folder = foss.create_folder(foss.user.rootFolderId, "Test", "")
    assert test_folder.name == "Test", "Test folder couldn't be created" 

    detail_folder = foss.detail_folder(test_folder.id)
    assert detail_folder.id == test_folder.id, "Details for folder are inconsistent" 
