__doc__ = """Test the "CreateXXX" sub commands of foss_cli"""

from fossology import foss_cli


def test_create_folder(runner, click_test_dict):
    """Test the CLI."""
    d = click_test_dict
    result = runner.invoke(
        foss_cli.cli,
        [
            "-vv",
            "create_folder",
            "AwesomeFolder",
            "--folder_description",
            "Description of Awesome Folder",
        ],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert d["VERBOSE"] == 2


def test_create_group(runner, click_test_dict):
    """Test the CLI."""
    d = click_test_dict
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "create_group", "clearing",],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert d["VERBOSE"] == 2
