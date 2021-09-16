from fossology import foss_cli
from pathlib import PurePath


def test_schedule_jobs_calling_with_wrong_report_format_exits_with_1(
    runner, click_test_file_path, click_test_file, click_test_dict
):
    d = click_test_dict
    q_path = PurePath(click_test_file_path, click_test_file)
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "schedule_jobs", str(q_path), "--report_format", "imp"],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert "Impossible report format imp" in result.output


def test_schedule_jobs_calling_with_wrong_access_level_exits_with_1(
    runner, click_test_file_path, click_test_file, click_test_dict
):
    d = click_test_dict
    q_path = PurePath(click_test_file_path, click_test_file)
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "schedule_jobs", str(q_path), "--access_level", "imp"],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert "Impossible access level imp" in result.output


def test_schedule_jobs_a_dry_run_without_reuse_newest_upload_always_exits_with_1(
    runner, click_test_file_path, click_test_file, click_test_dict
):
    d = click_test_dict
    q_path = PurePath(click_test_file_path, click_test_file)
    result = runner.invoke(
        foss_cli.cli,
        [
            "-vv",
            "--debug",
            "schedule_jobs",
            str(q_path),
            "--access_level",
            "public",
            "--dry_run",
        ],
        obj=d,
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    assert "Skip upload as dry_run is requested" in result.output
    assert f"Unable to find upload for {str(q_path)}" in result.output


def test_schedule_jobs_reuse_newest_job(
    runner, click_test_file_path, click_test_file, click_test_dict
):
    d = click_test_dict
    # first upload  is the initial one
    #  - it uploads
    #  - it triggers a job on the upload
    q_path = PurePath(click_test_file_path, click_test_file)
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "--debug", "schedule_jobs", str(q_path), "--access_level", "public",],
        obj=d,
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert f"Initiate new upload for {str(q_path)}" in result.output
    assert f"Finished upload for {str(q_path)}" in result.output
    assert "Scheduled new job" in result.output

    # second upload  is able to reuse
    #   --reuse_newest_upload
    #   --reuse_newest_job
    d = click_test_dict
    result = runner.invoke(
        foss_cli.cli,
        [
            "-vv",
            "--debug",
            "schedule_jobs",
            str(q_path),
            "--access_level",
            "public",
            "--reuse_newest_upload",
            "--reuse_newest_job",
        ],
        obj=d,
        catch_exceptions=False,
    )
    assert f"Can reuse upload for {click_test_file}" in result.output
    assert f"Can reuse old job on Upload {click_test_file}" in result.output
    assert "Generated report" in result.output
    assert "Report downloaded" in result.output
    assert "Report written to file: " in result.output
    assert result.exit_code == 0
