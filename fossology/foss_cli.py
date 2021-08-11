import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import click
import time
from fossology import Fossology

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

FOSS_LOGGING_MAP = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}


def init_foss(ctx):
    if ctx.obj["TOKEN"] == None:
        try:
            ctx.obj["TOKEN"] = os.environ["FOSS_TOKEN"]
        except Exception as e:
            logger.fatal("No Token provided. Either provide FOSS_TOKEN in environment or use the -t option.")
            raise e
    foss = Fossology(ctx.obj["SERVER"], ctx.obj["TOKEN"])
    logger.info(f"Logged in as user {foss.user.name}")
    return foss


@click.group()
@click.option("--token", "-t", help="token to be used.")
@click.option("--server", "-s", default="http://fossology/repo", help="url of server.")
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase logging verbosity level (e.g. -v -vv -vvv).",
)
@click.option(
    "--log_to_console",
    is_flag=True,
    default=True,
    help="Send logging output to console.",
)
@click.option(
    "--log_to_file", is_flag=True, default=False, help="Send logging output to File."
)
@click.option(
    "--log_file_name",
    default=".foss_cli.log",
    help="Specify log File Name if log is sent to file.",
)
@click.pass_context
def cli(ctx, server, token, verbose, log_to_console, log_to_file, log_file_name):
    group_commands = ["CreateFolder", "CreateGroup"]
    """The fossology cmdline client."""
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    if log_to_file:
        logfile_handler = RotatingFileHandler(
            log_file_name, maxBytes=2000000, backupCount=5
        )
        logfile_handler.setFormatter(formatter)
        logger.addHandler(logfile_handler)
    logger.setLevel(FOSS_LOGGING_MAP.get(verbose, logging.DEBUG))
    logger.warning("Always seen")
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["SERVER"] = server
    ctx.obj["TOKEN"] = token


@cli.command("CreateFolder")
@click.option("--bla1", help="bla1 help.")
@click.option("--bla2", help="bla2 help.")
@click.pass_context
def CreateFolder(ctx, bla1, bla2):
    """The fossology CreateFolder cmdline client."""
    if '--help' in click.get_os_args(): return
    click.echo("subbing")
    ctx.obj["FOSS"] = init_foss(ctx)
    foss = ctx.obj["FOSS"]
    click.echo(f"Logged in as user {foss.user.name}")


@cli.command("CreateGroup")
@click.option("--bla1", help="bla1 help.")
@click.option("--bla2", help="bla2 help.")
@click.pass_context
def CreateGroup(ctx, bla1, bla2):
    """The fossology CreateGroup cmdline client."""
    click.echo("subbing")
    if '--help' in click.get_os_args(): return
    if ctx.obj["DEBUG"]:
        click.echo(f"Debug mode is 'on' ")
    ctx.obj["FOSS"] = init_foss(ctx)
    foss = ctx.obj["FOSS"]
    click.echo(f"Logged in as user {foss.user.name}")


def main():
    cli(obj={})  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
