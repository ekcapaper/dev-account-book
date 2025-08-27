# tests/test_account_entry_repository_integration.py
from datetime import datetime
import pytest
from devaccountbook_backend.repositories.account_entry_repo import AccountEntryRepository
from devaccountbook_backend.schemas.account_entry_schemas import RelKind

def test_bootstrap(repo: AccountEntryRepository):
    # 제약 생성 쿼리가 오류 없이 실행되면 OK (별도 검증은 생략)
    # 동일 제약 재호출도 IF NOT EXISTS라 문제가 없어야 함
    repo.bootstrap()

def test_create_and_get_and_count(repo: AccountEntryRepository):
    new_id = repo.create_entry("t1", "d1", ["a", "b"])
    assert isinstance(new_id, str)

    got = repo.get_entry(new_id)
    assert got is not None
    assert got["id"] == new_id
    assert got["title"] == "t1"
    assert got["desc"] == "d1"
    assert got["tags"] == ["a", "b"]
    assert "createdAt" in got  # datetime으로 normalize 되었을 수 있음

    cnt = repo.count_entries()
    assert cnt == 1

def test_get_entries_paging(repo: AccountEntryRepository):
    ids = [repo.create_entry(f"title-{i}", None, [f"t{i}"]) for i in range(5)]
    rows = repo.get_entries(limit=3, offset=0)
    assert len(rows) == 3
    rows2 = repo.get_entries(limit=3, offset=3)
    assert len(rows2) == 2
    # 최신 createdAt DESC 이므로 첫 페이지와 두 번째 페이지가 겹치지 않아야 함
    returned_ids = {r["id"] for r in rows} | {r["id"] for r in rows2}
    assert set(ids) == returned_ids

def test_update_entry(repo: AccountEntryRepository):
    new_id = repo.create_entry("old", "old-desc", ["x"])
    ok_none = repo.update_entry(new_id, {})  # 빈 props → False
    assert ok_none is False

    ok = repo.update_entry(new_id, {"title": "new", "desc": None, "tags": ["y"], "bad": "ignored"})
    assert ok is True

    updated = repo.get_entry(new_id)
    assert updated["title"] == "new"
    assert updated["tags"] == ["y"]
    assert "updatedAt" in updated

def test_delete_entry(repo: AccountEntryRepository):
    new_id = repo.create_entry("will-delete", None, [])
    assert repo.get_entry(new_id) is not None

    ok = repo.delete_entry(new_id)
    assert ok is True

    assert repo.get_entry(new_id) is None
    assert repo.count_entries() == 0

def test_relations_add_get_delete(repo: AccountEntryRepository):
    a = repo.create_entry("A", None, [])
    b = repo.create_entry("B", None, [])
    c = repo.create_entry("C", None, [])

    # RELATES_TO (Enum 화이트리스트)
    kind = repo.add_relation(a, b, RelKind.RELATES_TO, {"weight": 1})
    assert kind == "RELATES_TO"
    repo.add_relation(a, c, RelKind.RELATES_TO, {"weight": 2})

    rels = repo.get_relations(a)
    assert "outgoing" in rels and "incoming" in rels
    outgoing = rels["outgoing"]
    assert len(outgoing) == 2
    assert {r["to_id"] for r in outgoing} == {b, c}
    assert outgoing[0]["props"]  # normalize_neo가 dict 유지

    # 삭제
    deleted_cnt = repo.delete_relation(a, b, RelKind.RELATES_TO)
    assert deleted_cnt >= 1

    rels2 = repo.get_relations(a)
    assert len(rels2["outgoing"]) == 1
    assert rels2["outgoing"][0]["to_id"] == c

@pytest.mark.skipif(not pytest.lazy_fixture("has_apoc"), reason="APOC not available")
def test_get_entry_tree_with_apoc(repo: AccountEntryRepository, has_apoc: bool):
    # 그래프: A -> B, A -> C
    a = repo.create_entry("A", None, [])
    b = repo.create_entry("B", None, [])
    c = repo.create_entry("C", None, [])
    repo.add_relation(a, b, RelKind.RELATES_TO, {})
    repo.add_relation(a, c, RelKind.RELATES_TO, {})

    tree = repo.get_entry_tree(a)
    # normalize_to_children 가 어떤 형태로 변환하든 최소한 값은 존재해야 함
    assert tree is not None
