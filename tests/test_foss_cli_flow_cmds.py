__doc__ = """Test the "workflow" sub commands of foss_cli"""
from pathlib import PurePath

from fossology import foss_cli


def test_upload_file(runner, click_test_file_path, click_test_file):
    """Test the CLI."""
    d = {}
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
    assert d["VERBOSE"] == 2
    assert d["DEBUG"]
    assert d["UPLOAD"].uploadname == click_test_file
    assert result.exit_code == 0
    assert "Summary of Upload" in result.output
    assert "Main License" in result.output
    assert "Total License" in result.output
    assert "totalConcludedLicenses" in result.output
    assert "Files Cleared " in result.output
    assert "CopyRightCount" in result.output
