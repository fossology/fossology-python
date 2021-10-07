from fossology.exceptions import AuthorizationError as AuthorizationError, FossologyApiError as FossologyApiError
from fossology.obj import Job as Job, get_options as get_options
from typing import Any

logger: Any

class Jobs:
    def list_jobs(self, upload: Any | None = ..., page_size: int = ..., page: int = ..., all_pages: bool = ...): ...
    def detail_job(self, job_id, wait: bool = ..., timeout: int = ...): ...
    def schedule_jobs(self, folder, upload, spec, group: Any | None = ..., wait: bool = ..., timeout: int = ...): ...
