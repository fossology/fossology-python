# Copyright 2019 Siemens AG
# SPDX-License-Identifier: LicenseRef-SISL-1.1-or-later


class Agents(object):

    """FOSSology agents.

    Represents the agents currently configured for a given user.
    """
    def __init__(self, bucket, copyright_email_author, ecc, keyword, mimetype, monk, nomos, package):
        self.bucket = bucket
        self.copyright_email_author = copyright_email_author
        self.ecc = ecc
        self.keyword = keyword
        self.mimetype = mimetype
        self.monk = monk
        self.nomos = nomos
        self.package = package

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class User(object):

    """FOSSology user.

    Represents the user currently authenticated against the FOSSology server.
    """
    def __init__(self, id, name, description, email, accessLevel, rootFolderId, emailNotification, agents):
        self.id = id
        self.name = name
        self.description = description
        self.email = email
        self.accessLevel = accessLevel
        self.rootFolderId = rootFolderId
        self.emailNotification = emailNotification
        self.agents = agents

    def __repr__(self):
        return (
            f"User {self.description} ({self.id}), {self.email}, access level {self.accessLevel} "
            f"and root folder {self.rootFolderId}"
        )

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)


class Folder(object):

    """FOSSology folder.

    Represents a FOSSology folder.
    """
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return f"{self.name} ({self.id}), {self.description}"

    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)
