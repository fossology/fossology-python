__doc__ = """Test the "workflow" sub commands of foss_cli"""
from pathlib import PurePath

from fossology import foss_cli


#  def test_upload_file(runner):
#      """Test the CLI."""
#      d = {}
#      filepath = "tests/files"
#      filename = "zlib_1.2.11.dfsg-0ubuntu2.debian.tar.xz"
#      q_path = PurePath(filepath, filename)
#      print(f"path {q_path}")
#      result = runner.invoke(
#         foss_cli.cli,
#         [
#         "-vv",
#         "--debug",
#         "upload_file",
#         (q_path),
#         "--reuse_last_upload",
#         "--summary",
#        ],
#        obj=d,
#        catch_exceptions=False,
#      )
#      assert d["VERBOSE"] == 2
#     assert d["DEBUG"]
#     assert d["UPLOAD"].uploadname == filename
#     assert result.exit_code == 0


def test_schedule_jobs(runner):
    """Test the CLI."""
    d = {}
    filepath = "tests/files"
    filename = "zlib_1.2.11.dfsg-0ubuntu2.debian.tar.xz"
    q_path = PurePath(filepath, filename)
    print(f"path {q_path}")
    result = runner.invoke(
        foss_cli.cli,
        ["-vv", "--debug", "schedule_jobs", str(q_path),],
        obj=d,
        catch_exceptions=False,
    )
    assert d["VERBOSE"] == 2
    assert d["DEBUG"]
    assert result.exit_code == 0
