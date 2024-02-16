# Copyright 2019 Siemens AG
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
        super().__init__(self.message)


class AuthorizationError(Error):
    """Authorization error"""

    def __init__(self, description, response):
        try:
            message = response.json().get("message")
        except JSONDecodeError:
            message = response.text
        self.message = f"{description}: {message} ({response.status_code})"
        super().__init__(self.message)


class FossologyApiError(Error):
    """Error during a Fossology request"""

    def __init__(self, description, response=None):
        try:
            message = response.json().get("message")
        except JSONDecodeError:
            message = response.text
        self.message = f"{description}: {message} ({response.status_code})"
        super().__init__(self.message)


class FossologyUnsupported(Error):
    """Endpoint or option not supported"""

    def __init__(self, description):
        self.message = description
        super().__init__(self.message)
