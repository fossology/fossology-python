# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import json
from enum import Enum


class AccessLevel(Enum):
    """Available access levels for uploads:

    PRIVATE
    PROTECTED
    PUBLIC

    """

    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"


class ReportFormat(Enum):
    """Available report format:

    DEP5
    SPDX2
    SPDX2TV
    READMEOSS
    UNIFIEDREPORT

    """

    DEP5 = "dep5"
    SPDX2 = "spdx2"
    SPDX2TV = "spdx2tv"
    READMEOSS = "readmeoss"
    UNIFIEDREPORT = "unifiedreport"


class SearchTypes(Enum):
    """Type of item that can be searched:

    ALLFILES
    CONTAINERS
    DIRECTORIES

    """

    ALLFILES = "allfiles"
    CONTAINERS = "containers"
    DIRECTORIES = "directories"


class TokenScope(Enum):
    """Scope for API tokens:

    READ: Read only access, limited only to "GET" calls

    WRITE: Read/Write access, required for calls other than "GET"

    """

    READ = "read"
    WRITE = "write"


class ClearingStatus(Enum):
    """Clearing statuses:

    OPEN
    INPROGRESS
    CLOSED
    REJECTED

    """

    OPEN = "Open"
    INPROGRESS = "InProgress"
    CLOSED = "Closed"
    REJECTED = "Rejected"


class LicenseType(Enum):
    """License types:

    CANDIDATE
    MAIN
    ALL

    """

    CANDIDATE = "candidate"
    MAIN = "main"
    ALL = "all"


class ObligationClass(Enum):
    """Classification of an obligation:

    GREEN
    WHITE
    YELLOW
    RED

    """

    GREEN = "green"
    WHITE = "white"
    YELLOW = "yellow"
    RED = "red"


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
        id,
        name,
        description,
        email,
        accessLevel,
        rootFolderId,
        emailNotification,
        agents=None,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.email = email
        self.accessLevel = accessLevel
        self.rootFolderId = rootFolderId
        self.emailNotification = emailNotification
        self.agents = agents
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"User {self.description} ({self.id}), {self.email}, "
            f"access level {self.accessLevel} "
            f"and root folder {self.rootFolderId}"
        )

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
    :type kwargs: key word argument
    """

    def __init__(
        self,
        scanner,
        conclusion,
        copyright=None,
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


class Licenses(object):

    """FOSSology file license findings.

    Represents a FOSSology licenses response.

    :param filePath: the path of the file in the specified upload
    :param findings: the license findings in that file
    :param kwargs: handle any other license information provided by the fossology instance
    :type filePath: string
    :type findings: Findings
    :type kwargs: key word argument
    """

    def __init__(
        self,
        filePath,
        findings=None,
        **kwargs,
    ):
        self.filepath = filePath
        if findings:
            self.findings = Findings.from_json(findings)
        else:
            self.findings = findings
        self.additional_info = kwargs

    def __str__(self):
        if self.findings.conclusion:
            return f"File {self.filepath} has {len(self.findings.conclusion)} concluded licenses"
        else:
            return f"File {self.filepath} doesn't have any concluded license yet"

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


class Upload(object):

    """FOSSology upload.

    Represents a FOSSology upload.

    :param folderid: the ID of the upload folder
    :param foldername: the name of the upload folder
    :param id: the ID of the upload
    :param description: further information about the upload
    :param uploadname: the name of the upload (default: the name of the upload file)
    :param uploaddate: the date of the upload
    :param hash: the hash data of the uploaded file
    :param kwargs: handle any other upload information provided by the fossology instance
    :type folderid: int
    :type foldername: string
    :type id: int
    :type description: string
    :type uploadname: string
    :type uploaddate: string
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
        filesize=None,
        filesha1=None,
        hash=None,
        **kwargs,
    ):
        self.folderid = folderid
        self.foldername = foldername
        self.id = id
        self.description = description
        self.uploadname = uploadname
        self.uploaddate = uploaddate
        if filesize and filesha1:
            self.filesize = filesize
            self.filesha1 = filesha1
            self.hash = None
        else:
            self.filesize = None
            self.filesha1 = None
            self.hash = Hash.from_json(hash)
        self.additional_info = kwargs

    def __str__(self):
        if self.filesize:
            return (
                f"Upload '{self.uploadname}' ({self.id}, {self.filesize}B, {self.filesha1}) "
                f"in folder {self.foldername} ({self.folderid})"
            )
        else:
            return (
                f"Upload '{self.uploadname}' ({self.id}, {self.hash.size}B, {self.hash.sha1}) "
                f"in folder {self.foldername} ({self.folderid})"
            )

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


class ApiInfo(object):

    """FOSSology API info.

    Represents the info endpoint of FOSSology API.

    :param name: the name of the API service
    :param description: additional information
    :param version: current API version
    :param security: security methods allowed
    :param contact: email contact from the API documentation
    :param license: licensing of the API
    :type name: string
    :type description: string
    :type version: string
    :type security: list
    :type contact: string
    :type license: ApiLicense object
    :type kwargs: key word argument
    """

    def __init__(
        self, name, description, version, security, contact, license, **kwargs
    ):
        self.name = name
        self.description = description
        self.version = version
        self.security = security
        self.contact = contact
        self.license = ApiLicense.from_json(license)
        self.additional_info = kwargs

    def __str__(self):
        return f"FOSSology API {self.name} is deployed with version {self.version}"

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


def get_options(group: str = None, folder: Folder = None) -> str:
    options = ""
    if group:
        options += f"for group {group} "
    if folder:
        options += f"in folder {folder.id} "
    return options
