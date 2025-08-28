# tests/test_account_entries_router.py
import typing
from typing import Any, get_origin, get_args, List
from enum import Enum
from datetime import date, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

# ---- 프로젝트 경로에 맞게 아래 import 를 수정하세요 ----
from devaccountbook_backend.api.v1.account_entries_router import router
from devaccountbook_backend.services.account_entry_service import get_account_entry_service
from devaccountbook_backend.schemas.account_entry_schemas import (
    AccountEntryCreate, AccountEntryPatch, AccountEntryOut,
    RelationCreate, RelationOut, RelationList, RelKind
)

# ---------- 유틸: Pydantic(v1/v2) 모델을 자동으로 채워주는 샘플 빌더 ----------

def _first_enum_member(enum_cls: typing.Type[Enum]):
    try:
        return list(enum_cls)[0]
    except Exception:
        # 비어있을 리 없지만 방어적으로
        return None

def _sample_for_type(tp: Any):
    origin = get_origin(tp)
    args = get_args(tp)

    # Optional[T] / Union[T1, T2, ...]
    if origin is typing.Union:
        non_none = [a for a in args if a is not type(None)]
        return _sample_for_type(non_none[0]) if non_none else None

    # 리터럴
    if getattr(typing, "Literal", None) and origin is typing.Literal:
        return args[0]

    # 컨테이너
    if origin in (list, List, set, tuple):
        return []
    if origin in (dict, typing.Dict):
        return {}

    # 기본형
    if tp in (str,):
        return "sample"
    if tp in (int,):
        return 1
    if tp in (float,):
        return 1.0
    if tp in (bool,):
        return True
    if tp in (datetime,):
        return datetime(2025, 1, 1, 0, 0, 0)
    if tp in (date,):
        return date(2025, 1, 1)

    # 열거형
    try:
        if isinstance(tp, type) and issubclass(tp, Enum):
            return _first_enum_member(tp)
    except Exception:
        pass

    # Pydantic 모델
    try:
        if isinstance(tp, type) and issubclass(tp, BaseModel):
            return build_sample_model(tp)
    except Exception:
        pass

    # Dict로 fallback
    return {}

def build_sample_model(model_cls: typing.Type[BaseModel], overrides: dict | None = None):
    """
    Pydantic v1/v2 겸용으로, 필수 필드만 자동 채워서 인스턴스를 만듭니다.
    필요하면 overrides로 특정 필드 값을 강제 설정하세요.
    """
    values = {}
    overrides = overrides or {}

    # v2: model_fields / v1: __fields__
    fields = getattr(model_cls, "model_fields", None) or getattr(model_cls, "__fields__", {})

    # v2 필드 접근
    if getattr(model_cls, "model_fields", None):
        for name, finfo in fields.items():
            if name in overrides:
                values[name] = overrides[name]
                continue
            required = finfo.is_required()
            if required:
                anno = finfo.annotation
                values[name] = _sample_for_type(anno)
        return model_cls(**values)

    # v1 필드 접근
    for name, finfo in fields.items():
        if name in overrides:
            values[name] = overrides[name]
            continue
        if finfo.required:
            anno = getattr(finfo, "outer_type_", finfo.type_)
            values[name] = _sample_for_type(anno)
    return model_cls(**values)

def dump_model(instance: BaseModel) -> dict:
    # v2: model_dump / v1: dict
    if hasattr(instance, "model_dump"):
        return instance.model_dump(exclude_unset=True)
    return instance.dict(exclude_unset=True)


# ------------------------ 가짜 서비스(Fake Service) ------------------------

class FakeAccountEntryService:
    def __init__(self):
        # 기존 데이터 2개
        self.entries: dict[str, AccountEntryOut] = {}
        self.links: dict[str, list[tuple[str, RelKind, dict]]] = {}

        e1 = build_sample_model(AccountEntryOut, overrides={"id": "e1"})
        e2 = build_sample_model(AccountEntryOut, overrides={"id": "e2"})
        self.entries["e1"] = e1
        self.entries["e2"] = e2

    # list & count
    def list(self, limit: int, offset: int):
        items = list(self.entries.values())[offset: offset + limit]
        return items

    def count(self) -> int:
        return len(self.entries)

    # CRUD
    def create(self, payload: AccountEntryCreate) -> str:
        new_id = f"e{len(self.entries) + 1}"
        self.entries[new_id] = build_sample_model(AccountEntryOut, overrides={"id": new_id})
        return new_id

    def get(self, entry_id: str):
        return self.entries.get(entry_id)

    def patch(self, entry_id: str, patch: AccountEntryPatch) -> bool:
        # 빈 바디면 업데이트 없음
        data = dump_model(patch)
        if not data:
            return False
        if entry_id not in self.entries:
            return False
        # 실제 변경은 생략 (mock)
        return True

    def delete(self, entry_id: str) -> bool:
        return self.entries.pop(entry_id, None) is not None

    # Graph 탐색
    def get_start_to_end_node(self, start_id: str):
        # 예시 응답
        return {"start": start_id, "leaf_ids": ["leaf-1", "leaf-2"]}

    # Relations
    def link(self, from_id: str, payload: RelationCreate):
        lst = self.links.setdefault(from_id, [])
        lst.append((payload.to_id, payload.kind, payload.props or {}))
        return True

    def list_links(self, entry_id: str):
        # RelationList 인스턴스를 최소 요건으로 생성
        # (구체 스키마를 모르는 경우라도 모델 생성기로 안전하게 생성)
        base = build_sample_model(RelationList)
        return base

    def unlink(self, from_id: str, to_id: str, kind: RelKind) -> int:
        lst = self.links.get(from_id, [])
        before = len(lst)
        lst[:] = [t for t in lst if not (t[0] == to_id and t[1] == kind)]
        after = len(lst)
        return 1 if before != after else 0


