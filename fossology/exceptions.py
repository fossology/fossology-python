# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

from json.decoder import JSONDecodeError


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class AuthenticationError(Error):
    """Authentication error"""

    def __init__(self, description, response=None):
        if response:
            try:
                message = response.json().get("message")
            except JSONDecodeError:
                message = response.text
            self.message = f"{description}: {message} ({response.status_code})"
        else:
            self.message = description


class AuthorizationError(Error):
    """Authorization error"""

    def __init__(self, description, response):
        try:
            message = response.json().get("message")
        except JSONDecodeError:
            message = response.text
        self.message = f"{description}: {message} ({response.status_code})"


class FossologyApiError(Error):
    """Error during a Fossology request"""

    def __init__(self, description, response=None):
        try:
            message = response.json().get("message")
        except JSONDecodeError:
            message = response.text
        self.message = f"{description}: {message} ({response.status_code})"


class FossologyUnsupported(Error):
    """Endpoint or option not supported"""

    def __init__(self, description):
        self.message = description
