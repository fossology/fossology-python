# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import unittest

from test_base import foss, logger
from fossology.exceptions import FossologyApiError
from fossology.obj import SearchTypes


class TestFossologySearch(unittest.TestCase):
    def test_search(self):
        try:
            search_result = foss.search(
                searchType=SearchTypes.ALLFILES, filename="GPL%"
            )
            self.assertIsNotNone(search_result, "Couldn't search Fossology")
        except FossologyApiError as error:
            logger.error(error.message)


if __name__ == "__main__":
    unittest.main()
    foss.close()
