"""Tests for `python_boilerplate` package."""

import pytest

from click.testing import CliRunner
from fossology import foss_cli 






def test_smoke(runner):
    """Test the CLI."""
    result = runner.invoke(foss_cli.cli,None,obj={})
    assert result.exit_code == 0


def test_help_on_top_level(runner):
    help_result = runner.invoke(foss_cli.cli, ['--help'], obj={})
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.'.replace(" ","") in help_result.output.replace(" ","")
    assert '-t, --token TEXT      token to be used.'.replace(" ","") in help_result.output.replace(" ","")
    assert '-s, --server TEXT     url of server.'.replace(" ","") in help_result.output.replace(" ","")
    assert '-v, --verbose         Increase logging verbosity level (e.g. -v -vv -vvv).'.replace(" ","") in help_result.output.replace(" ","")
    assert '--log_to_console      Send logging output to console.'.replace(" ","") in help_result.output.replace(" ","")
    assert '--log_to_file         Send logging output to File.'.replace(" ","") in help_result.output.replace(" ","")
    assert '--log_file_name TEXT  Specify log File Name if log is sent to file.'.replace(" ","") in help_result.output.replace(" ","")
    assert '--help                Show this message and exit.'.replace(" ","") in help_result.output.replace(" ","")
    assert 'Commands'.replace(" ","") in help_result.output.replace(" ","")
    assert 'CreateFolder  The fossology CreateFolder cmdline client.'.replace(" ","") in help_result.output.replace(" ","")
    assert 'CreateGroup   The fossology CreateGroup cmdline client.'.replace(" ","") in help_result.output.replace(" ","")


def test_help_on_CreateFolder(runner):
    help_result = runner.invoke(foss_cli.cli, ['CreateFolder','--help'], obj={})
    
    assert help_result.exit_code == 0

def test_help_on_CreateGroup(runner):
    help_result = runner.invoke(foss_cli.cli, ['CreateGroup','--help'], obj={})
    assert help_result.exit_code == 0


