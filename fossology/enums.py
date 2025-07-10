# Copyright 2023 Siemens AG
# SPDX-License-Identifier: MIT

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
    CLIXML

    """

    DEP5 = "dep5"
    SPDX2 = "spdx2"
    SPDX2TV = "spdx2tv"
    READMEOSS = "readmeoss"
    UNIFIEDREPORT = "unifiedreport"
    CLIXML = "clixml"


class SearchTypes(Enum):
    """Type of item that can be searched:

    ALLFILES
    CONTAINERS
    DIRECTORY

    """

    ALLFILES = "allfiles"
    CONTAINERS = "containers"
    DIRECTORY = "directory"


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


class JobStatus(Enum):
    """Job statuses:

    COMPLETED
    FAILED
    QUEUED
    PROCESSING

    """

    COMPLETED = "Completed"
    FAILED = "Failed"
    QUEUED = "Queued"
    PROCESSING = "Processing"


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


class MemberPerm(Enum):
    """Group member permissions:

    USER
    ADMIN
    ADVISOR

    """

    USER = 0
    ADMIN = 1
    ADVISOR = 2


class Permission(Enum):
    """Upload or group permissions:

    NONE
    READ_ONLY
    READ_WRITE
    CLEARING_ADMIN
    ADMIN
    """

    NONE = "0"
    READ_ONLY = "1"
    READ_WRITE = "3"
    CLEARING_ADMIN = "5"
    ADMIN = "10"


class ClearingScope(Enum):
    """Scope of the clearing:

    LOCAL
    PACKAGE
    GLOBAL
    """

    LOCAL = "local"
    PACKAGE = "package"
    GLOBAL = "global"


class ClearingType(Enum):
    """Type of the clearing:

    TO_BE_DISCUSSED
    IRRELEVANT
    IDENTIFIED
    DO_NOT_USE
    NON_FUNCTIONAL
    """

    TO_BE_DISCUSSED = "TO_BE_DISCUSSED"
    IRRELEVANT = "IRRELEVANT"
    IDENTIFIED = "IDENTIFIED"
    DO_NOT_USE = "DO_NOT_USE"
    NON_FUNCTIONAL = "NON_FUNCTIONAL"


class PrevNextSelection(Enum):
    """Type of file to be selected for the prev-next endpoint:

    WITHLICENSES
    NOCLEARING
    """

    WITHLICENSES = "withLicenses"
    NOCLEARING = "noClearing"


class CopyrightStatus(Enum):
    """Status of the copyrights:

    ACTIVE
    INACTIVE
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
