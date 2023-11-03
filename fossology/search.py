# mypy: disable-error-code="attr-defined"
# Copyright 2023 Siemens AG
# SPDX-License-Identifier: MIT
import logging

from fossology.enums import SearchTypes
from fossology.exceptions import AuthorizationError, FossologyApiError
from fossology.obj import File, SearchResult, Upload

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def search_headers(
    searchType: SearchTypes = SearchTypes.ALLFILES,
    upload: Upload | None = None,
    filename: str | None = None,
    tag: str | None = None,
    filesizemin: int | None = None,
    filesizemax: int | None = None,
    license: str | None = None,
    copyright: str | None = None,
    group: str | None = None,
    page_size: int = 100,
) -> dict:
    headers = {"searchType": searchType.value}
    if upload:
        headers["uploadId"] = str(upload.id)
    if filename:
        headers["filename"] = filename
    if tag:
        headers["tag"] = tag
    if filesizemin:
        headers["filesizemin"] = filesizemin  # type: ignore
    if filesizemax:
        headers["filesizemax"] = filesizemax  # type: ignore
    if license:
        headers["license"] = license
    if copyright:
        headers["copyright"] = copyright
    if group:
        headers["groupName"] = group
    headers["limit"] = str(page_size)
    return headers


class Search:
    """Class dedicated to all "search" related endpoints"""

    def search(
        self,
        searchType: SearchTypes = SearchTypes.ALLFILES,
        upload: Upload | None = None,
        filename: str | None = None,
        tag: str | None = None,
        filesizemin: int | None = None,
        filesizemax: int | None = None,
        license: str | None = None,
        copyright: str | None = None,
        group: str | None = None,
        page_size: int = 100,
        page: int = 1,
        all_pages: bool = False,
    ) -> tuple[list[SearchResult], int]:
        """Search for a specific file

        API Endpoint: GET /search

        :param searchType: Limit search to: directory, allfiles (default), containers
        :param upload: Limit search to a specific upload
        :param filename: Filename to find, can contain % as wild-card
        :param tag: tag to find
        :param filesizemin: Min filesize in bytes
        :param filesizemax: Max filesize in bytes
        :param license: License search filter
        :param copyright: Copyright search filter
        :param group: the group name to choose while performing search (default: None)
        :param page_size: limit the number of uploads per page (default: 100)
        :param page: the number of the page to fetch uploads from (default: 1)
        :param all_pages: get all uploads (default: False)
        :type searchType: one of SearchTypes Enum
        :type upload: Upload
        :type filename: string
        :type tag: string
        :type filesizemin: int
        :type filesizemax: int
        :type license: string
        :type copyright: string
        :type group: string
        :type page_size: int
        :type page: int
        :type all_pages: boolean
        :return: a tuple containing the list of search results and the total number of pages
        :rtype: tuple[list[SearchResult], int]
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        headers = search_headers(
            searchType,
            upload,
            filename,
            tag,
            filesizemin,
            filesizemax,
            license,
            copyright,
            group,
            page_size,
        )

        results_list = list()
        if all_pages:
            # will be reset after the total number of pages has been retrieved from the API
            x_total_pages = 2
        else:
            x_total_pages = page
        while page <= x_total_pages:
            headers["page"] = str(page)
            response = self.session.get(f"{self.api}/search", headers=headers)

            if response.status_code == 200:
                for result in response.json():
                    results_list.append(SearchResult.from_json(result))

                x_total_pages = int(response.headers.get("X-TOTAL-PAGES", 0))
                if not all_pages or x_total_pages == 0:
                    logger.info(
                        f"Retrieved page {page} of uploads, {x_total_pages} pages are in total available"
                    )
                    return results_list, x_total_pages
                page += 1

            else:
                description = "Unable to get a result with the given search criteria"
                raise FossologyApiError(description, response)

        logger.info(f"Retrieved all {x_total_pages} of search results")
        return results_list, x_total_pages

    def filesearch(
        self,
        filelist: list | None = None,
        group: str | None = None,
    ):
        """Search for files from hash sum

        API Endpoint: POST /filesearch

        The response does not generate Python objects yet, the plain JSON data is simply returned.

        :param filelist: the list of files (or containers) hashes to search for (default: [])
        :param group: the group name to choose while performing search (default: None)
        :type filelist: list
        :return: list of items corresponding to the search criteria
        :type group: string
        :rtype: JSON
        :raises FossologyApiError: if the REST call failed
        :raises AuthorizationError: if the REST call is not authorized
        """
        headers = {}
        if group:
            headers["groupName"] = group

        response = self.session.post(
            f"{self.api}/filesearch", headers=headers, json=filelist
        )

        if response.status_code == 200:
            all_files = []
            for hash_file in response.json():
                if hash_file.get("findings"):
                    all_files.append(File.from_json(hash_file))
                else:
                    return "Unable to get a result with the given filesearch criteria"
            return all_files

        elif response.status_code == 403:
            description = (
                "Not authorized to get a result with the given filesearch criteria"
            )
            raise AuthorizationError(description, response)

        else:
            description = "Unable to get a result with the given filesearch criteria"
            raise FossologyApiError(description, response)
