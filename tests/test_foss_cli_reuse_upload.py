# SPDX-License-Identifier: MIT

from types import SimpleNamespace
from unittest.mock import Mock

import click
import pytest

from fossology.foss_cli import get_newest_upload_of_file


@pytest.mark.parametrize(
    "upload_ids, expected_id",
    [
        ([1, 2], 1),
        ([2, 1], 1),
        ([1, 3], 1),
        ([3, 1], 1),
        ([2, 1, 3], 1),
        ([3], None),
        ([], None),
    ],
)
def test_get_newest_upload_of_file(upload_ids, expected_id):
    uploads = {
        1: SimpleNamespace(
            id=1,
            uploadname="package.tar.gz",
            uploaddate="2026-01-02 12:00:00+00",
        ),
        2: SimpleNamespace(
            id=2,
            uploadname="package.tar.gz",
            uploaddate="2026-01-01 12:00:00+00",
        ),
        3: SimpleNamespace(
            id=3,
            uploadname="unrelated.tar.gz",
            uploaddate="2026-01-03 12:00:00+00",
        ),
    }
    foss = Mock()
    foss.list_uploads.return_value = ([uploads[id] for id in upload_ids], 1)
    foss.detail_upload.side_effect = uploads.__getitem__
    ctx = click.Context(click.Command("test"), obj={"FOSS": foss})

    result = get_newest_upload_of_file(ctx, "/tmp/package.tar.gz", "")

    if expected_id is None:
        assert result is None
        foss.detail_upload.assert_not_called()
    else:
        assert result is uploads[expected_id]
        foss.detail_upload.assert_called_once_with(expected_id)
