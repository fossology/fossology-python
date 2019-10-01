# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT

from enum import Enum


class AccessLevel(Enum):
    """Access level for uploads: PRIVATE, PROTECTED, PUBLIC"""

    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"


class Agents(object):

    """FOSSology agents.

    Represents the agents currently configured for a given user.
    """

    def __init__(
        self,
        bucket,
        copyright_email_author,
        ecc,
        keyword,
        patent,
        mimetype,
        monk,
        nomos,
        ojo,
        package,
    ):
        self.bucket = bucket
        self.copyright_email_author = copyright_email_author
        self.ecc = ecc
        self.keyword = keyword
        self.patent = patent
        self.mimetype = mimetype
        self.monk = monk
        self.nomos = nomos
        self.ojo = ojo
        self.package = package

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class User(object):

    """FOSSology user.

    Represents the user currently authenticated against the FOSSology server.
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
        agents,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.email = email
        self.accessLevel = accessLevel
        self.rootFolderId = rootFolderId
        self.emailNotification = emailNotification
        self.agents = agents

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
    """

    def __init__(self, id, name, description, parent):
        self.id = id
        self.name = name
        self.description = description
        self.parent = parent

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
    """

    def __init__(
        self, folderid, foldername, id, description, uploadname, uploaddate, filesize
    ):
        self.folderid = folderid
        self.foldername = foldername
        self.id = id
        self.description = description
        self.uploadname = uploadname
        self.uploaddate = uploaddate
        self.filesize = filesize

    def __str__(self):
        return (
            f"Upload '{self.uploadname}' ({self.id}, {self.filesize}B) "
            f"in folder {self.foldername} ({self.folderid})"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Job(object):

    """FOSSology job.

    Represents a FOSSology job.
    FIXME eta and status information are not available in API version 1.0.3
    """

    def __init__(self, id, name, queueDate, uploadId, userId, groupId, eta, status):
        self.id = id
        self.name = name
        self.queueDate = queueDate
        self.uploadId = uploadId
        self.userId = userId
        self.groupId = groupId
        self.eta = eta
        self.status = status

    def __str__(self):
        return (
            f"Job '{self.name}' ({self.id}) queued on {self.queueDate} "
            f"(Status: {self.status} ETA: {self.eta})"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)
