# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

__doc__ = """
        The foss_cli cmdline interface uses the provided REST-API to communicate
        with the Fossology Server.
        Logging is implemented using the standard python logging framework.
        Log Level can be adapted using the -v/-vv option to foss_cli.
        Logging could be sent to console (option --log_to_file) and/or to a log_file
        (option --log_to_file). The name of the log_file (default is .foss_cli.log)
        could be adapted using the option --log_file_name <filename>.
"""
import configparser
import logging
import os
import pathlib
import pprint
import secrets
import sys
from getpass import getpass
from logging.handlers import RotatingFileHandler

import click

from fossology import Fossology, fossology_token
from fossology.enums import AccessLevel, ReportFormat, TokenScope
from fossology.exceptions import FossologyApiError, FossologyUnsupported
from fossology.obj import Folder, Summary

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

FOSS_LOGGING_MAP = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
MAX_SIZE_OF_LOGFILE = 200000
MAX_NUMBER_OF_LOGFILES = 5

DEFAULT_LOG_FILE_NAME = ".foss_cli.log"
DEFAULT_RESULT_DIR = ".foss_cli_results"
DEFAULT_CONFIG_FILE_NAME = ".foss_cli.ini"

JOB_SPEC = {
    "analysis": {
        "bucket": True,
        "copyright_email_author": True,
        "ecc": True,
        "keyword": True,
        "mime": True,
        "monk": True,
        "nomos": True,
        "ojo": True,
        "package": True,
        "specific_agent": True,
    },
    "decider": {
        "nomos_monk": True,
        "bulk_reused": True,
        "new_scanner": True,
        "ojo_decider": True,
    },
    "reuse": {
        "reuse_upload": 0,
        "reuse_group": 0,
        "reuse_main": True,
        "reuse_enhanced": True,
        "reuse_report": True,
        "reuse_copyright": True,
    },
}


def check_get_folder(ctx: click.Context, folder_name: str):
    """Get a Folder Instance based on the Folders name.

    :param ctx: click context
    :param folder_name: the name of the folder
    :type ctx: click.core.Context
    :type folder_name: str
    :return: the requested Folder
    :rtype: Folder()
    :raises FossologyUnsupported: if folder_name is (not or multiple times) found.
    """
    folder_to_use = None
    foss = ctx.obj["FOSS"]
    if folder_name == "":
        logger.warning(
            "folder_name not specified - upload will be to the Fossology Root folder."
        )
        folder_to_use = foss.rootFolder
    else:
        for a_folder in foss.folders:
            if a_folder.name == folder_name:
                logger.debug(f"Found upload folder {folder_name} with id {a_folder.id}")
                if folder_to_use is None:
                    folder_to_use = a_folder
                else:
                    description = "Multiple Folders with same name are not supported."
                    raise FossologyUnsupported(description)
        if folder_to_use is None:
            description = f"Requested Upload Folder {folder_name} does not exist."
            raise FossologyUnsupported(description)
    assert isinstance(folder_to_use, Folder)
    return folder_to_use


def check_get_report_format(format: str):
    """Check if the  given format is a valid ReportFormat value.

    :param format: name of a ReportFormat
    :type format: str
    :return: ReportFormat
    :rtype: Enum
    """
    for member in ReportFormat:
        if member.value == format:
            return member
    logger.fatal(f"Impossible report format {format}")
    sys.exit(1)


def check_get_access_level(level: str):
    """Check if the given level is a valid AccessLevel value.

    :param level: name of a Access level
    :type:  str
    :return: AccessLevel
    :rtype: Enum
    """
    for member in AccessLevel:
        if member.value == level:
            return member
    logger.fatal(f"Impossible access level {level}")
    sys.exit(1)


