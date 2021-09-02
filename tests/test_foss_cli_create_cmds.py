__doc__ = """Test the "CreateXXX" sub commands of foss_cli"""

import pytest
from fossology import foss_cli


# apply mark to all tests defined in the file
# https://docs.pytest.org/en/latest/example/markers.html#mark-examples
pytestmark = pytest.mark.foss_cli


def test_CreateFolder(runner):
    """Test the CLI."""
    result = runner.invoke(
        foss_cli.cli,
        [
            "CreateFolder",
            "--folder_name",
            "AwesomeFolder",
            "--folder_description",
            "Description of Awesome Folder",
        ],
        obj={},
    )
    assert result.exit_code == 0
