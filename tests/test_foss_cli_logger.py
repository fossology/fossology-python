__doc__ = """Test the logging of the foss_cli
           foss_cli distinguishes the verbosity levels 0,1,2
           defined in foss_cli.py
              FOSS_LOGGING_MAP = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
           and set with:
              logger.setLevel(FOSS_LOGGING_MAP.get(verbose, logging.DEBUG))
           in the cli main command.
           The Log command uses:
               Log --log-level 0  ==> logger.debug
               Log --log-level 1  ==> logger.info
               Log --log-level 2  ==> logger.warning
"""

import os

import pytest
from fossology import foss_cli

TEST_MESSAGE = "This is a Test Message."
DEFAULT_LOG_FILE_NAME = ".foss_cli.log"
TEST_LOG_FILE_NAME = "my.log"


@pytest.mark.foss_cli
def test_global_zero(runner):
    """Test with global verbosity level 0."""
    # Should be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["Log", "--log_level", "2", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should not be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["Log", "--log_level", "1", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE not in result.output
    # Should not be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["Log", "--log_level", "0", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE not in result.output


@pytest.mark.foss_cli
def test_global_one(runner):
    """Test with global verbosity level 1."""
    # Should be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-v", "Log", "--log_level", "2", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should  be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-v", "Log", "--log_level", "1", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should not be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-v", "Log", "--log_level", "0", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE not in result.output


@pytest.mark.foss_cli
def test_global_two(runner):
    """Test with global verbosity level 2."""
    # Should be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "Log", "--log_level", "2", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should  be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "Log", "--log_level", "1", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should  be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "Log", "--log_level", "0", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output


# As console and filehandler work the  same way corresponding to verbosity, it suffices to test the
# --log_to_file/log_file_name conceirning output  to the correct file.


@pytest.mark.foss_cli
def test_log_to_default_file(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(
            foss_cli.cli,
            [
                "--log_to_file",
                "-vv",
                "Log",
                "--log_level",
                "2",
                "--message_text",
                TEST_MESSAGE,
            ],
            obj={},
        )
        assert result.exit_code == 0
        assert os.path.isfile(DEFAULT_LOG_FILE_NAME)
        assert TEST_MESSAGE in open(DEFAULT_LOG_FILE_NAME).read()


@pytest.mark.foss_cli
def test_log_to_userdefined_file(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(
            foss_cli.cli,
            [
                "--log_to_file",
                "-vv",
                "--log_file_name",
                TEST_LOG_FILE_NAME,
                "Log",
                "--log_level",
                "2",
                "--message_text",
                TEST_MESSAGE,
            ],
            obj={},
        )
        assert result.exit_code == 0
        assert os.path.isfile(TEST_LOG_FILE_NAME)
        assert TEST_MESSAGE in open(TEST_LOG_FILE_NAME).read()