def needs_later_initialization_of_foss_instance(ctx: click.Context):
    """Check if later on a Fossology Instance will be created.

    :param ctx: click context
    :type ctx: click.core.Context
    :return: Indicator
    :rtype: bool

    """
    logger.debug(
        f"Function needs_later_initialization_of_foss_instance called {pprint.pformat(ctx.obj)}"
    )
    if ctx.obj["IS_REQUEST_FOR_HELP"] or ctx.obj["IS_REQUEST_FOR_CONFIG"]:
        return False
    return True


def get_newest_upload_of_file(ctx: click.Context, filename: str, folder_name: str):
    """Given a  filename and folder_name return the newest upload if available.

    :param ctx: click Context
    :param filename: str
    :param folder_name: str
    :type ctx: click.core.Context
    :type filename: str
    :type folder_name: str
    :return: Upload Instance or None
    :rtype: Upload or None
    """

    foss = ctx.obj["FOSS"]
    the_uploads, _ = foss.list_uploads(
        folder=folder_name if folder_name else foss.rootFolder,
    )
    found = None
    newest_date = "0000-09-05 13:25:38.079869+00"
    for a_upload in the_uploads:
        if filename.endswith(a_upload.uploadname):
            if a_upload.uploaddate > newest_date:
                newest_date = a_upload.uploaddate
                found = a_upload
    if found:
        the_upload = foss.detail_upload(a_upload.id)
        logger.info(
            f"Can reuse upload for {a_upload.uploadname}. The uploads id is {a_upload.id}."
        )
        assert a_upload.id == the_upload.id
        return the_upload
    else:
        return None


def init_foss(ctx: click.Context):
    """Initialize a Fossology Instance and store it in the context.

    :param ctx: click Context
    :type ctx: click.core.Context
    :raises e: KeyError Bearer TOKEN not set in environment
    :return: foss_instance
    :rtype: Fossology
    """
    logger.debug("INIT FOSS")
    if os.path.exists(DEFAULT_CONFIG_FILE_NAME):
        config = configparser.ConfigParser()
        ctx.obj["CONFIG"] = config
        config.read(DEFAULT_CONFIG_FILE_NAME)
        assert "FOSSOLOGY" in config.sections()
        ctx.obj["TOKEN"] = config["FOSSOLOGY"]["token"]
        ctx.obj["USERNAME"] = config["FOSSOLOGY"]["username"]
        ctx.obj["SERVER"] = config["FOSSOLOGY"]["server_url"]
        logger.debug(
            f"Set server token from configfile {ctx.obj['SERVER']}:{ctx.obj['TOKEN']}"
        )
    else:
        logger.debug("INIT FOSS: No config file found")

    if not ctx.obj["TOKEN"]:
        try:
            ctx.obj["TOKEN"] = os.environ["FOSS_TOKEN"]
        except KeyError as e:
            logger.fatal(
                "No Token provided. Either provide FOSS_TOKEN in environment or use the -t option."
            )
            raise e
    foss = Fossology(ctx.obj["SERVER"], ctx.obj["TOKEN"])  # using new API
    ctx.obj["FOSS"] = foss
    ctx.obj["USER"] = foss.user.name
    logger.debug(f"Logged in as user {foss.user.name}")

    return ctx.obj["FOSS"]