# ---------------------------- Pytest 픽스처 ----------------------------

@pytest.fixture()
def app():
    app = FastAPI()
    app.include_router(router)

    fake = FakeAccountEntryService()

    def _override():
        return fake

    # 의존성 오버라이드
    app.dependency_overrides[get_account_entry_service] = _override
    return app

@pytest.fixture()
def client(app: FastAPI):
    return TestClient(app)


# ---------------------------- 테스트들 ----------------------------

def test_list_account_entries_ok(client: TestClient):
    resp = client.get("/account-entries?limit=50&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # e1, e2가 초기 데이터

def test_count_account_entries_ok(client: TestClient):
    resp = client.get("/account-entries/count")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 2

def test_get_account_entry_ok(client: TestClient):
    resp = client.get("/account-entries/e1")
    assert resp.status_code == 200
    assert resp.json()  # 형태 검증은 스키마에 맡김

def test_get_account_entry_404(client: TestClient):
    resp = client.get("/account-entries/does-not-exist")
    assert resp.status_code == 404

def test_create_account_entry_ok(client: TestClient):
    # 요청 바디는 모델을 이용해 자동 생성
    body = dump_model(build_sample_model(AccountEntryCreate))
    resp = client.post("/account-entries", json=body)
    assert resp.status_code == 201
    assert resp.json()

def test_patch_account_entry_ok(client: TestClient):
    # non-empty body => True
    body = dump_model(build_sample_model(AccountEntryPatch))
    # 빈 모델이 생성될 수도 있어 방어적으로 필드 하나 넣기
    if not body:
        body = {"title": "value"}  # 스키마에 없으면 무시될 수 있으니 실제 스키마 필드를 쓰면 더 좋습니다.
    resp = client.patch("/account-entries/e1", json=body)
    # FakeService는 e1 존재 & body 비어있지 않으면 True
    assert resp.status_code == 200

def test_patch_account_entry_400_when_empty(client: TestClient):
    resp = client.patch("/account-entries/e1", json={})
    assert resp.status_code == 400

def test_delete_account_entry_ok(client: TestClient):
    # 먼저 하나 생성
    body = dump_model(build_sample_model(AccountEntryCreate))
    created = client.post("/account-entries", json=body).json()
    entry_id = created.get("id", "e999")  # 스키마에 id가 있다고 가정
    resp = client.delete(f"/account-entries/{entry_id}")
    assert resp.status_code == 204

def test_delete_account_entry_404(client: TestClient):
    resp = client.delete("/account-entries/not-found")
    assert resp.status_code == 404

def test_explore_start_leaf_ok(client: TestClient):
    resp = client.get("/account-entries/e1/explore-start-leaf")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("start") == "e1"
    assert isinstance(data.get("leaf_ids"), list)

def test_create_relation_ok(client: TestClient):
    # RelKind enum의 첫 멤버 사용
    kind_value = list(RelKind)[0].value if hasattr(RelKind, "__members__") else list(RelKind)[0]
    to_id = "e2"
    body = dump_model(build_sample_model(RelationCreate, overrides={"to_id": to_id, "kind": kind_value}))
    # props가 필수면 자동 생성 또는 빈 dict
    body.setdefault("props", {})
    resp = client.post(f"/account-entries/e1/relations", json=body)
    assert resp.status_code == 201
    out = resp.json()
    assert out.get("from_id") == "e1"
    assert out.get("to_id") == to_id

def test_list_relations_ok(client: TestClient):
    resp = client.get("/account-entries/e1/relations")
    assert resp.status_code == 200
    assert resp.json() is not None

def test_delete_relation_404_when_missing(client: TestClient):
    # 존재하지 않는 링크 삭제 시도
    # enum 직렬화 값 확보
    kind_value = list(RelKind)[0].value if hasattr(RelKind, "__members__") else list(RelKind)[0]
    resp = client.delete(f"/account-entries/e1/relations/{kind_value}/nope")
    assert resp.status_code == 404

def test_relation_create_then_delete_ok(client: TestClient):
    # 먼저 relation 생성
    kind_value = list(RelKind)[0].value if hasattr(RelKind, "__members__") else list(RelKind)[0]
    body = dump_model(build_sample_model(RelationCreate, overrides={"to_id": "e2", "kind": kind_value}))
    body.setdefault("props", {})
    c = client.post("/account-entries/e1/relations", json=body)
    assert c.status_code == 201

    # 삭제 시 204
    resp = client.delete(f"/account-entries/e1/relations/{kind_value}/e2")
    assert resp.status_code == 204
