__doc__ = """
        The foss_cli cmdline interface uses the provided REST-API to communicate
        with the Fossology Server.
        Logging is implemented using the standard python logging framework.
        Log Level can be adapted using the -v/-vv option to foss_cli.
        Logging could be sent to console (option --log_to_file) and/or to a log_file
        (option --log_to_file). The name of the log_file (default is .foss_cli.log)
        could be adapted using the option --log_file_name <filename>.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import click

from fossology import Fossology

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

FOSS_LOGGING_MAP = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
MAX_SIZE_OF_LOGFILE = 200000
MAX_NUMBER_OF_LOGFILES = 5


def init_foss(ctx):
    if ctx.obj["TOKEN"] is None:
        try:
            ctx.obj["TOKEN"] = os.environ["FOSS_TOKEN"]
        except Exception as e:
            logger.fatal(
                "No Token provided. Either provide FOSS_TOKEN in environment or use the -t option."
            )
            raise e
    if "FOSS" not in ctx.obj.keys():
        foss = Fossology(ctx.obj["SERVER"], ctx.obj["TOKEN"])
        ctx.obj["FOSS"] = foss
        ctx.obj["USER"] = foss.user.name
        logger.info(f"Logged in as user {foss.user.name}")
    return ctx.obj["FOSS"]


@click.group()
@click.option("--token", "-t", help="token to be used.")
@click.option("--server", "-s", default="http://fossology/repo", help="url of server.")
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity level (e.g. -v -vv). Default is 0.",
)
@click.option(
    "--log_to_console/--no_log_to_console",
    is_flag=True,
    default=True,  # print logging events >= WARNING by default on console
    help="Send logging output to console. Default is --log_to_console.",
)
@click.option(
    "--log_to_file/--no_log_to_file",
    is_flag=True,
    default=False,
    help="Send logging output to File. Default is --no_log_to_file.",
)
@click.option(
    "--log_file_name",
    default=".foss_cli.log",
    help="Specify log File Name if log is sent to file.  Default is .foss_cli.log.",
)
@click.pass_context
def cli(ctx, server, token, verbose, log_to_console, log_to_file, log_file_name):
    """The fossology cmdline client. \n
       - foss_cli    ==>  verbosity = 0 \n
       - foss_cli  -v  ==>  verbosity = 1  \n
       - foss_cli  -vv  ==>  verbosity =  2 \n
    """
    group_commands = ["Log", "CreateFolder", "CreateGroup"]  # noqa: F841
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    if log_to_file:
        logfile_handler = RotatingFileHandler(
            log_file_name,
            maxBytes=MAX_SIZE_OF_LOGFILE,
            backupCount=MAX_NUMBER_OF_LOGFILES,
        )
        logfile_handler.setFormatter(formatter)
        logger.addHandler(logfile_handler)
    logger.setLevel(FOSS_LOGGING_MAP.get(verbose, logging.DEBUG))
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["SERVER"] = server
    ctx.obj["TOKEN"] = token


@cli.command("Log")
@click.option(
    "--log_level", default=0, help="Set the log_level of the message [0,1,2]."
)
@click.option("--message_text", default="log message", help="Text of the log message.")
@click.pass_context
def Log(ctx, log_level, message_text):
    """Add a Log Message to the log.  If a log message is printed to the log depends
       on  the verbosity defined starting the foss_cli (default level 0 /-v level 1/-vv level 2).
       Beeing on global verbosity level 0 only messages of --log_level 2 will be printed.
       Beeing on global verbosity level 1  messages of --log_level 1 and 2 will be printed.
       Beeing on global verbosity level 2 messages of --log_level 0,1,2 will be printed.
       Where the log messages are printed depends on the global configuration for --log_to_console,
       --log_to_file and --log_file_name.
    """

    if log_level == 0:
        logger.debug(message_text)
    elif log_level == 1:
        logger.info(message_text)
    elif log_level == 2:
        logger.warning(message_text)
    else:
        error_text = "Impossible Log Level in Log command."
        logger.fatal(error_text)
        raise click.UsageError(error_text, ctx=ctx)


@cli.command("CreateFolder")
@click.option("--folder_name", help="The name of the folder.")
@click.option("--folder_description", help="Description of the Folder.")
@click.option("--folder_group", help="Name of the Group owning the Folder.")
@click.pass_context
def CreateFolder(ctx, folder_name, folder_description, folder_group):
    """The fossology CreateFolder command."""

    ctx.obj["FOLDER_NAME"] = folder_name
    ctx.obj["FOLDER_DESCRIPTION"] = folder_description
    ctx.obj["FOLDER_GROUP"] = folder_group
    foss = init_foss(ctx)
    folder = foss.create_folder(
        foss.rootFolder, folder_name, description=folder_description, group=folder_group
    )

    message = f"Folder {folder.name} with description {folder.description} created"
    logger.info(message)
    click.echo(message)


@cli.command("CreateGroup")
@click.option("--bla1", help="bla1 help.")
@click.option("--bla2", help="bla2 help.")
@click.pass_context
def CreateGroup(ctx, bla1, bla2):
    """The fossology CreateGroup command."""
    ctx.obj["FOSS"] = init_foss(ctx)
    foss = ctx.obj["FOSS"]
    click.echo(f"Logged in as user {foss.user.name}")


def main():
    cli(obj={})  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
