|License| |PyPI Version| |Python Version| |Static Checks| |Fossology Tests| |Coverage|

.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/deveaud-m/fossology-python/LICENSE.md

.. |PyPI Version| image:: https://badge.fury.io/py/fossology.svg
   :target: https://pypi.org/project/fossology

.. |Python Version| image:: https://img.shields.io/badge/python-3.7%2C3.8%2C3.9-blue?logo=python
   :target: https://www.python.org/doc/versions/

.. |Static Checks| image:: https://github.com/deveaud-m/fossology-python/workflows/Static%20Checks/badge.svg
   :target: https://github.com/deveaud-m/fossology-python/actions?query=workflow%3A%22Static+Checks%22

.. |Fossology Tests| image:: https://github.com/deveaud-m/fossology-python/workflows/Fossology%20Tests/badge.svg
   :target: https://github.com/deveaud-m/fossology-python/actions?query=workflow%3A%22Fossology+Tests%22

.. |Coverage| image:: https://codecov.io/gh/fossology/fossology-python/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/fossology/fossology-python

A simple wrapper for the Fossology REST API.

See `the OpenAPI specification <https://raw.githubusercontent.com/fossology/fossology/master/src/www/ui/api/documentation/openapi.yaml>`_ used to implement this library.

   Compatible API versions:

   - 1.2.1 (Fossology 3.10.0)
   - 1.3.2 (Fossology 3.11.0)

Documentation
=============

See `fossology-python on Github Pages <https://fossology.github.io/fossology-python>`_.

Usage
=====

Installation
------------

   This project is available as `Python package on PyPi.org <https://pypi.org/project/fossology/>`_.

-  Install fossology and required dependencies:

   .. code:: shell

      pip install fossology requests

Using the API
-------------

-  Get a REST API token either from the Fossology server under "User->Edit user account" or generate a token using the method available in this library:

   .. code:: Python

      from fossology import fossology_token
      from fossology.obj import TokenScope

      FOSSOLOGY_SERVER = "https://fossology.example.com/"
      FOSSOLOGY_USER = "fossy"
      FOSSOLOGY_PASSWORD = "fossy"
      TOKEN_NAME = "fossy_token"

      token = fossology_token(
            FOSSOLOGY_SERVER,
            FOSSOLOGY_USER,
            FOSSOLOGY_PASSWORD,
            TOKEN_NAME,
            TokenScope.WRITE
      )

-  Start using the API:

   .. code:: python

      from fossology import Fossology

      # Starting from API version 1.2.3, the `FOSSOLOGY_USER` option is not needed anymore
      foss = Fossology(FOSSOLOGY_SERVER, token, FOSSOLOGY_USER)
      print(f"Logged in as user {foss.user.name}")


Using  the Cmd Line (Pre  Alpha)
--------------------------------

Generate a configuration File:

    .. code:: bash

        $poetry run foss_cli  config
           server url within the testenvironment is http://fossology/repo
           server url: http://fossology/repo
           username/password. (within the testenvironment this is fossy/fossy)
           username: fossy
           Password: 
           token scope. (Either read or write):
           token_scope: write
           ... - WARNING - [foss_cli.py:406] - Create New Config server: ...h
           ... - WARNING - [foss_cli.py:451] - New Config section server: ...

This will get a token from Fossology Server and store it within the local .foss_cli.ini file. 
On subsequent foss_cli calls those values will be reused.

Verbosity of all foss_cli commands could be increased using the -v verbosity option.


    .. code:: bash

        $poetry run foss_cli  -vv config

Runs the same command with verbosity level  2.
It leaves a log-file in directory .foss_cli_results named .foss_cli.log.

This way ALL cmds could be logged.

To  create  a group:

     .. code:: bash

           poetry run foss_cli -vv create_group  AwesomeGroup

The looging again is left in directory .foss_cli_results named .foss_cli.log by default.

To create a a folder:

     .. code:: bash

          poetry run foss_cli -vv create_folder AwesomeFolder \
                   --folder_group AwesomeGroup \
                   --folder_description "Description of AwesomeFolder"


To upload a source package to the server and initialize a the schedule_jobs command could be used:

    .. code:: bash

       Usage: foss_cli schedule_jobs [OPTIONS] FILE_NAME
       The foss_cli schedule_jobs command.
       Options:
         --folder_name TEXT              The name of the folder to upload to.
         --file_description TEXT         The description of the upload.
         --dry_run / --no_dry_run        Do not upload but show what would be done.
                                         Use -vv to see output.
         --reuse_newest_upload / --no_reuse_newest_upload
                                         Reuse newest upload if available.
         --reuse_newest_job / --no_reuse_newest_job
                                         Reuse newest scheduled job for the upload if
                                         available.
         --report_format TEXT            The name of the reportformat. [dep5,
                                         spdx2,spdxtv,readmeoss,unifiedreport]
         --access_level TEXT             The access level of the
                                         upload.[private,protected,public]
         --help                          Show this message and exit.

To upload a file from the development source:

    .. code:: bash

        poetry run foss_cli -vv schedule_jobs tests/files/zlib_1.2.11.dfsg-0ubuntu2.debian.tar.xz \
                            --folder_name AwesomeFolder \
                            --access_level public \
                            --report_format unifiedreport

Contribute
==========

Develop
-------

-  All contributions in form of bug reports, feature requests or merge requests!

-  Use proper
   `docstrings <https://realpython.com/documenting-python-code/>`__ to
   document functions and classes

-  Extend the testsuite **poetry run pytest** with the new functions/classes

-  The **documentation website** can automatically be generated by the `Sphinx autodoc
   extension <http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_


Build
-----

- You can build the PyPi package using `poetry <https://poetry.eustace.io/>`_:

  .. code:: shell

    poetry build

- Build documentation:

  The static site is generated automatically by
  `GitHub Actions <https://github.com/fossology/fossology-python/actions/workflows/doc-deploy.yml>`_
  on every merge to main branch and pushed to **gh-pages** branch. The action uses
  `JamesIves/github-pages-deploy-action <https://github.com/JamesIves/github-pages-deploy-action>`_
  to deploy the static pages.

  To build it locally

  .. code:: shell

     poetry run sphinx-build -b html docs-source docs/

- Cleanup builds:

  .. code:: shell

     rm -r dist/ docs/

Tag
----

Each new release gets a new tag with important information about the changes added to the new release:

.. code:: shell

   git tag -a vx.x.x -m "New major/minor/patch release x.x.x"
   git push origin vx.x.x

Add required information in the corresponding `release in the Github project <https://github.com/fossology/fossology-python/releases>`_.


Test
----

The testsuite available in this project expects a running Fossology instance under the hostname **fossology** with the default admin user "fossy".

- Use the latest Fossology container from `Docker hub <https://hub.docker.com/r/fossology/fossology>`_:

  .. code:: shell

    docker pull fossology/fossology
    tar xJf tests/files/base-files_11.tar.xz -C /tmp
    docker run --mount src="/tmp",dst=/tmp,type=bind --name fossology -p 80:80 fossology/fossology

- Start the complete test suite or a specific test case (and generate coverage report):

  .. code:: shell

     poetry run coverage run --source=fossology -m pytest
     poetry run coverage report -m
     poetry run coverage html
