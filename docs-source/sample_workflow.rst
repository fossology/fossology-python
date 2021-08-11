===============
Sample Workflow
===============

 A small code sample :
    - create token (if necessary)
    - login on Fossology (using the token)
    - create a "clearing" group
    - upload a source file (visible for the group)
    - start default scan jobs
    - generate report
    - download report
    - store report in local file

Needed imports and Variables
============================

.. code-block:: python

    from typing import Dict
    import sys
    import os
    import secrets
    from getpass import getpass
    import requests
    from fossology import Fossology, fossology_token
    from fossology.obj import Group, AccessLevel, TokenScope


    FOSSOLOGY_SERVER = "http://fossology/repo"

Create JWT Token
================

Create token - if not already done - and store it in local file for reuse.

.. code-block:: python

  if not os.path.exists(".token"):
    print("Enter your Fossology credentials, e.g. in the test environment 'username: fossy' and 'password: fossy'")
    username = input("username: ")
    pw = getpass()
    token = fossology_token(
        FOSSOLOGY_SERVER,
        username,
        pw,
        secrets.token_urlsafe(8), # TOKEN_NAME seen in the database
        TokenScope.WRITE,
    )
    with open(".token", "w") as fp:
        fp.write(token)
    print("token written to .token")
  else:
    print("Reuse token from .token")
  # Load the token
  with open(".token", "r") as fp:
    token = fp.read()


Login to the fossology Server
=============================

 Create the Fossology Instance.

.. code-block:: python

  foss = Fossology(FOSSOLOGY_SERVER, token)
  print(f"Logged in as user {foss.user.name}")


Create Folder If needed 
=======================

Create Folder if needed.

.. code-block:: python

  folder_name = "AwesomeFossFolder"
  folder_desc = "AwesomeProjectSources"
  folder_already_created = False
  # Check if the folder already exists
  for folder in foss.folders:
    if folder.name == folder_name:
        folder_already_created = True
        print(f"Already Created {folder.name} with description {folder.description}")
        test_folder = folder

  if not folder_already_created:
    print("Folder needs creation")
    test_folder = foss.create_folder(
        foss.rootFolder, folder_name, description=folder_desc
    )
    print(f"Created {test_folder.name} with description {test_folder.description}")
  assert test_folder.name == folder_name
  assert test_folder.description == folder_desc



Create Group If needed 
=======================

Create Group If needed.

.. code-block:: python

  group_name = "clearing"
  group_already_created = False

  for group in foss.list_groups():
    if group.name == group_name:
        group_already_created = True
        print(f"Group {group_name} already created")
        test_group = group

  if not group_already_created:
    # XXX create_group does not return created group
    foss.create_group(group_name)
    for group in foss.list_groups():
        if group.name == group_name:
            test_group = group
    print(f"Created group named {test_group.name}")

  assert test_group
  assert test_group.name == group_name




Upload File 
===========
We first get an example file from our github repository testenvironment and then
upload it to the server. 

.. code-block:: python

  filename = "my_base-files_11.tar.xz"
  if not os.path.isfile(os.path.join("/tmp", filename)):
    url = "https://github.com/fossology/fossology-python/blob/master/tests/files/base-files_11.tar.xz"
    print(f"Get a local copy of {filename} from {url}")
    r = requests.get(url)
    with open(os.path.join("/tmp", filename), "wb") as fp:
        fp.write(r.content)
  assert os.path.isfile(os.path.join("/tmp", filename))


  uploads, num_elems = foss.list_uploads(
    folder=test_folder, group=test_group.name, all_pages=True
  )
  file_already_uploaded = False
  test_file = filename
  test_file_path = f"/tmp/{test_file}"

  for upload in uploads:
    if test_file == upload.uploadname:
        file_already_uploaded = True
        my_upload = upload
        print(f"{test_file} Already uploaded")

  if not file_already_uploaded:
    print(f"{test_file} needs upload")
    my_upload = foss.upload_file(
        test_folder,
        file=test_file_path,
        description="Test upload via fossology-python lib",
        group=test_group.name,
        access_level=AccessLevel.PUBLIC,
    )
  assert my_upload.uploadname == test_file

Start default scan jobs
=======================

.. code-block:: python

  detailed_job = foss.schedule_jobs(
    test_folder,
    my_upload,
    {
        "analysis": {
            "bucket": True,
            "copyright_email_author": True,
            "ecc": True,
            "keyword": True,
            "monk": True,
            "mime": True,
            "monk": True,
            "nomos": True,
            "ojo": True,
            "package": True,
            "specific_agent": True,
        },
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
            "reuse_report": True,
            "reuse_copyright": True,
        },
    },
  )

  print(f"scan job {detailed_job} set up")


Generate report
===============

.. code-block:: python

  report_id = foss.generate_report(my_upload, group=test_group.name)
  print(f"report created with id {report_id} ")

Download report
===============

.. code-block:: python

  content, name = foss.download_report(report_id, test_group.name)

Write report to disk
====================

.. code-block:: python

  dst = os.path.join("/tmp",name, "wb")
  with open(dst, "wb") as fp:
    fp.write(content)

  print(f"report was written to file {dst}.")

Output
======

::

    username/password within the testenvironment is fossy/fossy
    username: fossy
    Password: 
    token written to .token
    Logged in as user fossy
    Folder needs creation
    Created AwesomeFossFolder with description AwesomeProjectSources
    Created group named clearing
    my_base-files_11.tar.xz needs upload
    scan job Job 'my_base-files_11.tar.xz' (3) queued on 2021-08-09 14:03:20.253572+00 (Status: Processing ETA: 0) set up
    report created with id 4 
    report was written to file /tmp/ReadMe_OSS_my_base-files_11.tar.xz_1628517800.txt


