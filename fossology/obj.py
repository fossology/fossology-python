# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import json
from enum import Enum


class AccessLevel(Enum):
    """Available access levels for uploads:

    PRIVATE: the upload will only be visible to the owner

    PROTECTED: ?

    PUBLIC: the upload will be visible for everyone
    """

    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"


class ReportFormat(Enum):
    """Available report format: DEP5, SPDX2, SPDX2TV, READMEOSS, UNIFIEDREPORT"""

    DEP5 = "dep5"
    SPDX2 = "spdx2"
    SPDX2TV = "spdx2tv"
    READMEOSS = "readmeoss"
    UNIFIEDREPORT = "unifiedreport"


class SearchTypes(Enum):
    """Type of item that can be searched: ALLFILES, CONTAINERS, DIRECTORIES"""

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
    """Clearing statuses
    """

    OPEN = "Open"
    PROGRESS = "InProgress"
    CLOSED = "Closed"
    REJECTED = "Rejected"


class LicenseAgent(Enum):
    """Available license agents: NOMOS, MONK, NINKA, OJO, REPORTIMPORT"""

    NOMOS = "nomos"
    MONK = "monk"
    NINKA = "ninka"
    OJO = "ojo"
    REPORTIMPORT = "reportImport"


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


class Upload(object):

    """FOSSology upload.

    Represents a FOSSology upload.

    :param folderid: the ID of the upload folder
    :param foldername: the name of the upload folder
    :param id: the ID of the upload
    :param description: further information about the upload
    :param uploadname: the name of the upload (default: the name of the upload file)
    :param uploaddate: the date of the upload
    :param filesize: the size of the uploaded file in bytes
    :param filesha1: the SHA1 hash sum of the file
    :param kwargs: handle any other upload information provided by the fossology instance
    :type folderid: int
    :type foldername: string
    :type id: int
    :type description: string
    :type uploadname: string
    :type uploaddate: string
    :type filesize: int
    :type filesha1: string
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
        filesize,
        filesha1,
        **kwargs,
    ):
        self.folderid = folderid
        self.foldername = foldername
        self.id = id
        self.description = description
        self.uploadname = uploadname
        self.uploaddate = uploaddate
        self.filesize = filesize
        self.filesha1 = filesha1
        self.additional_info = kwargs

    def __str__(self):
        return (
            f"Upload '{self.uploadname}' ({self.id}, {self.filesize}B, {self.filesha1}) "
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
