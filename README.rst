|License| |PyPI Version| |Python Version| |Downloads| |Static Checks| |Fossology Tests| |Coverage|

.. |License| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://github.com/fossology/fossology-python/blob/main/LICENSE.md

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

Current release is compatible with **Fossology version 4.7.1** - API version 1.6.2 (not all endpoints are supported)

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

      $ foss_cli -vv upload_file tests/files/base-files_10.3-debian10-test.tar.bz2 \
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
                                          spdx2,spdxtv,readmeoss,unifiedreport,
                                          clixml,spdx3json,spdx3rdf,spdx3jsonld]
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

-  Extend the testsuite **uv run pytest** with the new functions/classes

-  The **documentation website** can automatically be generated by the `Sphinx autodoc
   extension <http://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_

**HINT**

   To avoid running the whole testsuite during development of a new branch with changing only touching the code related
   to the CLI, name your branch ``feat/cli-{something}`` and only the ``test_foss_cli_*`` will run in the pull request context.

**Testing Requirements for New Code**

   When contributing new features or API extensions, ensure comprehensive test coverage using these guidelines:

   -  **Unit Tests with Responses Framework**: Use the `responses <https://github.com/getsentry/responses>`_ library
      to mock HTTP requests and provide unit test coverage for all code paths. This allows fast, isolated testing without
      requiring a running Fossology instance. See existing tests in ``tests/`` directory for examples of the
      ``@responses.activate`` decorator pattern.

   -  **Integration Tests**: Provide at least one generic integration test that runs against an actual Fossology instance.
      These tests validate real API behavior and can be executed:

      - **Locally**: Run against a Fossology Docker container (see the Test section below for setup instructions)
      - **In CI/CD**: Tests automatically run via GitHub Actions in the `API Tests job
        <https://github.com/fossology/fossology-python/.github/workflows/fossologytests.yml>`_

   -  **Coverage Requirements**: All new code paths must be covered by tests. Pull requests without adequate test
      coverage will not be accepted. Use ``uv run coverage`` to verify coverage locally.

**Static Checks**

   Before submitting your pull request, ensure your code passes all static checks:

   -  **Linting with Ruff**: Check code style and quality:

      .. code:: shell

         uv run ruff check

   -  **Type Checking with Mypy**: Verify type annotations:

      .. code:: shell

         uv run poe types

   -  **Run All Checks**: You can run the complete static checks suite locally:

      .. code:: shell

         uv sync --all-extras
         uv run ruff check
         uv run poe types

   These checks are automatically run on every pull request via GitHub Actions (`Static Checks
   <https://github.com/fossology/fossology-python/actions/workflows/staticchecks.yml>`_).

**Commit Message Format**

   All commits should include appropriate footers in the commit message body:

   -  **Signed-off-by**: Required for all commits. Use ``git commit -s`` to add automatically:

      .. code:: shell

         Signed-off-by: Your Name <your.email@example.com>

   -  **Assisted-by** (AI-assisted work): If you used AI coding tools to generate this commit,
      include the tool and model information:

      .. code:: shell

         Assisted-by: GitHub Copilot (Claude Haiku 4.5)

   Example commit with both footers:

   .. code:: shell

      git commit -m "feat: implement new API endpoint

      Add support for the /v2/inventory endpoint with comprehensive test coverage.

      Signed-off-by: Jane Doe <jane@example.com>
      Assisted-by: GitHub Copilot (Claude Haiku 4.5)"

**AI-Assisted Contributions**

   AI coding agents are active in this repository. If you are an AI agent or using AI-assisted tooling,
   please follow these guidelines:

   -  **Do not pollute the issue tracker** with lengthy explanations for simple fixes or API extensions.
      The issue tracker is reserved for discussing significant design decisions and feature proposals.

   -  **Keep pull requests concise.** The maintainers do not need a full report of every change — the
      code speaks for itself. Minimize verbose descriptions and auto-generated summaries.

   -  **All new extensions must include test cases.** Every new feature or API extension must be properly
      covered by tests that provide confidence in the patch. Pull requests without adequate test coverage
      will not be accepted.

   -  **Include Assisted-by footer** in commit messages. This documents which AI tool generated the commit,
      improving transparency and traceability. Example: ``Assisted-by: GitHub Copilot (Claude Haiku 4.5)``

