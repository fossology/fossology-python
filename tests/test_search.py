# Copyright 2019-2020 Siemens AG
# SPDX-License-Identifier: MIT

import unittest

from test_base import foss
from fossology.obj import SearchTypes


class TestFossologySearch(unittest.TestCase):
    def test_search(self):
        search_result = foss.search(searchType=SearchTypes.ALLFILES, filename="GPL%")
        self.assertIsNotNone(search_result, "Couldn't search Fossology")
        search_result = foss.search(
            searchType=SearchTypes.ALLFILES,
            filename="test%",
            tag="test",
            filesizemin="0",
            filesizemax="1024",
            license="Artistic",
            copyright="Debian",
        )
        self.assertEqual(search_result, [], "Search result should be empty")


if __name__ == "__main__":
    unittest.main()
    foss.close()
