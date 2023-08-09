# Copyright 2022 Siemens AG
# SPDX-License-Identifier: MIT

__doc__ = """Test the "workflow" sub commands of foss_cli"""
import configparser
import os
import time
from pathlib import PurePath

from fossology import foss_cli


def test_upload_file(runner, click_test_file_path, click_test_file, click_test_dict):
    """Test the CLI."""
    d = click_test_dict
    q_path = PurePath(click_test_file_path, click_test_file)
    result = runner.invoke(
        foss_cli.cli,
        [
            "-vv",
            "--debug",
            "upload_file",
            str(q_path),
            "--reuse_newest_upload",
            "--summary",
        ],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert d["VERBOSE"] == 2
    assert d["DEBUG"]
    assert d["UPLOAD"].uploadname == click_test_file
    assert "Summary of upload" in result.output
    time.sleep(2)
    result = runner.invoke(
        foss_cli.cli,
        [
            "-vv",
            "delete_upload",
            click_test_file,
        ],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_create_config_file_with_wrong_token_scope_uses_default_read(
    runner, foss_server, click_test_dict
):
    with runner.isolated_filesystem():
        d = click_test_dict
        d["IS_REQUEST_FOR_HELP"] = False
        d["IS_REQUEST_FOR_CONFIG"] = True
        result = runner.invoke(
            foss_cli.cli,
            [
                "-vv",
                "config",
                "--server",
                foss_server,
                "--nointeractive",
                "--password",
                "fossy",
                "--username",
                "fossy",
                "--token_scope",
                "fossy",
            ],
            obj=d,
            catch_exceptions=False,
        )
        print(result.output)
        assert result.exit_code == 0
        assert "New config has been generated" in result.output


def test_create_config_file_and_run_with_it(runner, foss_server, click_test_dict):
    with runner.isolated_filesystem():
        # STEP 1: Create config file
        d = click_test_dict
        d["IS_REQUEST_FOR_CONFIG"] = True
        d["IS_REQUEST_FOR_HELP"] = False
        result = runner.invoke(
            foss_cli.cli,
            [
                "-vv",
                "config",
                "--server",
                foss_server,
                "--password",
                "fossy",
                "--username",
                "fossy",
                "--token_scope",
                "write",
                "--nointeractive",
            ],
            obj=d,
            catch_exceptions=False,
        )
        print(result.output)
        assert result.exit_code == 0
        assert "New config has been generated" in result.output
        assert os.path.exists(foss_cli.DEFAULT_CONFIG_FILE_NAME)
        config = configparser.ConfigParser()
        config.read(f"{foss_cli.DEFAULT_CONFIG_FILE_NAME}")
        assert "FOSSOLOGY" in config.sections()

        assert result.exit_code == 0

        d = click_test_dict
        d["IS_REQUEST_FOR_CONFIG"] = False
        d["IS_REQUEST_FOR_HELP"] = False
        result = runner.invoke(
            foss_cli.cli,
            [
                "--debug",
                "-vv",
                "log",
            ],
            obj=d,
            catch_exceptions=False,
        )
        print(result.output)
        assert result.exit_code == 0
        assert "CONFIG" in d.keys()
        assert "Set server token from configfile" in result.output
