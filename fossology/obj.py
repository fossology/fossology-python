# mypy: disable-error-code="attr-defined"
# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

import json
from typing import Iterable

from fossology.enums import ClearingScope, ClearingType, Permission


class Agents(object):
    """FOSSology agents.

    Represents the agents currently configured for a given user.

    :param bucket: run bucket agent on every upload
    :param copyright_email_author: run copyright_email_author agent on every upload
    :param ecc: run ecc agent on every upload
    :param keyword: run keyword agent on every upload
    :param mimetype: run mimetype agent on every upload
    :param monk: run monk agent on every upload
    :param nomos: run nomos agent on every upload
    :param ojo: run ojo agent on every upload
    :param package: run package agent on every upload
    :param kwargs: handle any other agent provided by the fossology instance
    :type bucket: boolean
    :type copyright_email_author: boolean
    :type ecc: boolean
    :type keyword: boolean
    :type mimetype: boolean
    :type monk: boolean
    :type nomos: boolean
    :type ojo: boolean
    :type package: boolean
    :type kwargs: key word argument
    """

    def __init__(
        self,
        bucket,
        copyright_email_author,
        ecc,
        keyword,
        mimetype,
        monk,
        nomos,
        ojo,
        package,
        **kwargs,
    ):
        self.bucket = bucket
        self.copyright_email_author = copyright_email_author
        self.ecc = ecc
        self.keyword = keyword
        self.mimetype = mimetype
        self.monk = monk
        self.nomos = nomos
        self.ojo = ojo
        self.package = package
        self.additional_agents = kwargs

    def to_dict(self):
        generic_agents = {
            "bucket": self.bucket,
            "copyright_email_author": self.copyright_email_author,
            "ecc": self.ecc,
            "keyword": self.keyword,
            "mimetype": self.mimetype,
            "monk": self.monk,
            "nomos": self.nomos,
            "ojo": self.ojo,
            "package": self.package,
        }
        try:
            agents = {**generic_agents, **self.additional_agents}
        except AttributeError:
            agents = generic_agents
        return agents

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)

    def to_json(self):
        return json.dumps(self.to_dict())


