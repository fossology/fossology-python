__doc__ = """Test the "help" text of the different sub commands of foss_cli"""

from fossology import foss_cli


def test_smoke(runner):
    """Test the CLI."""
    result = runner.invoke(foss_cli.cli, None, obj={})
    assert result.exit_code == 0


def test_help_on_top_level(runner):
    help_result = runner.invoke(foss_cli.cli, ["--help"], obj={})
    assert help_result.exit_code == 0
    print(help_result.output)
    assert "--help  ".replace(" ", "") in help_result.output.replace(" ", "")
    assert "-t, --token TEXT ".replace(" ", "") in help_result.output.replace(" ", "")
    assert "-s, --server TEXT".replace(" ", "") in help_result.output.replace(" ", "")
    assert "-u, --username TEXT".replace(" ", "") in help_result.output.replace(" ", "")
    assert "-v, --verbose ".replace(" ", "") in help_result.output.replace(" ", "")
    assert (
        "--log_to_console ".replace(" ", "")
        in help_result.output.replace(" ", "").strip()
    )
    assert "--log_to_file / --no_log_to_file".replace(
        " ", ""
    ) in help_result.output.replace(" ", "")
    assert "--log_file_name TEXT".replace(" ", "") in help_result.output.replace(
        " ", ""
    )
    assert "Commands".replace(" ", "") in help_result.output.replace(" ", "")
    assert "CreateFolder".replace(" ", "") in help_result.output.replace(" ", "")
    assert "CreateGroup ".replace(" ", "") in help_result.output.replace(" ", "")
    assert " Log ".replace(" ", "") in help_result.output.replace(" ", "")


def test_help_on_Log(runner):
    help_result = runner.invoke(foss_cli.cli, ["Log", "--help"], obj={})
    assert help_result.exit_code == 0
    assert "--log_level INTEGER".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--message_text TEXT".replace(" ", "") in help_result.output.replace(" ", "")


def test_help_on_CreateFolder(runner):
    help_result = runner.invoke(foss_cli.cli, ["CreateFolder", "--help"], obj={})
    assert help_result.exit_code == 0
    assert "--folder_name TEXT".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--folder_description TEXT".replace(" ", "") in help_result.output.replace(
        " ", ""
    )
    assert "--folder_group TEXT".replace(" ", "") in help_result.output.replace(" ", "")


def test_help_on_CreateGroup(runner):
    help_result = runner.invoke(foss_cli.cli, ["CreateGroup", "--help"], obj={})
    assert help_result.exit_code == 0
