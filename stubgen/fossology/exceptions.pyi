from typing import Any

class Error(Exception): ...

class AuthenticationError(Error):
    message: Any
    def __init__(self, description, response: Any | None = ...) -> None: ...

class AuthorizationError(Error):
    message: Any
    def __init__(self, description, response) -> None: ...

class FossologyApiError(Error):
    message: Any
    def __init__(self, description, response: Any | None = ...) -> None: ...

class FossologyUnsupported(Error):
    message: Any
    def __init__(self, description) -> None: ...
