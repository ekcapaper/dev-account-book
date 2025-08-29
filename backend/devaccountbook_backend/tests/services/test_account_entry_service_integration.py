from devaccountbook_backend.schemas.account_entry_schemas import (
    AccountEntryCreate,
    AccountEntryPatch,
    AccountEntryOut,
    RelationCreate,
    RelKind,
    RelationList,
)
from devaccountbook_backend.services.account_entry_service import AccountEntryService
from devaccountbook_backend.tests.repo.conftest import *


@pytest.fixture
def service(repo: AccountEntryRepository) -> AccountEntryService:
    # conftest의 repo(실제 Neo4j 세션 연결)로 서비스 구성
    return AccountEntryService(repo)


def test_create_and_get(service: AccountEntryService):
    new_id = service.create(AccountEntryCreate(title="first", desc="hello", tags=["t1"]))
    assert isinstance(new_id, str) and new_id

    got = service.get(new_id)
    assert isinstance(got, AccountEntryOut)
    assert got.id == new_id
    assert got.title == "first"
    assert got.desc == "hello"


def test_list_and_count(service: AccountEntryService):
    a = service.create(AccountEntryCreate(title="A", desc=None, tags=[]))
    b = service.create(AccountEntryCreate(title="B", desc="bbb", tags=["x"]))

    cnt = service.count()
    assert cnt >= 2

    rows = service.list(limit=50, offset=0)
    assert isinstance(rows, list)
    assert all(isinstance(x, AccountEntryOut) for x in rows)
    ids = {x.id for x in rows}
    assert a in ids and b in ids


def test_patch(service: AccountEntryService):
    _id = service.create(AccountEntryCreate(title="before", desc=None, tags=[]))
    ok = service.patch(_id, AccountEntryPatch(title="after"))
    assert ok is True

    updated = service.get(_id)
    assert updated.title == "after"


def test_delete_then_get_none(service: AccountEntryService):
    _id = service.create(AccountEntryCreate(title="todelete", desc=None, tags=[]))
    ok = service.delete(_id)
    assert ok is True

    # 서비스 구현이 None을 반환하도록 의도되어 있으므로 None 기대
    # (만약 여기서 예외가 나면 service.get()에서 None 케이스 처리가 누락된 것)
    res = service.get(_id)
    assert res is None


def test_link_list_unlink(service: AccountEntryService):
    a = service.create(AccountEntryCreate(title="A", desc=None, tags=[]))
    b = service.create(AccountEntryCreate(title="B", desc=None, tags=[]))

    service.link(a, RelationCreate(to_id=b, kind=RelKind.RELATES_TO))

    rels = service.list_links(a)
    assert isinstance(rels, RelationList)
    assert any(r.to_id == b for r in rels.outgoing)

    deleted = service.unlink(a, b, RelKind.RELATES_TO)
    assert deleted >= 1


def test_get_start_to_end_node(service: AccountEntryService):
    root = service.create(AccountEntryCreate(title="root", desc=None, tags=[]))
    child = service.create(AccountEntryCreate(title="child", desc=None, tags=[]))
    # 필요 시 관계 생성 후 검증
    result = service.get_start_to_end_node(root)
    assert result is None

    service.link(root, RelationCreate(to_id=child, kind=RelKind.RELATES_TO))
    result = service.get_start_to_end_node(root)
    print(result)
