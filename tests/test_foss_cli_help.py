__doc__ = """Test the "help" text of the different sub commands of foss_cli"""

from fossology import foss_cli


def test_smoke(runner):
    """Test the CLI."""
    result = runner.invoke(foss_cli.cli, None, obj={})
    assert result.exit_code == 0


def test_help_on_top_level(runner, click_test_dict):
    d = click_test_dict
    d["IS_REQUEST_FOR_HELP"] = True

    cmds = [
        "cli [OPTIONS] COMMAND [ARGS]...",
        "-t, --token TEXT ",
        " -v, --verbose",
        " --log_to_console / --no_log_to_console",
        " --log_to_file / --no_log_to_file",
        " --log_file_name TEXT",
        " --debug / --no_debug",
        " --result_dir TEXT",
        " --help ",
        "Commands:",
        "create_folder",
        "create_group",
        "log",
        "upload_file",
        "schedule_jobs",
    ]
    help_result = runner.invoke(foss_cli.cli, ["--help"], obj=d)
    for cmd in cmds:
        assert cmd.replace(" ", "") in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0


def test_help_foss_config(runner, click_test_dict):
    d = click_test_dict
    d["IS_REQUEST_FOR_HELP"] = True
    cmds = [
        "Create a foss_cli config file.",
    ]
    help_result = runner.invoke(foss_cli.cli, ["config", "--help"], obj=d)
    for cmd in cmds:
        assert cmd.replace(" ", "") in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0


def test_help_on_log(runner, click_test_dict):
    d = click_test_dict
    d["IS_REQUEST_FOR_HELP"] = True
    cmds = [
        "log [OPTIONS]",
        "--log_level INTEGER ",
        "--message_text TEXT",
        "--help",
    ]
    help_result = runner.invoke(foss_cli.cli, ["log", "--help"], obj=d)
    for cmd in cmds:
        assert cmd.replace(" ", "") in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0


def test_help_on_create_folder(runner, click_test_dict):
    d = click_test_dict
    d["IS_REQUEST_FOR_HELP"] = True
    cmds = [
        "create_folder [OPTIONS] FOLDER_NAME",
        "--folder_description TEXT",
        "--folder_group TEXT",
        "--help",
    ]
    help_result = runner.invoke(foss_cli.cli, ["create_folder", "--help"], obj=d)
    for cmd in cmds:
        assert cmd.replace(" ", "") in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0


def test_help_on_create_group(runner, click_test_dict):
    d = click_test_dict
    d["IS_REQUEST_FOR_HELP"] = True
    cmds = [
        "create_group [OPTIONS] GROUP_NAME",
        "--help",
    ]
    help_result = runner.invoke(foss_cli.cli, ["create_group", "--help"], obj=d)
    for cmd in cmds:
        assert cmd.replace(" ", "") in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0


def test_help_on_upload_file(runner, click_test_dict):
    d = click_test_dict
    d["IS_REQUEST_FOR_HELP"] = True
    cmds = [
        "upload_file [OPTIONS] UPLOAD_FILE",
        "--folder_name TEXT",
        "--description TEXT",
        "--access_level TEXT",
        "--summary/ --no_summary",
        "--reuse_newest_upload/ --no_reuse_newest_upload",
        "--help",
    ]
    help_result = runner.invoke(foss_cli.cli, ["upload_file", "--help"], obj=d)
    for cmd in cmds:
        assert cmd.replace(" ", "") in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0


def test_help_on_schedule_jobs(runner, click_test_dict):
    d = click_test_dict
    d["IS_REQUEST_FOR_HELP"] = True
    cmds = [
        "schedule_jobs [OPTIONS] FILE_NAME",
        "--folder_name TEXT",
        "--file_description TEXT",
        "--reuse_newest_upload / --no_reuse_newest_upload",
        "--reuse_newest_job/ --no_reuse_newest_job",
        "--report_format TEXT",
        "--access_level TEXT",
        "--help",
    ]
    help_result = runner.invoke(foss_cli.cli, ["schedule_jobs", "--help"], obj=d)
    for cmd in cmds:
        assert cmd.replace(" ", "") in help_result.output.replace(" ", "")
    assert help_result.exit_code == 0
