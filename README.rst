|License| |PyPI Version| |Python Version| |Downloads| |Static Checks| |Fossology Tests| |Coverage|

.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/deveaud-m/fossology-python/LICENSE.md

.. |PyPI Version| image:: https://badge.fury.io/py/fossology.svg
   :target: https://pypi.org/project/fossology

.. |Python Version| image:: https://img.shields.io/badge/python-3.11%2C3.12-blue?logo=python
   :target: https://www.python.org/doc/versions/

.. |Downloads| image:: https://static.pepy.tech/badge/fossology
   :target: https://pepy.tech/project/fossology

.. |Static Checks| image:: https://github.com/deveaud-m/fossology-python/workflows/Static%20Checks/badge.svg
   :target: https://github.com/deveaud-m/fossology-python/actions?query=workflow%3A%22Static+Checks%22

.. |Fossology Tests| image:: https://github.com/deveaud-m/fossology-python/workflows/API%20Tests/badge.svg
   :target: https://github.com/deveaud-m/fossology-python/actions?query=workflow%3A%22API+Tests%22

.. |Coverage| image:: https://codecov.io/gh/fossology/fossology-python/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/fossology/fossology-python
   

A simple wrapper for the Fossology REST API.

See `the OpenAPI specification <https://raw.githubusercontent.com/fossology/fossology/master/src/www/ui/api/documentation/openapi.yaml>`_ used to implement this library.

Current release is compatible with **Fossology version 4.4.0** - API version 1.6.1 (not all endpoints are supported)

   `See release notes <https://github.com/fossology/fossology-python/releases>`_ for all details.

   If you miss an API Endpoint, please open a new issue or contribute a pull request.

   API v2 is partially supported too, however the specification is not stable yet and not all endpoints are supported.

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

-  Get a REST API token either from the Fossology server under **``User->Edit user account``** or generate a token using the method available in this library:

   .. code:: python

      from fossology import fossology_token
      from fossology.enum import TokenScope

      FOSSOLOGY_SERVER = "https://fossology.example.com/repo" # Note the absence of the trailing slash, otherwise the token generation will fail
      FOSSOLOGY_USER = "fossy"
      FOSSOLOGY_PASSWORD = "fossy"
      TOKEN_NAME = "fossy_token"

      # By default version v1 of the token generation API will be used
      token = fossology_token(
            FOSSOLOGY_SERVER,
            FOSSOLOGY_USER,
            FOSSOLOGY_PASSWORD,
            TOKEN_NAME,
            TokenScope.WRITE
            version="v1"
      )

-  Start using the API:

   .. code:: python

      from fossology import Fossology

      # By default version v1 of the API will be used
      foss = Fossology(FOSSOLOGY_SERVER, token, FOSSOLOGY_USER, version="v1")
      print(f"Logged in as user {foss.user.name}")


Using the CLI
-------------

Fossology Python also offers a command line interface to simplify interactions with your Fossology server.

- To get a list of available commands, run:

   .. code:: bash

      $ foss_cli --help
      Usage: foss_cli [OPTIONS] COMMAND [ARGS]...

- Generate a configuration file:

   .. code:: bash

      $ foss_cli config
      Enter the URL to your Fossology server: e.g. http://fossology/repo
      Fossology URL: http://fossology/repo
      Enter Username and Password: e.g. fossy/fossy (in the default environment)
      Username: fossy
      Password: 
      Enter a scope for your Fossology token: either 'read' or 'write'
      Token scope: write

   This will get a token from Fossology server and store it within the local ``.foss_cli.ini`` file. 

   On subsequent foss_cli calls those values will be reused.

   Re-run the config command to **create a new token** once it expired.

- Verbosity of all foss_cli commands could be increased using the ``-v`` verbosity option:

   .. code:: bash

      $ foss_cli -vv [COMMAND]

   This runs the given command with verbosity level 2 (all debug statements will be logged).

   A log file in directory ``.foss_cli_results`` named ``.foss_cli.log`` will be created.

- To create a group:

   .. code:: bash

      $ foss_cli -vv create_group FossGroup

- To create a a folder:

   .. code:: bash

      $ foss_cli -vv create_folder FossFolder \
         --folder_group FossGroup \
         --folder_description "Description of FossFolder"

- To upload a file:

   .. code:: bash

      $ foss_cli -vv upload_file tests/files/zlib_1.2.11.dfsg-0ubuntu2.debian.tar.xz \
            --folder_name FossFolder
            --access_level public

- To upload a source package to the server and initialize a scan workflow including report generation:

   .. code:: bash

      $ foss_cli -vv start_workflow --help 
      Usage: foss_cli start_workflow [OPTIONS] FILE_NAME
      The foss_cli start_workflow command.
      Options:
            --folder_name TEXT            The name of the folder to upload to.
            --file_description TEXT       The description of the upload.
            --dry_run / --no_dry_run      Do not upload but show what would be done.
                                          Use -vv to see output.
            --reuse_newest_upload / --no_reuse_newest_upload
                                          Reuse newest upload if available.
            --reuse_newest_job / --no_reuse_newest_job
                                          Reuse newest scheduled job for the upload if
                                          available.
            --report_format TEXT          The name of the reportformat. [dep5,
                                          spdx2,spdxtv,readmeoss,unifiedreport]
            --access_level TEXT           The access level of the
                                          upload.[private,protected,public]
            --help                        Show this message and exit.

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

**HINT**

   To avoid running the whole testsuite during development of a new branch with changing only touching the code related
   to the CLI, name your branch ``feat/cli-{something}`` and only the ``test_foss_cli_*`` will run in the pull request context.

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
---

Each new release gets a new tag with important information about the changes added to the new release:

.. code:: shell

   git tag -a vx.x.x -m "New major/minor/patch release x.x.x"
   git push origin vx.x.x

Add required information in the corresponding `release in the Github project <https://github.com/fossology/fossology-python/releases>`_.

Publish
-------

Publish the newest release to PyPi (visit https://pypi.org/manage/account/#api-tokens to get the token):

.. code:: shell

   poetry publish --build --username __token__ --password $PYPI_TOKEN

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