@click.group()
@click.option("--token", "-t", help="The token to be used.")
@click.option(
    "--verbose",
    "-v",
    count=True,
    help="Increase verbosity level (e.g. -v -vv).",
)
@click.option(
    "--log_to_console/--no_log_to_console",
    is_flag=True,
    default=True,  # print logging events >= WARNING by default on console
    show_default=True,
    help="Send logging output to console",
)
@click.option(
    "--log_to_file/--no_log_to_file",
    is_flag=True,
    default=False,
    show_default=True,
    help="Send logging output to file",
)
@click.option(
    "--log_file_name",
    default=DEFAULT_LOG_FILE_NAME,
    show_default=True,
    help="Specify log filename",
)
@click.option(
    "--debug/--no_debug",
    is_flag=True,
    default=False,
    show_default=True,
    help="Send detailed logging output to console.",
)
@click.option(
    "--result_dir",
    default=DEFAULT_RESULT_DIR,
    show_default=True,
    help="Name of the directory where foss_cli writes results.",
)
@click.pass_context
def cli(
    ctx: click.core.Context,
    token: str,
    verbose: int,
    log_to_console: bool,
    log_to_file: bool,
    log_file_name: str,
    debug: bool,
    result_dir: str,
):
    """The foss_cli cmdline.  Multiple -v increase verbosity-level."""
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    if not os.path.isdir(result_dir):
        os.mkdir(result_dir)

    if log_to_file:
        logfile_handler = RotatingFileHandler(
            os.path.join(result_dir, log_file_name),
            maxBytes=MAX_SIZE_OF_LOGFILE,
            backupCount=MAX_NUMBER_OF_LOGFILES,
        )
        logfile_handler.setFormatter(formatter)
        logger.addHandler(logfile_handler)
    logger.setLevel(FOSS_LOGGING_MAP.get(verbose, logging.DEBUG))
    assert os.path.isdir(result_dir)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["TOKEN"] = token
    ctx.obj["DEBUG"] = debug
    ctx.obj["RESULT_DIR"] = result_dir

    if ctx.obj["VERBOSE"] >= 2:
        logger.debug(f"foss_cli called with: {pprint.pformat(sys.argv)}")

    foss_needs_initialization = needs_later_initialization_of_foss_instance(ctx)
    if foss_needs_initialization:
        logger.debug("Initializing Fossology client according to the CLI context")
        foss = init_foss(ctx)  # leaves the foss instance within the ctx dict
    else:
        logger.debug("Initialization of Fossology client is not needed")

    if debug:
        logger.debug("Started in debug mode")
        if foss_needs_initialization:
            logger.debug(
                f"Using API: {pprint.pformat(foss.api)} version {pprint.pformat(foss.info.version)}"
            )
            logger.debug(
                f"Running as user {pprint.pformat(foss.user.name)} on {pprint.pformat(foss.host)}"
            )
        else:
            logger.debug("Fossology client was not initialized")


@cli.command("config")
@click.option(
    "--server",
    default="http://fossology/repo",
    show_default=True,
    help="URL of Fossology server",
)
@click.option(
    "--username",
    default="fossy",
    show_default=True,
    help="Username on Fossology server",
)
@click.option("--password", default="fossy", show_default=True, help="Password")
@click.option(
    "--token_scope",
    default="read",
    show_default=True,
    help="Access scope on Fossology Server (read/write)",
)
@click.option(
    "--interactive/--nointeractive",
    is_flag=True,
    default=True,
    show_default=True,
    help="Get config values via stdin",
)
@click.pass_context
def config(
    ctx: click.core.Context,
    server: str,
    username: str,
    password: str,
    token_scope: str,
    interactive: bool,
):
    """Create a foss_cli config file."""

    if interactive:
        print("Enter the URL to your Fossology server: e.g. http://fossology/repo")
        server = input("Fossology URL: ")
        print(
            "Enter Username and Password: e.g. fossy/fossy (in the default environment)"
        )
        username = input("Username: ")
        password = getpass()
        token_scope = "read"
        while True:
            try:
                print(
                    "Enter a scope for your Fossology token: either 'read' or 'write'"
                )
                token_scope = input("Token scope: ")
                assert token_scope in ["read", "write"]
                break
            except Exception:
                print("Allowed values are 'read' or 'write' (using 'read' as default)")

    logger.warning(
        f"Create a new config for {username} on {server} with scope {token_scope}"
    )

    if token_scope == "read":
        the_token_scope = TokenScope.READ
    else:
        the_token_scope = TokenScope.WRITE

    logger.debug(f"Create token for {username} on {server}")
    token = fossology_token(
        server,
        username,
        password,
        secrets.token_urlsafe(8),  # TOKEN_NAME
        the_token_scope,
    )
    logger.debug(f"Token {token} has been created")

    path_to_cfg_file = pathlib.Path.cwd() / DEFAULT_CONFIG_FILE_NAME

    if path_to_cfg_file.exists():
        logger.info(
            f"Found existing foss_cli config file {path_to_cfg_file}, updating the values..."
        )
        config = configparser.ConfigParser()
        config.read(path_to_cfg_file)
    else:
        logger.info(
            f"foss_cli config file {path_to_cfg_file} not found, creating a new one..."
        )
        config = configparser.ConfigParser()

    config["FOSSOLOGY"] = {
        "SERVER_URL": server,
        "USERNAME": username,
        "TOKEN": token,
    }
    with open(path_to_cfg_file, "w") as fp:
        config.write(fp)

    logger.warning(f"New config has been generated in {path_to_cfg_file}")


