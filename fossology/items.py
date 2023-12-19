# mypy: disable-error-code="attr-defined"
# Copyright 2019 Siemens AG
# SPDX-License-Identifier: MIT
import json
import logging

from fossology.enums import CopyrightStatus, PrevNextSelection
from fossology.exceptions import FossologyApiError
from fossology.obj import (
    FileInfo,
    GetBulkHistory,
    GetClearingHistory,
    GetPrevNextItem,
    Upload,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Items:
    """Class dedicated to all "uploads...items" related endpoints"""

    def item_info(
        self,
        upload: Upload,
        item_id: int,
    ) -> FileInfo:
        """Get the info for a specific upload item

        API Endpoint: GET /uploads/{id}/item/{itemId}/info

        :param upload: the upload to get items from
        :param item_id: the id of the item
        :type upload: Upload
        :type item_id: int,
        :return: the file info for the specified item
        :rtype: FileInfo
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/item/{item_id}/info"
        )

        if response.status_code == 200:
            return FileInfo.from_json(response.json())

        elif response.status_code == 404:
            description = f"Upload {upload.id} or item {item_id} not found"
            raise FossologyApiError(description, response)
        else:
            description = f"API error while getting info for item {item_id} from upload {upload.uploadname}"
            raise FossologyApiError(description, response)

    def item_copyrights(
        self,
        upload: Upload,
        item_id: int,
        status: CopyrightStatus,
    ) -> int:
        """Get the total copyrights of the mentioned upload tree ID

        API Endpoint: GET /uploads/{id}/item/{itemId}/totalcopyrights

        :param upload: the upload to get items from
        :param item_id: the id of the item
        :param status: the status of the copyrights
        :type upload: Upload
        :type item_id: int,
        :return: the total number of copyrights for the uploadtree item
        :rtype: int
        :raises FossologyApiError: if the REST call failed
        """
        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/item/{item_id}/totalcopyrights?status={status.value}"
        )

        if response.status_code == 200:
            return response.json()["total_copyrights"]

        elif response.status_code == 404:
            description = f"Upload {upload.id} or item {item_id} not found"
            raise FossologyApiError(description, response)
        else:
            description = f"API error while getting total copyrights for item {item_id} from upload {upload.uploadname}."
            raise FossologyApiError(description, response)

    def get_clearing_history(
        self,
        upload: Upload,
        item_id: int,
    ) -> list[GetClearingHistory]:
        """Get the clearing history for a specific upload item

        API Endpoint: GET /uploads/{id}/item/{itemId}/clearing-history

        :param upload: the upload to get items from
        :param item_id: the id of the item with clearing decision
        :type upload: Upload
        :type item_id: int,
        :return: the clearing history for the specified item
        :rtype: List[GetClearingHistory]
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/item/{item_id}/clearing-history"
        )

        if response.status_code == 200:
            clearing_history = []
            for action in response.json():
                clearing_history.append(GetClearingHistory.from_json(action))
            return clearing_history

        elif response.status_code == 404:
            description = f"Upload {upload.id} or item {item_id} not found"
            raise FossologyApiError(description, response)
        else:
            description = f"API error while getting clearing history for item {item_id} from upload {upload.uploadname}."
            raise FossologyApiError(description, response)

    def get_prev_next(
        self, upload: Upload, item_id: int, selection: PrevNextSelection | None = None
    ) -> GetPrevNextItem:
        """Get the index of the previous and the next time for an upload

        API Endpoint: GET /uploads/{id}/item/{itemId}/prev-next

        :param upload: the upload to get items from
        :param item_id: the id of the item with clearing decision
        :param selection: tell Fossology server how to select prev-next item
        :type upload: Upload
        :type item_id: int
        :type selection: str
        :return: list of items for the clearing history
        :rtype: List[GetPrevNextItem]
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        params = {}
        if selection:
            params["selection"] = selection

        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/item/{item_id}/prev-next", params=params
        )

        if response.status_code == 200:
            return GetPrevNextItem.from_json(response.json())

        elif response.status_code == 404:
            description = f"Upload {upload.id} or item {item_id} not found"
            raise FossologyApiError(description, response)
        else:
            description = f"API error while getting prev-next items for {item_id} from upload {upload.uploadname}."
            raise FossologyApiError(description, response)

    def get_bulk_history(
        self,
        upload: Upload,
        item_id: int,
    ) -> list[GetBulkHistory]:
        """Get the bulk history for a specific upload item

        API Endpoint: GET /uploads/{id}/item/{itemId}/bulk-history

        :param upload: the upload to get items from
        :param item_id: the id of the item with clearing decision
        :type upload: Upload
        :type item_id: int
        :return: list of data from the bulk history
        :rtype: List[GetBulkHistory]
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        response = self.session.get(
            f"{self.api}/uploads/{upload.id}/item/{item_id}/bulk-history"
        )

        if response.status_code == 200:
            bulk_history = []
            for item in response.json():
                bulk_history.append(GetBulkHistory.from_json(item))
            return bulk_history

        elif response.status_code == 404:
            description = f"Upload {upload.id} or item {item_id} not found"
            raise FossologyApiError(description, response)
        else:
            description = f"API error while getting bulk history for {item_id} from upload {upload.uploadname}."
            raise FossologyApiError(description, response)

    def schedule_bulk_scan(
        self,
        upload: Upload,
        item_id: int,
        spec: dict,
    ):
        """Schedule a bulk scan for a specific upload item

        API Endpoint: POST /uploads/{id}/item/{itemId}/bulk-scan

        Bulk scan specifications `spec` are added to the request body,
        following options are available:

        >>> bulk_scan_spec = {
        ...     "bulkActions": [
        ...         {
        ...             "licenseShortName": 'MIT',
        ...             "licenseText": 'License text',
        ...             "acknowledgement": 'Acknowledgment text',
        ...             "comment": 'Comment text',
        ...             "licenseAction": 'ADD', # or 'REMOVE'
        ...         }
        ...     ],
        ...     "refText": 'Reference Text',
        ...     "bulkScope": 'folder', # or upload
        ...     "forceDecision": 'false',
        ...     "ignoreIrre": 'false',
        ...     "delimiters": 'DEFAULT',
        ...     "scanOnlyFindings": 'true',
        ... }

        :param upload: the upload for the bulk scan
        :param item_id: the id of the item for the bulk scan
        :param spec: bulk scan specification
        :type upload: Upload
        :type item_id: int
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        headers = {"Content-Type": "application/json"}
        response = self.session.post(
            f"{self.api}/uploads/{upload.id}/item/{item_id}/bulk-scan",
            headers=headers,
            data=json.dumps(spec),
        )
        if response.status_code == 201:
            logger.info(
                f"Bulk scan scheduled for upload {upload.uploadname}, item {item_id}"
            )
        elif response.status_code == 400:
            description = (
                f"Bad bulk scan request for upload {upload.id}, item {item_id}"
            )
            raise FossologyApiError(description, response)
        elif response.status_code == 404:
            description = f"Upload {upload.id} or item {item_id} not found"
            raise FossologyApiError(description, response)
        else:
            description = f"API error while scheduling bulk scan for item {item_id} from upload {upload.uploadname}."
            raise FossologyApiError(description, response)
