__doc__ = """Test the "CreateXXX" sub commands of foss_cli"""

from fossology import foss_cli


def test_create_folder(runner):
    """Test the CLI."""
    d = {}
    result = runner.invoke(
        foss_cli.cli,
        [
            "-vv",
            "create_folder",
            "--folder_name",
            "AwesomeFolder",
            "--folder_description",
            "Description of Awesome Folder",
        ],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert d["VERBOSE"] == 2


def test_create_group(runner):
    """Test the CLI."""
    d = {}
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "create_group", "clearing",],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert d["VERBOSE"] == 2
