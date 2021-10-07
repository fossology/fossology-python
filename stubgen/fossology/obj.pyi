from enum import Enum
from typing import Any

class AccessLevel(Enum):
    PRIVATE: str
    PROTECTED: str
    PUBLIC: str

class ReportFormat(Enum):
    DEP5: str
    SPDX2: str
    SPDX2TV: str
    READMEOSS: str
    UNIFIEDREPORT: str

class SearchTypes(Enum):
    ALLFILES: str
    CONTAINERS: str
    DIRECTORIES: str

class TokenScope(Enum):
    READ: str
    WRITE: str

class ClearingStatus(Enum):
    OPEN: str
    PROGRESS: str
    CLOSED: str
    REJECTED: str

class LicenseType(Enum):
    CANDIDATE: str
    MAIN: str
    ALL: str

class ObligationClass(Enum):
    GREEN: str
    WHITE: str
    YELLOW: str
    RED: str

class Agents:
    bucket: Any
    copyright_email_author: Any
    ecc: Any
    keyword: Any
    mimetype: Any
    monk: Any
    nomos: Any
    ojo: Any
    package: Any
    additional_agents: Any
    def __init__(self, bucket, copyright_email_author, ecc, keyword, mimetype, monk, nomos, ojo, package, **kwargs) -> None: ...
    def to_dict(self): ...
    @classmethod
    def from_json(cls, json_dict): ...
    def to_json(self): ...

class User:
    id: Any
    name: Any
    description: Any
    email: Any
    accessLevel: Any
    rootFolderId: Any
    emailNotification: Any
    agents: Any
    additional_info: Any
    def __init__(self, id, name, description, email, accessLevel, rootFolderId, emailNotification, agents: Any | None = ..., **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Folder:
    id: Any
    name: Any
    description: Any
    parent: Any
    additional_info: Any
    def __init__(self, id, name, description, parent, **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Findings:
    scanner: Any
    conclusion: Any
    copyright: Any
    additional_info: Any
    def __init__(self, scanner, conclusion, copyright: Any | None = ..., **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Group:
    id: Any
    name: Any
    additional_info: Any
    def __init__(self, id, name, **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class License:
    id: Any
    shortName: Any
    fullName: Any
    text: Any
    url: Any
    risk: Any
    isCandidate: Any
    additional_info: Any
    def __init__(self, shortName, fullName, text, url, risk, isCandidate, id: Any | None = ..., **kwargs) -> None: ...
    def to_dict(self): ...
    @classmethod
    def from_json(cls, json_dict): ...
    def to_json(self) -> str: ...

class Obligation:
    id: Any
    topic: Any
    type: Any
    text: Any
    classification: Any
    comment: Any
    additional_info: Any
    def __init__(self, id, topic, type, text, classification, comment, **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Licenses:
    filepath: Any
    findings: Any
    additional_info: Any
    def __init__(self, filePath, findings: Any | None = ..., **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Hash:
    sha1: Any
    md5: Any
    sha256: Any
    size: Any
    additional_info: Any
    def __init__(self, sha1, md5, sha256, size, **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class File:
    hash: Any
    findings: Any
    additional_info: Any
    def __init__(self, hash, findings, **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Upload:
    folderid: Any
    foldername: Any
    id: Any
    description: Any
    uploadname: Any
    uploaddate: Any
    filesize: Any
    filesha1: Any
    hash: Any
    additional_info: Any
    def __init__(self, folderid, foldername, id, description, uploadname, uploaddate, filesize: Any | None = ..., filesha1: Any | None = ..., hash: Any | None = ..., **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Summary:
    id: Any
    uploadName: Any
    mainLicense: Any
    uniqueLicenses: Any
    totalLicenses: Any
    uniqueConcludedLicenses: Any
    totalConcludedLicenses: Any
    filesToBeCleared: Any
    filesCleared: Any
    clearingStatus: Any
    copyrightCount: Any
    additional_info: Any
    def __init__(self, id, uploadName, mainLicense, uniqueLicenses, totalLicenses, uniqueConcludedLicenses, totalConcludedLicenses, filesToBeCleared, filesCleared, clearingStatus, copyrightCount, **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

class Job:
    id: Any
    name: Any
    queueDate: Any
    uploadId: Any
    userId: Any
    groupId: Any
    eta: Any
    status: Any
    additional_info: Any
    def __init__(self, id, name, queueDate, uploadId, userId, groupId, eta, status, **kwargs) -> None: ...
    @classmethod
    def from_json(cls, json_dict): ...

def get_options(group: str = ..., folder: Folder = ...) -> str: ...
