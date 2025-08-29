import pytest
from unittest.mock import MagicMock

from devaccountbook_backend.models.account_entry_domain import AccountEntryNode
from devaccountbook_backend.services.account_entry_service import AccountEntryService
from devaccountbook_backend.schemas.account_entry_schemas import (
    AccountEntryCreate, AccountEntryPatch, AccountEntryOut, RelationCreate, RelKind, RelationList
)
from devaccountbook_backend.dtos.account_entry_dto import (
    AccountEntryNodeCreateDTO, AccountEntryNodePatchDTO,
    AccountEntryRelationCreateDTO, AccountEntryRelationDeleteDTO
)

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.bootstrap.return_value = None
    return repo

@pytest.fixture
def service(mock_repo):
    return AccountEntryService(mock_repo)

def test_list_returns_account_entry_out(service, mock_repo):
    from datetime import datetime
    from datetime import timezone
    mock_repo.get_entries.return_value = [
        AccountEntryNode.model_validate(
        {"id": "1", "title": "Entry 1", "desc": "Test", "tags": [], "createdAt": datetime.now(timezone.utc),})
    ]

    result = service.list(limit=10, offset=0)

    assert isinstance(result[0], AccountEntryOut)
    assert result[0].id == "1"
    mock_repo.get_entries.assert_called_once_with(limit=10, offset=0)

def test_count(service, mock_repo):
    mock_repo.count_entries.return_value = 42

    assert service.count() == 42
    mock_repo.count_entries.assert_called_once()

def test_create(service, mock_repo):
    payload = AccountEntryCreate(title="New Entry", desc="desc", tags=["tag"])
    mock_repo.create_entry.return_value = "new_id"

    result = service.create(payload)

    assert result == "new_id"
    mock_repo.create_entry.assert_called_once()
    args, _ = mock_repo.create_entry.call_args
    assert isinstance(args[0], AccountEntryNodeCreateDTO)

def test_get(service, mock_repo):
    mock_repo.get_entry.return_value.model_dump.return_value = {
        "id": "1", "title": "test", "desc": None
    }

    result = service.get("1")

    assert isinstance(result, AccountEntryOut)
    assert result.id == "1"
    mock_repo.get_entry.assert_called_once_with("1")

def test_patch(service, mock_repo):
    payload = AccountEntryPatch(title="updated")
    mock_repo.update_entry.return_value = True

    result = service.patch("1", payload)

    assert result is True
    mock_repo.update_entry.assert_called_once()
    args, _ = mock_repo.update_entry.call_args
    assert isinstance(args[1], AccountEntryNodePatchDTO)

def test_delete(service, mock_repo):
    mock_repo.delete_entry.return_value = True

    assert service.delete("1") is True
    mock_repo.delete_entry.assert_called_once_with("1")

def test_link(service, mock_repo):
    # repo.get_entry → mock 객체 리턴
    mock_entry = MagicMock()
    mock_entry.model_dump.return_value = {"from_id": "1", "to_id": "2", "kind": "RELATES_TO"}
    mock_repo.get_entry.return_value = mock_entry
    mock_repo.add_relation.return_value = "rel_id"

    payload = RelationCreate(to_id="2", kind=RelKind.RELATES_TO)

    result = service.link("1", payload)

    assert result == "rel_id"
    mock_repo.add_relation.assert_called_once()
    args, _ = mock_repo.add_relation.call_args
    assert isinstance(args[0], AccountEntryRelationCreateDTO)

def test_list_links(service, mock_repo):
    mock_repo.get_relations.return_value.model_dump.return_value = {
        "outgoing": [], "incoming": []
    }

    result = service.list_links("1")

    assert isinstance(result, RelationList)
    mock_repo.get_relations.assert_called_once_with("1")

def test_unlink(service, mock_repo):
    mock_repo.delete_relation.return_value = 1

    result = service.unlink("1", "2", RelKind.RELATES_TO)

    assert result == 1
    mock_repo.delete_relation.assert_called_once()
    args, _ = mock_repo.delete_relation.call_args
    assert isinstance(args[0], AccountEntryRelationDeleteDTO)