@cli.command("log")
@click.option(
    "--log_level",
    default=0,
    show_default=True,
    help="Set the log_level of the message (0,1,2)",
)
@click.option(
    "--message_text",
    default="log message",
    show_default=True,
    help="Text of the log message",
)
@click.pass_context
def log(ctx: click.core.Context, log_level: int, message_text: str):
    """Add a Log Message to the log. If a log message is printed to the log depends
    on the verbosity defined starting the foss_cli (default level 0 /-v level 1/-vv level 2).
    Beeing on global verbosity level 0 only messages of --log_level 2 will be printed.
    Beeing on global verbosity level 1 messages of --log_level 1 and 2 will be printed.
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


@cli.command("create_folder")
@click.argument("folder_name")
@click.option("--folder_description", help="Description of the Folder.")
@click.option("--folder_group", help="Name of the Group owning the Folder.")
@click.pass_context
def create_folder(
    ctx: click.core.Context,
    folder_name: str,
    folder_description: str,
    folder_group: str,
):
    """The foss_cli create_folder command."""
    foss = ctx.obj["FOSS"]
    logger.debug(
        f" Try to create folder {folder_name} for group {folder_group} desc: {folder_description}"
    )
    try:
        folder = foss.create_folder(
            foss.rootFolder,
            folder_name,
            description=folder_description,
            group=folder_group,
        )
        logger.debug(
            f"Folder {folder.name} with description {folder.description} created"
        )
    except Exception as e:
        logger.fatal(f"Error creating Folder {folder_name} ", exc_info=True)
        raise e


@cli.command("create_group")
@click.argument("group_name")
@click.pass_context
def create_group(ctx: click.core.Context, group_name: str):
    """The foss_cli create_group command."""
    logger.debug(f"Create group {group_name}")
    foss = ctx.obj["FOSS"]
    try:
        foss.create_group(group_name)
        logger.debug(f" group {group_name} created")
    except FossologyApiError as e:
        if f"Group {group_name} already exists" in e.message:
            logger.debug(f"Group {group_name} already exists.")
        else:
            logger.fatal(f"Error adding group {group_name} ", exc_info=True)
            raise e


@cli.command("upload_file")
@click.argument(
    "upload_file",
    type=click.Path(exists=True),
)
@click.option(
    "--folder_name", default="", show_default=True, help="The name of the upload folder"
)
@click.option(
    "--description", default="", show_default=True, help="The description of the upload"
)
@click.option(
    "--access_level",
    default="public",
    show_default=True,
    help="The access level the upload",
)
@click.option(
    "--reuse_newest_upload/--no_reuse_newest_upload",
    is_flag=True,
    default=False,
    help="Reuse last upload if available.",
)
@click.option(
    "--summary/--no_summary",
    is_flag=True,
    default=False,
    help="Get summary of upload.",
)
@click.pass_context
def upload_file(
    ctx: click.Context,
    upload_file: str,
    folder_name: str,
    description: str,
    access_level: str,
    reuse_newest_upload: bool,
    summary: Summary,
):
    """The foss_cli upload_file command."""

    logger.debug(f"Try to upload file {upload_file}")
    foss = ctx.obj["FOSS"]

    # check/set the requested access level
    the_access_level = check_get_access_level(access_level)

    # check/set the requested folder
    folder_to_use = check_get_folder(ctx, folder_name)

    if reuse_newest_upload:
        the_upload = get_newest_upload_of_file(ctx, upload_file, folder_name)
    else:
        the_upload = None

    if the_upload is None:
        the_upload = foss.upload_file(
            folder_to_use,
            file=upload_file,
            description=description if description else "upload via foss-cli",
            access_level=the_access_level,
            wait_time=10,
        )

    ctx.obj["UPLOAD"] = the_upload

    if summary:
        summary = foss.upload_summary(the_upload)
        if ctx.obj["DEBUG"]:
            logger.debug(
                f"Summary of upload {summary.uploadName} ({summary.id})"
                f"Main license: {summary.mainLicense}"
                f"Unique licenses: {summary.uniqueLicenses}"
                f"Total licenses: {summary.totalLicenses}"
                f"Unique concluded licenses: {summary.uniqueConcludedLicenses}"
                f"Total concluded licenses: {summary.totalConcludedLicenses}"
                f"Files to be cleared: {summary.filesToBeCleared}"
                f"Files cleared: {summary.filesCleared}"
                f"Clearing status: {summary.clearingStatus}"
                f"Copyright count: {summary.copyrightCount}"
                f"Additional info: {summary.additional_info}"
            )


@cli.command("delete_folder")
@click.argument("folder_name")
@click.pass_context
def delete_folder(
    ctx: click.core.Context,
    folder_name: str,
):
    """The foss_cli delete_folder command."""

    logger.debug(f"Try to delete folder {folder_name}")
    foss = ctx.obj["FOSS"]

    folder = None
    for f in foss.list_folders():
        if f.name == folder_name:
            folder = f
            logger.debug(f"Found folder to delete: {folder}")
            break

    if not folder:
        logger.fatal(f"Unable to find folder {folder_name}.")
        ctx.exit(1)

    foss.delete_folder(folder)
    logger.debug(f"Delete command was send to {foss.host} for folder {folder}")


@cli.command("delete_upload")
@click.argument("upload_name")
@click.pass_context
def delete_upload(
    ctx: click.core.Context,
    upload_name: str,
):
    """The foss_cli folder_id command."""

    logger.debug(f"Try to delete upload {upload_name}")
    foss = ctx.obj["FOSS"]

    upload = None
    for u in foss.list_uploads(all_pages=True)[0]:
        if u.uploadname == upload_name:
            upload = u
            logger.debug(f"Found upload to delete: {upload}")
            break

    foss.delete_upload(upload)
    logger.debug(f"Delete command was send to {foss.host} for upload {upload}")


@cli.command("start_workflow")
@click.argument(
    "file_name",
    type=click.Path(exists=True),
)
@click.option(
    "--folder_name",
    default="",
    show_default=True,
    help="The name of the folder to upload to",
)
@click.option(
    "--file_description",
    default="Upload via foss-cli",
    show_default=True,
    help="The description of the upload",
)
@click.option(
    "--dry_run/--no_dry_run",
    is_flag=True,
    default=False,
    show_default=True,
    help="Do not upload but show what would be done. Use -vv to see output.",
)
@click.option(
    "--reuse_newest_upload/--no_reuse_newest_upload",
    is_flag=True,
    default=False,
    show_default=True,
    help="Reuse newest upload if available",
)
@click.option(
    "--reuse_newest_job/--no_reuse_newest_job",
    is_flag=True,
    default=False,
    show_default=True,
    help="Reuse newest scheduled job for the upload if available",
)
@click.option(
    "--report_format",
    default="unifiedreport",
    show_default=True,
    help="The name of the reportformat (dep5, spdx2, spdxtv, readmeoss, unifiedreport)",
)
@click.option(
    "--access_level",
    default="protected",
    show_default=True,
    help="The access level of the upload (private, protected, public)",
)
@click.pass_context
def start_workflow(  # noqa: C901
    ctx: click.core.Context,
    file_name: str,
    file_description: str,
    folder_name: str,
    report_format: str,
    access_level: str,
    reuse_newest_upload: bool,
    reuse_newest_job: bool,
    dry_run: bool,
):
    """The foss_cli start_workflow command."""
    global JOB_SPEC
    logger.debug(f"Try to schedule job for {file_name}")
    foss = ctx.obj["FOSS"]

    # check/set the requested report format
    the_report_format = check_get_report_format(report_format)

    # check/set the requested access level
    the_access_level = check_get_access_level(access_level)

    # check/get the folder to use identified by the provided  folder_name
    folder_to_use = check_get_folder(ctx, folder_name)

    # check/get the foss.upload to use
    if reuse_newest_upload:
        the_upload = get_newest_upload_of_file(ctx, file_name, folder_name)
    else:
        if dry_run:
            logger.warning(
                "Skip upload as dry_run is requested without --reuse_newest_upload"
            )
            the_upload = None
        else:
            logger.debug(f"Initiate new upload for {file_name}")

            the_upload = foss.upload_file(
                folder_to_use,
                file=file_name,
                description=file_description,
                access_level=the_access_level,
                wait_time=10,
            )
            logger.debug(f"Finished upload for {file_name}")

    if the_upload is None:
        logger.fatal(f"Unable to find upload for {file_name}.")
        ctx.exit(1)

    # check/get job correlated with the upload
    job = None
    if reuse_newest_job:
        logger.debug(f"Try to find a scheduled job on {the_upload.uploadname}")
        the_jobs, pages = foss.list_jobs(the_upload)
        newest_date = "0000-09-05 13:25:38.079869+00"
        for the_job in the_jobs:
            if the_job.queueDate > newest_date:
                newest_date = the_job.queueDate
                job = the_job
        if job is None:
            logger.info(f"Upload {the_upload.uploadname} never started a job ")
        else:
            logger.debug(
                f"Can reuse old job on Upload {the_upload.uploadname}: Newest Job id {job.id} is from {job.queueDate} "
            )

    if job is None:  # always true if --no_reuse_newest_job
        job = foss.schedule_jobs(
            folder_to_use if folder_to_use else foss.rootFolder,
            the_upload,
            JOB_SPEC,
            wait=True,  # we wait (default 30 sec) for the job to complete
        )
        logger.debug(f"Scheduled new job {job}")

    # check/get state of job correlated with the upload
    logger.debug(f"job  {job.id}  is in state {job.status} ")
    if job.status == "Processing":
        logger.fatal(
            f"job  {job.id}  is still in state {job.status}: Please try again later with --reuse_newest_upload --reuse_newest_job "
        )
        ctx.exit(1)

    assert job.status == "Completed"

    # trigger generation of report
    report_id = foss.generate_report(the_upload, report_format=the_report_format)
    logger.debug(f"Generated report {report_id}")

    # download report
    content, name = foss.download_report(report_id)
    logger.debug(
        f"Report downloaded: {name}:  content type: {type(content)} len:  {len(content)}."
    )

    destination_file = os.path.join(ctx.obj["RESULT_DIR"], name)
    with open(destination_file, "wb") as fp:
        written = fp.write(content)
        assert written == len(content)
        logger.info(
            f"Report written to file: report_name {name}  written to {destination_file}"
        )


def main():
    d = dict()
    d["IS_REQUEST_FOR_HELP"] = False
    d["IS_REQUEST_FOR_CONFIG"] = False
    for arg in sys.argv[1:]:
        if arg == "--help":
            d["IS_REQUEST_FOR_HELP"] = True
        if arg == "config":
            d["IS_REQUEST_FOR_CONFIG"] = True
    cli(obj=d)  # pragma: no cover


if __name__ == "__main__":
    main()