Check API Coverage
------------------

A helper script is available to measure how much of the Fossology REST API is
covered by this library.  It fetches the official OpenAPI spec and compares
every endpoint against the ``API Endpoint:`` annotations in the source
docstrings:

.. code:: shell

   python check_api_coverage.py

By default the upstream spec on GitHub is used. You can also point it at a
local file or a running Fossology instance:

.. code:: shell

   # Local spec file
   python check_api_coverage.py --spec /path/to/openapi.yaml

   # Live Fossology instance
   python check_api_coverage.py --spec http://fossology/repo/api/v1/openapi

The script prints a summary table, a list of not-yet-implemented endpoints, and
any endpoints documented in the wrapper that are absent from the spec.

Build
-----

- You can build the PyPi package using standard Python build tools:

  .. code:: shell

    uv build

- Build documentation:

  The static site is generated automatically by
  `GitHub Actions <https://github.com/fossology/fossology-python/actions/workflows/doc-deploy.yml>`_
  on every merge to main branch and pushed to **gh-pages** branch. The action uses
  `JamesIves/github-pages-deploy-action <https://github.com/JamesIves/github-pages-deploy-action>`_
  to deploy the static pages.

  To build it locally

  .. code:: shell

     uv run sphinx-build -b html docs-source docs/

- Cleanup builds:

  .. code:: shell

     rm -r dist/ docs/

Tag
---

Releases are automatically managed by `Semantic Release <https://python-semantic-release.readthedocs.io/>`_ 
via GitHub Actions. The version and tag are determined from commit messages using the following scheme:

**Semantic Commit Message Format**

-  ``fix: ...`` → Patch version bump (1.0.0 → 1.0.1)
-  ``feat: ...`` → Minor version bump (1.0.0 → 1.1.0)
-  ``feat!: ...`` or ``BREAKING CHANGE: ...`` → **Major version bump** (1.0.0 → 2.0.0)

**To Trigger a Major Release**

Use the breaking change format in your commit message:

.. code:: shell

   git commit -m "feat(api)!: redesign authentication system"

Or include a footer:

.. code:: shell

   git commit -m "feat: update core endpoints

   BREAKING CHANGE: The /v1 endpoints are no longer supported. Use /v2 instead."

When merged to main, semantic-release will automatically:

-  Detect the breaking change
-  Bump the major version
-  Generate release notes from commit messages
-  Create a GitHub release
-  Build and publish to PyPI

Publish
-------

Publishing to PyPI is **automatically handled by Semantic Release** on every merge to main. 
No manual steps are required once your PR is merged.

The automated workflow (see `.github/workflows/semantic-release.yml 
<https://github.com/fossology/fossology-python/actions/workflows/semantic-release.yml>`_):

-  Detects version changes from commit messages
-  Builds the package with ``uv build``
-  Publishes to PyPI using trusted publishing (no token needed)
-  Creates a GitHub Release with auto-generated changelog

Test
----

The testsuite available in this project expects a running Fossology instance under the hostname **fossology** with the default admin user "fossy".

- Use the latest Fossology container from `Docker hub <https://hub.docker.com/r/fossology/fossology>`_:

  .. code:: shell

    docker pull fossology/fossology
    tar xvf tests/files/base-files_10.3-debian10-test.tar.bz2 -C /tmp
    chmod a+r /tmp/base-files-10.3
    docker run --mount src="/tmp",dst=/tmp,type=bind --name fossology -p 80:80 fossology/fossology

- Start the complete test suite or a specific test case (and generate coverage report):

  .. code:: shell

     uv run coverage run --source=fossology -m pytest
     uv run coverage report -m
     uv run coverage html
