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
        """Get a directory with the agent configuration

        :return: the agents configured for the current user
        :rtype: dict
        """
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
        """Get a JSON object with the agent configuration

        :return: the agents configured for the current user
        :rtype: JSON
        """
        return json.dumps(self.to_dict())


class User(object):
    """FOSSology user.

    Represents the user currently authenticated against the FOSSology server.

    :param id: the user ID
    :param name: the user name
    :param description: further information about the user
    :param email: the user's email
    :param accessLevel: TBD
    :param rootFolderId: the ID of the user's root folder
    :param emailNotification: are email notifications configured for that user?
    :param agents: the default agent configuration for the user
    :param kwargs: handle any other user information provided by the fossology instance
    :type id: int
    :type name: string
    :type description: string
    :type email: string
    :type accessLevel: string
    :type rootFolderId: int
    :type emailNotification: boolean
    :type agents: Agents
    :type kwargs: key word argument
    """

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
        agents: dict | None = None,
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
    """FOSSology group member.

    Represents a member of a group.

    :param user: the user data structure of the member
    :param group_perm: the permission of the user in the group (0: User, 1: Admin, 2: Advisor)
    :param kwargs: handle any other folder information provided by the fossology instance
    :type user: User
    :type group_perm: int
    :type kwargs: key word argument
    """

    def __init__(
        self,
        user: User,
        group_perm: int,
        **kwargs: dict,
    ):
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
    :param kwargs: handle any other folder information provided by the fossology instance
    :type id: int
    :type name: string
    :type description: string
    :type parent: int
    :type kwargs: key word argument
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

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Findings(object):
    """FOSSology license findings.

    Represents FOSSology license findings.

    :param scanner: the list of licenses found by the specified scanners
    :param conclusion: the concluded license by user of for a package
    :param copyright: the copyrights found in the package
    :param kwargs: handle any other finding information provided by the fossology instance
    :type scanner: list
    :type conclusion: list
    :type copyright: list
    :type kwargs: key word argument
    """

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
        return (
            f"Licenses found by scanners: {self.scanner}, concluded licenses: {self.conclusion}, "
            f"{len(self.copyright)} copyrights"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Group(object):
    """FOSSology group.

    Represents a FOSSology group.

    :param id: the ID of the group
    :param name: the name of the group
    :param kwargs: handle any other folder information provided by the fossology instance
    :type id: int
    :type name: string
    :type kwargs: key word argument
    """

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
    """GroupIds with their respective permissions for a upload

    Represents the group permissions for a FOSSology upload.

    :param perm: the permission
    :param group_pk: the id of the group
    :param group_name: the name of the group
    :type perm: str
    :type group_pk: str
    :type group_name: str
    """

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
    """Upload permissions

    Represents the permissions for a FOSSology upload.

    :param publicPerm: the public permission of the group
    :param permGroups: array of permGroup objects for the upload
    :param kwargs: handle any other folder information provided by the fossology instance
    :type publicPerm: str
    :type permGroups: array
    :type kwargs: key word argument
    """

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
    """FOSSology license.

    Represents a FOSSology license.

    :param shortName: the short name of the license
    :param fullName: the full name of the license
    :param text: the text of the license
    :param url: URL of the license text
    :param risk: the risk level of the license
    :param isCandidate: is the license a candidate?
    :param kwargs: handle any other folder information provided by the fossology instance
    :type shortName: string
    :type fullName: string
    :type text: string
    :type url: string
    :type risk: int
    :type isCandidate: bool
    :type kwargs: key word argument
    """

    def __init__(
        self, shortName, fullName, text, url, risk, isCandidate, id=None, **kwargs
    ):
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
        """Get a directory with the license data

        :return: the license data
        :rtype: dict
        """
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
        """Get a JSON object with the license data

        :return: the license data
        :rtype: JSON
        """
        return json.dumps(self.to_dict())


class Obligation(object):
    """FOSSology license obligation.

    Represents a FOSSology license obligation.

    :param id: the ID of the obligation
    :param topic: the topic of the obligation
    :param type: the type of the obligation
    :param text: the text of the obligation
    :param classification: level of attention it should raise in the clearing process
    :param comment: comment for the obligation
    :param kwargs: handle any other folder information provided by the fossology instance
    :type id: int
    :type topic: string
    :type type: string
    :type text: string
    :type classification: string
    :type comment: string
    :type kwargs: key word argument
    """

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
    """FOSSology hash.

    Represents a FOSSology file hash values.

    :param sha1: the SHA1 hash sum of the file
    :param md5: the MDA check sum of the file
    :param sha256: the SHA256 hash sum of the file
    :param size: the size of the file in bytes
    :param kwargs: handle any other hash information provided by the fossology instance
    :type sha1: string
    :type md5: string
    :type sha256: string
    :type size: int
    :type kwargs: key word argument
    """

    def __init__(
        self,
        sha1,
        md5,
        sha256,
        size,
        **kwargs,
    ):
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
    """FOSSology file response from filesearch.

    Represents a FOSSology filesearch response.

    :param hash: the hash information of the file
    :param findings: the license findings in that file
    :param kwargs: handle any other license information provided by the fossology instance
    :type hash: Hash
    :type findings: Findings
    :type kwargs: key word argument
    """

    def __init__(
        self,
        hash,
        findings,
        **kwargs,
    ):
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
    """FOSSology file info response.

    Represents a FOSSology file info response.

    :param view_info: view info of the file
    :param meta_info: meta info of the file
    :param package_info: package info of the file
    :param tag_info: tag info of the file
    :param reuse_info: reuse info of the file
    :param kwargs: handle any other license information provided by the fossology instance
    :type view_info: Object
    :type meta_info: Object
    :type package_info: Object
    :type tag_info: Object
    :type reuse_info: Object
    :type kwargs: key word argument
    """

    def __init__(
        self,
        view_info,
        meta_info,
        package_info,
        tag_info,
        reuse_info,
        **kwargs,
    ):
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
    """FOSSology upload.

    Represents a FOSSology upload.

    :param folderid: the ID of the upload folder
    :param foldername: the name of the upload folder
    :param id: the ID of the upload
    :param description: further information about the upload
    :param uploadname: the name of the upload (default: the name of the upload file)
    :param uploaddate: the date of the upload
    :param assignee: the user who is assigned to the upload
    :param assigneeDate: the date of the assignment
    :param closingDate: the date of the closing
    :param hash: the hash data of the uploaded file
    :param kwargs: handle any other upload information provided by the fossology instance
    :type folderid: int
    :type foldername: string
    :type id: int
    :type description: string
    :type uploadname: string
    :type uploaddate: string
    :type assignee: string
    :type assigneeDate: string
    :type closingDate: string
    :type hash: Hash
    :type kwargs: key word argument
    """

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
    """Copyright findings in a FOSSology upload

    Represents copyright matches of a FOSSology upload.

    :param copyright: the copyright
    :param filePath: relative file path
    :param kwargs: handle any other information provided by the FOSSology instance
    :type copyright: str
    :type filePath: list
    :type kwargs: key word argument
    """

    def __init__(
        self,
        copyright: str,
        filePath: list[str],
        **kwargs,
    ):
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
    """FOSSology upload licenses.

    Represents licenses and copyright matches of a FOSSology upload.

    :param filePath: relative file path
    :param findings: the licenses and copyrights findings
    :param kwargs: handle any other information provided by the fossology instance
    :type filePath: str
    :type findings: Findings
    :type kwargs: key word argument
    """

    def __init__(
        self,
        filePath: str,
        findings: dict,
        **kwargs,
    ):
        self.filepath = filePath
        self.findings = Findings.from_json(findings)
        self.additional_info = kwargs

    def __str__(self):
        return f"File {self.filepath} has {len(self.findings.conclusion)} license and {len(self.findings.copyright)}matches"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Summary(object):
    """FOSSology upload summary.

    Represents a FOSSology upload summary.

    :param id: the ID of the upload
    :param uploadName: the name of the upload
    :param mainLicense: the main upload license
    :param uniqueLicenses: the number of unique licenses
    :param totalLicenses: the total number of licenses
    :param uniqueConcludedLicenses: the number of unique concluded licenses
    :param totalConcludedLicenses: the total number of concluded licenses
    :param filesToBeCleared: the number of remaining files to be cleared
    :param filesCleared: the number of files already cleared
    :param clearingStatus: the clearing status
    :param copyrightCount: the number of copyrights found
    :param kwargs: handle any other summary information provided by the fossology instance
    :type id: int
    :type uploadName: string
    :type mainLicense: string
    :type uniqueLicenses: int
    :type totalLicenses: int
    :type uniqueConcludedLicenses: int
    :type totalConcludedLicenses: int
    :type filesToBeCleared: int
    :type filesCleared: int
    :type clearingStatus: string
    :type copyrightCount: int
    :type kwargs: key word argument
    """

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
    """FOSSology job.

    Represents a FOSSology job.

    :param id: the ID of the job
    :param name: the name of the job
    :param queueDate: the start date of the job
    :param uploadId: the ID of the upload
    :param userId: the ID of the user wo started the job
    :param groupId: the ID of the job's group
    :param eta: the estimated termination time
    :param status: the status of the job
    :param kwargs: handle any other job information provided by the fossology instance
    :type id: int
    :type name: string
    :type queueDate: string
    :type uploadId: int
    :type userId: int
    :type groupId: int
    :type eta: string
    :type status: string
    :type kwargs: key word argument
    """

    def __init__(
        self, id, name, queueDate, uploadId, userId, groupId, eta, status, **kwargs
    ):
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
    """FOSSology job download

    Represents a FOSSology job download.

    :param text: text for download link
    :param link: link to download the report
    :param kwargs: handle any other job download information provided by the fossology instance
    :type text: string
    :type link: string
    :type kwargs: dict
    """

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
    """FOSSology job queue.

    Represents a FOSSology job queue.

    :param jobQueueId: job queue ID
    :param jobQueueType: job queue type (agent name)
    :param startTime: job queue start time
    :param endTime: job queue end time
    :param status: job queue complemention status
    :param itemsProcessed: number of items processes
    :param log: location of the log file (if it exists)
    :param dependencies: list of dependent job queue ids
    :param itemsPerSec: number of items processed per second
    :param canDoActions: job can accept new actions like pause and cancel
    :param isInProgress: checks if the job queue is still in progress
    :param isReady: is the job ready
    :param download: report download information
    :param kwargs: handle any other job queue information provided by the fossology instance
    :type jobQueueId: int
    :type jobQueueType: string
    :type startTime: string
    :type endTime: string
    :type status: string
    :type itemsProcessed: int
    :type log: string
    :type dependencies: list(int)
    :type itemsPerSec: float
    :type canDoActions: bool
    :type isInProgress: bool
    :type isReady: bool
    :type download: JobDownload
    :type kwargs: key word argument
    """

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
    """FOSSology job

    Represents the history of all the jobs and the job queue info

    :param jobId: job ID
    :param jobName: job name (generally upload name)
    :param jobQueue: jobs queued for the current job
    :param uploadId: upload ID to which the job belongs to
    :type jobId: int
    :type jobName: string
    :type jobQueue: list of JobQueue
    :type uploadId: int
    """

    def __init__(
        self,
        jobId: int,
        jobName: str,
        jobQueue: list[JobQueue],
        uploadId: int,
    ):
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
    """FOSSology API License.

    :param name: name of the API license
    :param url: link to the license text
    :type name: string
    :type url: string
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __str__(self):
        return f"API license '{self.name}' ({self.url})"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class FossologyServer(object):
    """FOSSology server info.

    :param version: version of the FOSSology server (e.g. 4.0.0)
    :param branchName: branch deployed on the FOSSology server
    :param commitHash: hash of commit deployed on the FOSSology server
    :param commitDate: date of commit deployed on the FOSSology server in ISO8601 format
    :param buildDate: date on which packages were built in ISO8601 format
    :type version: string
    :type branchName: string
    :type commitHash: string
    :type commitDate: string
    :type buildDate: string
    """

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
    """FOSSology API info.

    Represents the info endpoint of FOSSology API.

    :param name: the name of the API service
    :param description: additional information
    :param version: current API version
    :param security: security methods allowed
    :param contact: email contact from the API documentation
    :param license: licensing of the API
    :param fossology: information about FOSSology server
    :type name: string
    :type description: string
    :type version: string
    :type security: list
    :type contact: string
    :type license: ApiLicense object
    :type fossology: FossologyServer object
    :type kwargs: key word argument
    """

    def __init__(
        self,
        name,
        description,
        version,
        security,
        contact,
        license,
        fossology,
        **kwargs,
    ):
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
    """FOSSology server status

    Represent the status of FOSSology sub-systems

    :param status: the status of the sub-system (OK, ERROR)
    :type status: string
    """

    def __init__(self, status):
        self.status = status

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class HealthInfo(object):
    """FOSSology server health info.

    Represents the health endpoint of FOSSology API.

    :param status: the overall status of the API service (OK, WARN, ERROR)
    :param scheduler: the status of the FOSSology scheduler
    :param db: the status of the FOSSology DB
    :type status: string
    :type scheduler: Status object
    :type db: Status object
    :type kwargs: key word argument
    """

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
    """Search result.

    Represents a search response from FOSSology API.

    :param upload: upload where the searched file has been found
    :param uploadTreeId: id of the upload tree
    :param filename: filename of the tree item
    :param kwargs: handle any other job information provided by the fossology instance
    :type upload: Upload
    :type uploadTreeId: int
    :type filename: string
    :type kwargs: key word argument
    """

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
    """Clearing history.

    Represents the clearing history of a specified item.

    :param date: date of the clearing history
    :param username: username of the user who created the decision
    :param scope: scope of the clearing
    :param type: type of the clearing
    :param addedLicenses: list of license shortnames added to the decision
    :param removedLicenses: list of license shortnames removed to the decision
    :param kwargs: handle any other job information provided by the fossology instance
    :type date: string
    :type username: string
    :type scope: str
    :type type: str
    :type addedLicenses: List[str]
    :type removedLicenses: List[str]
    :type kwargs: key word argument
    """

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
    """Bulk history.

    Represents the bulk history of a specified item.

    :param bulkId: the bulk id
    :param clearingEventId: the event id associated with the bulk
    :param text: scan reference text
    :param matched: whether matched or not
    :param tried: whether tried or not
    :param addedLicenses: list of license shortnames added to the scan
    :param removedLicenses: list of license shortnames removed to the scan
    :param kwargs: handle any other job information provided by the fossology instance
    :type bulkId: int
    :type clearingEventId: int
    :type text: str
    :type matched: bool
    :type tried: bool
    :type addedLicenses: List[str]
    :type removedLicenses: List[str]
    :type kwargs: key word argument
    """

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
    """PrevNext item for the clearing history.

    Represents the prev-next item list for the clearing history.

    :param prevItemId: id of the previous item
    :param nextItemId: id of the next item
    :param kwargs: handle any other job information provided by the fossology instance
    :type prevItemId: int
    :type nextItemId: int
    :type kwargs: key word argument
    """

    def __init__(
        self,
        prevItemId: int,
        nextItemId: int,
        **kwargs,
    ):
        self.prevItemId = prevItemId
        self.nextItemId = nextItemId
        self.additional_info = kwargs

    def __str__(self):
        return f"Prev: {self.prevItemId} | Next: {self.nextItemId}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)
