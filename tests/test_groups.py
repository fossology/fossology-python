# Copyright 2019-2021 Siemens AG
# SPDX-License-Identifier: MIT

import secrets
from unittest.mock import Mock, call

import pytest
import responses

import fossology
from fossology.exceptions import FossologyApiError
from fossology.obj import MemberPerm, User


# Helper functions
def get_group(foss: fossology.Fossology, name: str) -> int:
    for group in foss.list_groups():
        if group.name == name:
            return group


def verify_user_group_membership(
    foss: fossology.Fossology, group_id: int, user_id: int
) -> bool:
    for member in foss.list_group_members(group_id):
        if member.user.id == user_id:
            assert member.group_perm == MemberPerm.ADVISOR.value
            return True
    return False


# Test functions
@responses.activate
def test_list_groups_error(foss_server: str, foss: fossology.Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/groups", status=500)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.list_groups()
    assert f"Unable to get a list of groups for {foss.user.name}" in str(excinfo.value)


@responses.activate
def test_list_group_members_error(foss_server: str, foss: fossology.Fossology):
    responses.add(responses.GET, f"{foss_server}/api/v1/groups/42/members", status=500)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.list_group_members(42)
    assert "Unable to get a list of members for group 42" in str(excinfo.value)


@responses.activate
def test_delete_group_member_validation_error(
    foss_server: str, foss: fossology.Fossology
):
    responses.add(
        responses.DELETE, f"{foss_server}/api/v1/groups/42/user/42", status=400
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.delete_group_member(42, 42)
    assert "Validation error while removing member 42 from group 42." in str(
        excinfo.value
    )


@responses.activate
def test_delete_group_member_error(foss_server: str, foss: fossology.Fossology):
    responses.add(
        responses.DELETE, f"{foss_server}/api/v1/groups/42/user/42", status=500
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.delete_group_member(42, 42)
    assert "An error occurred while deleting user 42 from group 42" in str(
        excinfo.value
    )


@responses.activate
def test_delete_group_error(foss_server: str, foss: fossology.Fossology):
    group_id = secrets.randbelow(10)
    responses.add(
        responses.DELETE, f"{foss_server}/api/v1/groups/{group_id}", status=500
    )
    with pytest.raises(FossologyApiError) as excinfo:
        foss.delete_group(group_id)
    assert f"Group {group_id} could not be deleted" in str(excinfo.value)


def test_create_group(foss: fossology.Fossology):
    name = secrets.token_urlsafe(8)
    foss.create_group(name)
    group = get_group(foss, name)
    assert group

    # Recreate group to test API response 400
    with pytest.raises(FossologyApiError) as excinfo:
        foss.create_group(name)
    assert (
        f"Group {name} already exists, failed to create group or no group name provided"
        in str(excinfo.value)
    )
    # Cleanup
    foss.delete_group(group.id)


def test_list_deletable_groups(foss_server: str, foss: fossology.Fossology):
    name = secrets.token_urlsafe(8)
    foss.create_group(name)
    group = get_group(foss, name)
    assert group
    deletable_groups = foss.list_groups(deletable=True)
    assert deletable_groups
    for group in deletable_groups:
        foss.delete_group(group.id)


def test_list_group_members(foss: fossology.Fossology, created_foss_user: User):
    name = secrets.token_urlsafe(8)
    foss.create_group(name)
    group = get_group(foss, name)
    foss.add_group_member(group.id, created_foss_user.id, MemberPerm.ADVISOR)
    assert verify_user_group_membership(foss, group.id, created_foss_user.id)
    # Cleanup
    foss.delete_group(group.id)


def test_add_group_member_if_user_does_not_exists_raises_fossology_api_error(
    foss: fossology.Fossology,
):
    name = secrets.token_urlsafe(8)
    foss.create_group(name)
    group = get_group(foss, name)
    with pytest.raises(FossologyApiError) as excinfo:
        foss.add_group_member(group.id, 42, MemberPerm.ADVISOR)
    assert f"An error occurred while adding user 42 to group {group.id}" in str(
        excinfo.value
    )
    # Cleanup
    foss.delete_group(group.id)


def test_add_group_member_if_member_already_exists_returns_400(
    foss: fossology.Fossology, created_foss_user: User, monkeypatch: pytest.MonkeyPatch
):
    mocked_logger = Mock()
    monkeypatch.setattr("fossology.groups.logger", mocked_logger)
    name = secrets.token_urlsafe(8)
    foss.create_group(name)
    group = get_group(foss, name)
    foss.add_group_member(group.id, created_foss_user.id, MemberPerm.ADVISOR)
    assert verify_user_group_membership(foss, group.id, created_foss_user.id)
    assert (
        call(f"User {created_foss_user.id} has been added to group {group.id}.")
        in mocked_logger.info.mock_calls
    )
    foss.add_group_member(group.id, created_foss_user.id, MemberPerm.ADVISOR)
    assert (
        call(f"User {created_foss_user.id} is already a member of group {group.id}.")
        in mocked_logger.info.mock_calls
    )
    # Cleanup
    foss.delete_group(group.id)


def test_delete_group_member(foss: fossology.Fossology, created_foss_user: User):
    name = secrets.token_urlsafe(8)
    foss.create_group(name)
    group = get_group(foss, name)
    foss.add_group_member(group.id, created_foss_user.id, MemberPerm.ADVISOR)
    assert verify_user_group_membership(foss, group.id, created_foss_user.id)
    foss.delete_group_member(group.id, created_foss_user.id)
    assert not verify_user_group_membership(foss, group.id, created_foss_user.id)

    # Cleanup
    foss.delete_group(group.id)


def test_delete_group_member_if_group_does_not_exists_raises_fossology_api_error(
    foss: fossology.Fossology, created_foss_user: User
):
    with pytest.raises(FossologyApiError) as excinfo:
        foss.delete_group_member(42, created_foss_user.id)
    assert f"Member {created_foss_user.id} or group 42 not found." in str(excinfo.value)
