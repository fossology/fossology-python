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
    assert "--debug/ --no_debug".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--debug/ --no_debug".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--log_file_name TEXT".replace(" ", "") in help_result.output.replace(
        " ", ""
    )
    assert "Commands".replace(" ", "") in help_result.output.replace(" ", "")
    assert "create_folder".replace(" ", "") in help_result.output.replace(" ", "")
    assert "create_group ".replace(" ", "") in help_result.output.replace(" ", "")
    assert " log ".replace(" ", "") in help_result.output.replace(" ", "")
    assert " upload_file ".replace(" ", "") in help_result.output.replace(" ", "")


def test_help_on_log(runner):
    help_result = runner.invoke(foss_cli.cli, ["log", "--help"], obj={})
    assert help_result.exit_code == 0
    assert "--log_level INTEGER".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--message_text TEXT".replace(" ", "") in help_result.output.replace(" ", "")


def test_help_on_create_folder(runner):
    help_result = runner.invoke(foss_cli.cli, ["create_folder", "--help"], obj={})
    assert help_result.exit_code == 0
    assert "--folder_name TEXT".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--folder_description TEXT".replace(" ", "") in help_result.output.replace(
        " ", ""
    )
    assert "--folder_group TEXT".replace(" ", "") in help_result.output.replace(" ", "")


def test_help_on_create_group(runner):
    help_result = runner.invoke(foss_cli.cli, ["create_group", "--help"], obj={})
    assert help_result.exit_code == 0


def test_help_on_upload_file(runner):
    help_result = runner.invoke(foss_cli.cli, ["upload_file", "--help"], obj={})
    assert "--folder_name TEXT".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--description TEXT".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--access_level TEXT".replace(" ", "") in help_result.output.replace(" ", "")
    assert "--summary/ --no_summary".replace(" ", "") in help_result.output.replace(
        " ", ""
    )
    assert "--reuse_last_upload/ --no_reuse_last_upload".replace(
        " ", ""
    ) in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0
