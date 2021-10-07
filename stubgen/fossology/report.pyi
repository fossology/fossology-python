from fossology.exceptions import AuthorizationError as AuthorizationError, FossologyApiError as FossologyApiError
from fossology.obj import ReportFormat as ReportFormat, Upload as Upload, get_options as get_options
from typing import Any, Tuple

logger: Any

class Report:
    def generate_report(self, upload: Upload, report_format: ReportFormat = ..., group: str = ...): ...
    def download_report(self, report_id: int, group: str = ...) -> Tuple[str, str]: ...