class User(object):
    """FOSSology user."""

    def __init__(
        self,
        id: int,
        name: str,
        description: str,
        email: str | None = None,
        accessLevel: int | None = None,
        rootFolderId: int | None = None,
        emailNotification: str | None = None,
        default_group: str | None = None,
        agents: Agents | None = None,
        **kwargs: dict,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.email = email
        self.accessLevel = accessLevel
        self.rootFolderId = rootFolderId
        self.emailNotification = emailNotification
        self.default_group = default_group
        self.agents = agents
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"User {self.description} ({self.id}), {self.email}, "
            f"access level {self.accessLevel}, "
            f"root folder {self.rootFolderId}, "
            f"default group {self.default_group}"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class UserGroupMember(object):
    """FOSSology group member."""

    def __init__(self, user: User, group_perm: int, **kwargs: dict):
        self.user = User.from_json(user)
        self.group_perm = group_perm
        self.additional_info = kwargs

    def __str__(self):
        return f"Member {self.user.name} ({self.user.id}) has permission {self.group_perm}."

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Folder(object):
    """FOSSology folder.

    Represents a FOSSology folder.

    :param id: the ID of the folder
    :param name: the name of the folder
    :param description: further information about the folder
    :param parent: the ID of the parent folder
    """

    def __init__(self, id, name, description, parent, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.parent = parent
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"{self.name} ({self.id}), '{self.description}', "
            f"parent folder id = {self.parent}"
        )

    def __eq__(self, other):
        if isinstance(other, Folder):
            return self.id == other.id
        return False

    @classmethod
    def from_json(cls, json_dict):
        """Parse folder from API v1 response"""
        parent = None

        if "parentID" in json_dict:
            parent = json_dict.get("parentID")
        elif "parentId" in json_dict:
            parent = json_dict.get("parentId")
        elif "parent" in json_dict and not isinstance(json_dict.get("parent"), dict):
            parent = json_dict.get("parent")

        return cls(
            id=json_dict.get("id"),
            name=json_dict.get("name"),
            description=json_dict.get("description"),
            parent=parent,
        )

    @classmethod
    def from_json_v2(cls, json_dict):
        """Parse folder from API v2 response"""
        parent = None

        if isinstance(json_dict.get("parent"), dict):
            parent = json_dict["parent"].get("id")
        elif json_dict.get("parent") is not None:
            parent = json_dict.get("parent")

        return cls(
            id=json_dict.get("id"),
            name=json_dict.get("name"),
            description=json_dict.get("description"),
            parent=parent,
        )


class Findings(object):
    """FOSSology license findings."""

    def __init__(
        self,
        scanner: list,
        conclusion: list | None = None,
        copyright: list | None = None,
        **kwargs,
    ):
        self.scanner = scanner
        self.conclusion = conclusion
        self.copyright = copyright
        self.additional_info = kwargs

    def __str__(self):
        len_copyright = len(self.copyright) if self.copyright else 0
        return (
            f"Licenses found by scanners: {self.scanner}, concluded licenses: {self.conclusion}, "
            f"{len_copyright} copyrights"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Group(object):
    """FOSSology group."""

    def __init__(self, id, name, **kwargs):
        self.id = id
        self.name = name
        self.additional_info = kwargs

    def __str__(self):
        return f"Group {self.name} ({self.id})"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class PermGroups(object):
    """GroupIds with their respective permissions for a upload."""

    def __init__(self, perm: str, group_pk: str, group_name: str):
        self.perm = Permission(perm)
        self.group_pk = group_pk
        self.group_name = group_name

    def __str__(self):
        return f"Group {self.group_name} ({self.group_pk}) with {self.perm.name} permission"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class UploadPermGroups(object):
    """Upload permissions."""

    def __init__(self, publicPerm: str, permGroups: list, **kwargs):
        self.publicPerm = Permission(publicPerm)
        self.permGroups = list()
        for perm in permGroups:
            self.permGroups.append(PermGroups.from_json(perm))
        self.additional_info = kwargs

    def __str__(self):
        return f"Upload with {self.publicPerm.name} permission and permissions for groups {self.permGroups}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class License(object):
    """FOSSology license."""

    def __init__(self, shortName, fullName, text, url, risk, isCandidate, id=None, **kwargs):
        self.id = id
        self.shortName = shortName
        self.fullName = fullName
        self.text = text
        self.url = url
        self.risk = risk
        self.isCandidate = isCandidate
        self.additional_info = kwargs

    def __str__(self):
        license_type = "License"
        if self.isCandidate:
            license_type = "Candidate license"
        return f"{license_type} {self.fullName} - {self.shortName} ({self.id}) with risk level {self.risk}"

    def to_dict(self):
        return {
            "shortName": self.shortName,
            "fullName": self.fullName,
            "text": self.text,
            "url": self.url,
            "risk": self.risk,
            "isCandidate": self.isCandidate,
        }

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class Obligation(object):
    """FOSSology license obligation."""

    def __init__(self, id, topic, type, text, classification, comment, **kwargs):
        self.id = id
        self.topic = topic
        self.type = type
        self.text = text
        self.classification = classification
        self.comment = comment
        self.additional_info = kwargs

    def __str__(self):
        return f"Obligation {self.topic}, {self.type} ({self.id}) is classified {self.classification}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Hash(object):
    """FOSSology hash."""

    def __init__(self, sha1, md5, sha256, size, **kwargs):
        self.sha1 = sha1
        self.md5 = md5
        self.sha256 = sha256
        self.size = size
        self.additional_info = kwargs

    def __str__(self):
        return f"File SHA1: {self.sha1} MD5 {self.md5} SH256 {self.sha256} Size {self.size}B"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class File(object):
    """FOSSology file response from filesearch."""

    def __init__(self, hash, findings, **kwargs):
        self.hash = Hash.from_json(hash)
        self.findings = Findings.from_json(findings)
        self.additional_info = kwargs

    def __str__(self):
        if self.findings.conclusion:
            return f"File with SHA1 {self.hash.sha1} has {len(self.findings.conclusion)} concluded licenses"
        else:
            return f"File with SHA1 {self.hash.sha1} doesn't have any concluded license yet"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class FileInfo(object):
    """FOSSology file info response."""

    def __init__(self, view_info, meta_info, package_info, tag_info, reuse_info, **kwargs):
        self.view_info = view_info
        self.meta_info = meta_info
        self.package_info = package_info
        self.tag_info = tag_info
        self.reuse_info = reuse_info
        self.additional_info = kwargs

    def __str__(self):
        return f"File view {self.view_info}"

    @classmethod
    def from_json(cls, json_dict):
        for key in ("viewInfo", "metaInfo", "packageInfo", "tagInfo", "reuseInfo"):
            try:
                json_dict[key.replace("I", "_i")] = json_dict[key]
                del json_dict[key]
            except KeyError:
                pass
        return cls(**json_dict)


class Upload(object):
    """FOSSology upload."""

    def __init__(
        self,
        folderid,
        foldername,
        id,
        description,
        uploadname,
        uploaddate,
        assignee=None,
        assigneeDate=None,
        closingDate=None,
        hash=None,
        **kwargs,
    ):
        self.folderid = folderid
        self.foldername = foldername
        self.id = id
        self.description = description
        self.uploadname = uploadname
        self.uploaddate = uploaddate
        self.assignee = (assignee,)
        self.assigneeDate = (assigneeDate,)
        self.closeDate = (closingDate,)
        self.hash = Hash.from_json(hash)
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"Upload '{self.uploadname}' ({self.id}, {self.hash.size}B, {self.hash.sha1}) "
            f"in folder {self.foldername} ({self.folderid})"
        )

    @classmethod
    def from_json(cls, json_dict):
        for key in ("folderId", "folderName", "uploadName", "uploadDate"):
            try:
                json_dict[key.lower()] = json_dict[key]
                del json_dict[key]
            except KeyError:
                pass
        return cls(**json_dict)


class UploadCopyrights(object):
    """Copyright findings in a FOSSology upload."""

    def __init__(self, copyright: str, filePath: list[str], **kwargs):
        self.copyright = copyright
        self.filepath = list()
        for path in filePath:
            self.filepath.append(path)
        self.additional_info = kwargs

    def __str__(self):
        return f"Copyright {self.copyright} was found in {len(self.filepath)} files."

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class UploadLicenses(object):
    """FOSSology upload licenses."""

    def __init__(self, filePath: str, findings: dict, **kwargs):
        self.filepath = filePath
        self.findings = Findings.from_json(findings)
        self.additional_info = kwargs

    def __str__(self):
        len_conclusion = len(self.findings.conclusion) if self.findings.conclusion else 0
        len_copyright = len(self.findings.copyright) if self.findings.copyright else 0
        return f"File {self.filepath} has {len_conclusion} license and {len_copyright} copyrights found."

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Summary(object):
    """FOSSology upload summary."""

    def __init__(
        self,
        id,
        uploadName,
        mainLicense,
        uniqueLicenses,
        totalLicenses,
        uniqueConcludedLicenses,
        totalConcludedLicenses,
        filesToBeCleared,
        filesCleared,
        clearingStatus,
        copyrightCount,
        **kwargs,
    ):
        self.id = id
        self.uploadName = uploadName
        self.mainLicense = mainLicense
        self.uniqueLicenses = uniqueLicenses
        self.totalLicenses = totalLicenses
        self.uniqueConcludedLicenses = uniqueConcludedLicenses
        self.totalConcludedLicenses = totalConcludedLicenses
        self.filesToBeCleared = filesToBeCleared
        self.filesCleared = filesCleared
        self.clearingStatus = clearingStatus
        self.copyrightCount = copyrightCount
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"Clearing status for '{self.uploadName}' is '{self.clearingStatus}',"
            f" main license = {self.mainLicense}"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Job(object):
    """FOSSology job."""

    def __init__(self, id, name, queueDate, uploadId, userId, groupId, eta, status, **kwargs):
        self.id = id
        self.name = name
        self.queueDate = queueDate
        self.uploadId = uploadId
        self.userId = userId
        self.groupId = groupId
        self.eta = eta
        self.status = status
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"Job '{self.name}' ({self.id}) queued on {self.queueDate} "
            f"(Status: {self.status} ETA: {self.eta})"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class JobDownload(object):
    """FOSSology job download."""

    def __init__(self, text: str, link: str, **kwargs):
        self.text = text
        self.link = link
        self.additional_info = kwargs

    def __str__(self):
        return f"Job output {self.text} can be downloaded here: {self.link}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class JobQueue(object):
    """FOSSology job queue."""

    def __init__(
        self,
        jobQueueId: int,
        jobQueueType: str,
        startTime: str,
        endTime: str,
        status: str,
        itemsProcessed: int,
        log: str,
        dependencies: list[int],
        itemsPerSec: int,
        canDoActions: bool,
        isInProgress: bool,
        isReady: bool,
        download: JobDownload,
        **kwargs,
    ):
        self.id = jobQueueId
        self.jobQueueType = jobQueueType
        self.startTime = startTime
        self.endTime = endTime
        self.status = status
        self.itemsProcessed = itemsProcessed
        self.log = log
        self.dependencies = dependencies
        self.itemsPerSec = itemsPerSec
        self.canDoActions = canDoActions
        self.isInProgress = isInProgress
        self.isReady = isReady
        self.download = JobDownload.from_json(download) if download else None
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"Job '{self.jobQueueType}' ({self.id}) queued on {self.startTime} processed {self.itemsProcessed} items "
            f"(Status: {self.status} EndTime: {self.endTime})"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class ShowJob(object):
    """FOSSology job."""

    def __init__(self, jobId: int, jobName: str, jobQueue: list[JobQueue], uploadId: int):
        self.id = jobId
        self.jobName = jobName
        self.jobQueue = list()
        for job in jobQueue:
            self.jobQueue.append(JobQueue.from_json(job))
        self.uploadId = uploadId

    def __str__(self):
        return f"Job {self.jobName} ({self.id}) for upload {self.uploadId} with {len(self.jobQueue)} jobs in the queue"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class ApiLicense(object):
    """FOSSology API License."""

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __str__(self):
        return f"API license '{self.name}' ({self.url})"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class FossologyServer(object):
    """FOSSology server info."""

    def __init__(self, version, branchName, commitHash, commitDate, buildDate):
        self.version = version
        self.branchName = branchName
        self.commitHash = commitHash
        self.commitDate = commitDate
        self.buildDate = buildDate

    def __str__(self):
        return f"Fossology server version {self.version} (branch {self.branchName} - {self.commitHash})"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class ApiInfo(object):
    """FOSSology API info."""

    def __init__(self, name, description, version, security, contact, license, fossology, **kwargs):
        self.name = name
        self.description = description
        self.version = version
        self.security = security
        self.contact = contact
        self.license = ApiLicense.from_json(license)
        self.fossology = FossologyServer.from_json(fossology)
        self.additional_info = kwargs

    def __str__(self):
        return f"{self.name} is deployed with version {self.version}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Status(object):
    """FOSSology server status."""

    def __init__(self, status):
        self.status = status

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class HealthInfo(object):
    """FOSSology server health info."""

    def __init__(self, status, scheduler, db, **kwargs):
        self.status = status
        self.scheduler = Status.from_json(scheduler)
        self.db = Status.from_json(db)

    def __str__(self):
        return f"FOSSology server status is: {self.status} (Scheduler: {self.scheduler.status} - DB: {self.db.status})"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class SearchResult(object):
    """Search result."""

    def __init__(self, upload, uploadTreeId, filename, **kwargs):
        self.upload = Upload.from_json(upload)
        self.uploadTreeId = uploadTreeId
        self.filename = filename
        self.additional_info = kwargs

    def __str__(self):
        return f"File found in upload {self.upload.uploadname} ({self.uploadTreeId}): {self.filename}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class GetClearingHistory(object):
    """Clearing history."""

    def __init__(
        self,
        date: str,
        username: str,
        scope: str,
        type: str,
        addedLicenses: Iterable[str],
        removedLicenses: Iterable[str],
        **kwargs,
    ):
        self.date = date
        self.username = username
        self.scope = ClearingScope(scope)
        self.type = ClearingType(type)
        self.addedLicenses = addedLicenses
        self.removedLicenses = removedLicenses
        self.additional_info = kwargs

    def __str__(self):
        return f"{self.username} changed clearing history at {self.date} in {self.scope} (type: {self.type})"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class GetBulkHistory(object):
    """Bulk history."""

    def __init__(
        self,
        bulkId: int,
        clearingEventId: int,
        text: str,
        matched: bool,
        tried: bool,
        addedLicenses: Iterable[str],
        removedLicenses: Iterable[str],
        **kwargs,
    ):
        self.bulkId = bulkId
        self.clearingEventId = clearingEventId
        self.text = text
        self.matched = matched
        self.tried = tried
        self.addedLicenses = addedLicenses
        self.removedLicenses = removedLicenses
        self.additional_info = kwargs

    def __str__(self):
        return f"Bulk Id {self.bulkId} associated with {self.clearingEventId} | Search for {self.text}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class GetPrevNextItem(object):
    """PrevNext item for the clearing history."""

    def __init__(self, prevItemId: int, nextItemId: int, **kwargs):
        self.prevItemId = prevItemId
        self.nextItemId = nextItemId
        self.additional_info = kwargs

    def __str__(self):
        return f"Prev: {self.prevItemId} | Next: {self.nextItemId}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)