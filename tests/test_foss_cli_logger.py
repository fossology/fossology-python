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

from fossology import foss_cli

TEST_MESSAGE = "This is a Test Message."
TEST_LOG_FILE_NAME = "my.log"
TEST_RESULT_DIR = "test_result_dir"


def test_with_verbosity_0(runner):
    # Should be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["log", "--log_level", "2", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should not be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["log", "--log_level", "1", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE not in result.output
    # Should not be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["log", "--log_level", "0", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE not in result.output


def test_with_verbosity_1(runner):
    # Should be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-v", "log", "--log_level", "2", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should  be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-v", "log", "--log_level", "1", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should not be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-v", "log", "--log_level", "0", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE not in result.output


def test_with_verbosity_2(runner):
    # Should be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "log", "--log_level", "2", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should  be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "log", "--log_level", "1", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output
    # Should  be seen on console
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "log", "--log_level", "0", "--message_text", TEST_MESSAGE],
        obj={},
    )
    assert result.exit_code == 0
    assert TEST_MESSAGE in result.output


# As console and filehandler work the  same way corresponding to verbosity, it suffices to test the
# --log_to_file/log_file_name conceirning output  to the correct file.


def test_log_to_default_file(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(
            foss_cli.cli,
            [
                "--log_to_file",
                "-vv",
                "log",
                "--log_level",
                "2",
                "--message_text",
                TEST_MESSAGE,
            ],
            obj={},
        )
        assert result.exit_code == 0
        filename = os.path.join(
            foss_cli.DEFAULT_RESULT_DIR, foss_cli.DEFAULT_LOG_FILE_NAME
        )
        assert os.path.isfile(filename)
        assert TEST_MESSAGE in open(filename).read()


def test_log_to_userdefined_file(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(
            foss_cli.cli,
            [
                "--log_to_file",
                "-vv",
                "--log_file_name",
                TEST_LOG_FILE_NAME,
                "log",
                "--log_level",
                "2",
                "--message_text",
                TEST_MESSAGE,
            ],
            obj={},
        )
        assert result.exit_code == 0
        filename = os.path.join(foss_cli.DEFAULT_RESULT_DIR, TEST_LOG_FILE_NAME)
        assert os.path.isdir(foss_cli.DEFAULT_RESULT_DIR)
        assert os.path.isfile(filename)
        assert TEST_MESSAGE in open(filename).read()


def test_log_to_userdefined_file_in_userdefined_result_dir(runner):
    with runner.isolated_filesystem():
        result = runner.invoke(
            foss_cli.cli,
            [
                "--log_to_file",
                "-vv",
                "--result_dir",
                TEST_RESULT_DIR,
                "--log_file_name",
                TEST_LOG_FILE_NAME,
                "log",
                "--log_level",
                "2",
                "--message_text",
                TEST_MESSAGE,
            ],
            obj={},
        )
        assert result.exit_code == 0
        filename = os.path.join(TEST_RESULT_DIR, TEST_LOG_FILE_NAME)
        assert os.path.isdir(TEST_RESULT_DIR)
        assert os.path.isfile(filename)
        assert TEST_MESSAGE in open(filename).read()


def test_debug_and_verbosity_is_captured_in_context(runner):
    with runner.isolated_filesystem():
        d = {}
        result = runner.invoke(foss_cli.cli, ["-vv", "--debug", "log",], obj=d,)
        assert result.exit_code == 0
        assert d["VERBOSE"] == 2
        assert d["DEBUG"]
