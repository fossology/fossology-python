__doc__ = """
        The foss_cli cmdline interface uses the provided REST-API to communicate
        with the Fossology Server.
        Logging is implemented using the standard python logging framework.
        Log Level can be adapted using the -v/-vv option to foss_cli.
        Logging could be sent to console (option --log_to_file) and/or to a log_file
        (option --log_to_file). The name of the log_file (default is .foss_cli.log)
        could be adapted using the option --log_file_name <filename>.
"""
import pprint
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import click

from fossology import Fossology
from fossology.exceptions import AuthenticationError, FossologyApiError
from fossology.obj import AccessLevel, ReportFormat

logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)

FOSS_LOGGING_MAP = {0: logging.WARNING, 1: logging.INFO, 2: logging.DEBUG}
MAX_SIZE_OF_LOGFILE = 200000
MAX_NUMBER_OF_LOGFILES = 5

IS_REQUEST_FOR_HELP = False


JOB_SPEC = {
    "analysis": {
        "bucket": True,
        "copyright_email_author": True,
        "ecc": True,
        "keyword": True,
        "monk": True,
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


def get_report_format(format: str):
    """[Get report format.]
    :param format: [name of a report format]
    :type format: str
    :return: []
    :rtype: [ReportFormat Attribute]
    """
    if format == "dep5":
        the_report_format = ReportFormat.DEP5
    elif format == "spx2":
        the_report_format = ReportFormat.SPDX2
    elif format == "spx2tv":
        the_report_format = ReportFormat.SPDX2TV
    elif format == "readmeoss":
        the_report_format = ReportFormat.READMEOSS
    elif format == "unifiedreport":
        the_report_format = ReportFormat.UNIFIEDREPORT
    else:
        logger.fatal(f"Impossible report format {format}")
        sys.exit(1)
    return the_report_format


def is_help():
    """[summary]
    :return: [Indicates if it is a --help invocation]
    :rtype: [bool]
    """
    global IS_REQUEST_FOR_HELP
    if IS_REQUEST_FOR_HELP:
        logger.debug("Skip Initialisation as it is a --help call")
        return True
    return False


def init_foss(ctx: dict):
    """[Initialize Fossology Instance.]

    :param ctx: [context provided by all click-commands]
    :type ctx: [dict]
    :raises e: [Bearer TOKEN not set in environment]
    :raises e1: [Authentication with new API failed. Tried with old_api - but usernamewas missing in environment.]
    :raises e2: [Authentication with old APi failed -too.]
    :return: [foss_instance]
    :rtype: [Fossology]
    """
    if ctx.obj["TOKEN"] is None:
        try:
            ctx.obj["TOKEN"] = os.environ["FOSS_TOKEN"]
        except Exception as e:
            logger.fatal(
                "No Token provided. Either provide FOSS_TOKEN in environment or use the -t option."
            )
            raise e
    if "FOSS" not in ctx.obj.keys():  # Initial try to connect to the server
        try:
            foss = Fossology(ctx.obj["SERVER"], ctx.obj["TOKEN"])  # using new API
            ctx.obj["FOSS"] = foss
        except AuthenticationError as e1:  # Maybe it is an old version needing the username ?
            try:
                if ctx.obj["USERNAME"] is None:
                    logger.fatal(
                        "Connecting to the Fossology Server using new API failed - \
                          to check with the old API a username is needed - but not provided",
                        exc_info=True,
                    )
                    raise e1
                else:
                    foss = Fossology(
                        ctx.obj["SERVER"], ctx.obj["TOKEN"], ctx.obj["USERNAME"],
                    )
            except AuthenticationError as e2:
                logger.fatal(
                    'Connecting to the Fossology Server using new API failed - \
                         even connecting to the old API with user {ctx.obj["USERNAME"]} failed',
                    exc_info=True,
                )
                raise e2
        ctx.obj["FOSS"] = foss
        ctx.obj["USER"] = foss.user.name
    logger.debug(f"Logged in as user {foss.user.name}")
    return ctx.obj["FOSS"]


@click.group()
@click.option("--token", "-t", help="token to be used.")
@click.option("--server", "-s", default="http://fossology/repo", help="url of server.")
@click.option("--username", "-u", default="fossy", help="Username on Fossology Server.")
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
@click.option(
    "--debug/--no_debug",
    is_flag=True,
    default=False,
    help="Send detailed logging output to console. Default is --nodebug.",
)
@click.pass_context
def cli(
    ctx,
    server,
    username,
    token,
    verbose,
    log_to_console,
    log_to_file,
    log_file_name,
    debug,
):
    """The fossology cmdline client.  Multiple -v increase verbosity-level.
    """
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
    ctx.obj["USERNAME"] = username
    ctx.obj["DEBUG"] = debug

    if not is_help():
        foss = init_foss(ctx)  # leaves the foss instance within the ctx dict
    if debug:
        logger.debug("Started in debug mode")
        logger.debug(f"Servers users:{pprint.pformat(foss.users)}")
        folder_ids = [folder.id for folder in foss.folders]
        for id in folder_ids:
            detail = foss.detail_folder(id)
            logger.debug(f"Get Folder {detail.id}")
            logger.debug(f"    Name: {detail.name}  Parent:   {detail.parent}")
            logger.debug(
                f"    desc: {detail.description}  Add-Info: {detail.additional_info}"
            )
        logger.debug(f"Servers api:{pprint.pformat(foss.api)}")
        logger.debug(f"Servers version:{pprint.pformat(foss.version)}")
        logger.debug(f"User Authorized on Server:{pprint.pformat(foss.user.name)}")
        logger.debug(f"Root Folder on Server:{pprint.pformat(foss.rootFolder.name)}")


@cli.command("log")
@click.option(
    "--log_level", default=0, help="Set the log_level of the message [0,1,2]."
)
@click.option("--message_text", default="log message", help="Text of the log message.")
@click.pass_context
def log(ctx, log_level, message_text):
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


@cli.command("create_folder")
@click.option("--folder_name", help="The name of the folder.")
@click.option("--folder_description", help="Description of the Folder.")
@click.option("--folder_group", help="Name of the Group owning the Folder.")
@click.pass_context
def create_folder(ctx, folder_name, folder_description, folder_group):
    """The fossology create_folder command."""
    ctx.obj["FOLDER_NAME"] = folder_name
    ctx.obj["FOLDER_DESCRIPTION"] = folder_description
    ctx.obj["FOLDER_GROUP"] = folder_group
    foss = ctx.obj["FOSS"]
    try:
        logger.debug(
            f" Try to create folder {folder_name} for group {folder_group} desc: {folder_description}"
        )
        folder = foss.create_folder(
            foss.rootFolder,
            folder_name,
            description=folder_description,
            group=folder_group,
        )
        message = f"Folder {folder.name} with description {folder.description} created"
        logger.debug(message)
    except Exception as e:
        logger.fatal(f"Error creating Folder {folder_name} ", exc_info=True)
        raise e


@cli.command("create_group")
@click.argument("group_name")
@click.pass_context
def create_group(ctx, group_name):
    """The fossology create_group command."""
    logger.debug(f"Try to create group {group_name}")
    foss = ctx.obj["FOSS"]
    try:
        foss.create_group(group_name)
        logger.debug(f" group {group_name} created")
    except FossologyApiError as e:
        if "Details: Group already exists.  Not added." in e.message:
            logger.debug(
                f" group {group_name} already exists. Anyway the group is available."
            )
        else:
            logger.fatal(f"Error adding group {group_name} ", exc_info=True)
            raise e


def get_last_upload_of_file(ctx: dict, filename: str, folder_name: str):
    """[summary]

    :param ctx: [click Context]
    :param filename: []
    :param folder_name: []
    :return Upload
    """
    foss = ctx.obj["FOSS"]
    the_uploads, pages = foss.list_uploads(
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
            f"Reused upload id {a_upload.id} matches {upload_file} and is the newest"
        )
        assert a_upload.id == the_upload.id
        return the_upload
    else:
        return None


@cli.command("upload_file")
@click.argument(
    "upload_file", type=click.Path(exists=True),
)
@click.option("--folder_name", default=None, help="The name of the folderto upload to.")
@click.option("--description", default=None, help="The decription of the upload.")
@click.option("--access_level", default="Public", help="The acces Level  the upload.")
@click.option(
    "--reuse_last_upload/--no_reuse_last_upload",
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
    ctx, upload_file, folder_name, description, access_level, reuse_last_upload, summary
):
    """The fossology upload_file command."""

    logger.debug(f"Try to upload file {upload_file}")
    foss = ctx.obj["FOSS"]
    if access_level != "Public":
        logger.fatal(
            f"{access_level}  AccesLevel other than public not yet implemented"
        )

    if reuse_last_upload:
        the_upload = get_last_upload_of_file(ctx, upload_file, folder_name)
    else:
        the_upload = None

    if the_upload is None:
        the_upload = foss.upload_file(
            folder_name if folder_name else foss.rootFolder,
            file=upload_file,
            description=description if description else "upload via foss-cli",
            access_level=AccessLevel.PUBLIC,
        )

    ctx.obj["UPLOAD"] = the_upload

    if summary:
        summary = foss.upload_summary(the_upload)
        if ctx.obj["DEBUG"]:
            logger.debug(
                f"Summary of Upload id {summary.id} Name {summary.uploadName} "
            )
            logger.debug(
                f"    Main Lic {summary.mainLicense} Unique Lic  {summary.uniqueLicenses} "
            )
            logger.debug(
                f"    Total Lic {summary.totalLicenses} Unique Concl Lic  {summary.uniqueConcludedLicenses}"
            )
            logger.debug(
                f"    totalConcludedLicenses {summary.totalConcludedLicenses} FileToBeCleared  {summary.filesToBeCleared} "
            )
            logger.debug(
                f"    Files Cleared {summary.filesCleared}  ClearingStatus  {summary.clearingStatus} "
            )
            logger.debug(
                f"    CopyRightCount {summary.copyrightCount}  Add Info  {summary.additional_info} "
            )


@cli.command("schedule_jobs")
@click.argument(
    "file_name", type=click.Path(exists=True),
)
@click.option(
    "--folder_name", default=None, help="The name of the folder to upload to."
)
@click.option(
    "--report_format", default="unifiedreport", help="The name of the reportformat."
)
@click.pass_context
def schedule_jobs(ctx, file_name, folder_name, report_format):
    """The fossology schedule_jobs command."""
    global JOB_SPEC
    the_report_format = get_report_format(report_format)
    logger.debug(f"Try to shedule job {file_name}")
    foss = ctx.obj["FOSS"]

    the_upload = get_last_upload_of_file(ctx, file_name, folder_name)

    if the_upload is None:
        logger.fatal(f"Unable to find upload for {file_name}.")
        logger.fatal("Fix the current cache thinking")
        sys.exit(0)
    else:
        logger.info(f"upload id {the_upload.id} is the newest")

    the_jobs, pages = foss.list_jobs(the_upload)
    job = None
    newest_date = "0000-09-05 13:25:38.079869+00"
    for the_job in the_jobs:
        if the_job.queueDate > newest_date:
            newest_date = the_job.queueDate
            job = the_job
    if job:
        logger.info(f"Newest Job id {job.id} is from {job.queueDate} ")
    else:
        job = foss.schedule_jobs(
            folder_name if folder_name else foss.rootFolder, the_upload, JOB_SPEC
        )
        logger.debug(f"Try to schedule job {job}")

    if ctx.obj["DEBUG"]:
        logger.debug(f"Job  {job.id} name {job.name}")

    detail = foss.detail_job(job.id)
    logger.debug(f"job  {job.id}  state {job.status} ")
    logger.debug(f"Detail {dir(detail)} ")

    report_id = foss.generate_report(the_upload, report_format=the_report_format)

    logger.debug(f"report {report_id}  Generated ")
    #   content, name = foss.download_report(report_id, group_name)
    content, name = foss.download_report(report_id)
    logger.debug(f"content type: {type(content)} len {len(content)} Downloaded")

    content = content.splitlines()
    logger.debug(f"content {pprint.pformat(content)} ")

    content = b"content".decode("utf-8")
    logger.debug(f"report {name}  Downloaded")
    logger.debug(f"report {name}  had content {pprint.pformat(content.splitlines())}")


def main():
    global IS_REQUEST_FOR_HELP
    for i in sys.argv[1:]:
        if i == "--help":
            IS_REQUEST_FOR_HELP = True
    cli(obj={})  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
