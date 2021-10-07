from fossology.exceptions import FossologyApiError as FossologyApiError, FossologyUnsupported as FossologyUnsupported
from fossology.obj import Group as Group
from typing import Any, List

logger: Any

class Groups:
    def list_groups(self) -> List: ...
    def create_group(self, name) -> None: ...
