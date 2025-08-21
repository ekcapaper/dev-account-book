from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.openapi.models import Response
from fastapi.params import Query

from devaccountbook_backend.schemas.account_entry_schemas import AccountEntryCreate, AccountEntryPatch, AccountEntryOut, \
    CountOut
from devaccountbook_backend.services.account_entry_service import AccountEntryService, get_account_entry_service
# 서비스 생략 버전: repo를 가져오려면 아래를 사용
# from devaccountbook_backend.repositories.item_repo import ItemRepository
# from devaccountbook_backend.db.neo import get_neo4j_session
from devaccountbook_backend.schemas.account_entry_schemas import RelationCreate, RelKind
from fastapi import APIRouter, Depends, HTTPException, status
from devaccountbook_backend.schemas.account_entry_schemas import (
    AccountEntryCreate, AccountEntryPatch, AccountEntryOut,
    RelationCreate, RelationOut, RelationList, RelKind
)
from devaccountbook_backend.services.account_entry_service import (
    AccountEntryService
)
router = APIRouter(prefix="/account-entries", tags=["items"])

# 전체
# GET /v1/account-entries?limit=50&offset=0
@router.get("", response_model=List[AccountEntryOut])
def list_account_entries(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: AccountEntryService = Depends(get_account_entry_service),
):
    items = service.list(limit=limit, offset=offset)
    return [AccountEntryOut(**it) for it in items]

@router.get("/count", response_model=CountOut)
def count_account_entries(
    service: AccountEntryService = Depends(get_account_entry_service),
):
    return CountOut(total=service.count())

# CRUD
@router.post("", response_model=AccountEntryOut, status_code=status.HTTP_201_CREATED)
def create_account_entry(payload: AccountEntryCreate, svc: AccountEntryService = Depends(get_account_entry_service)):
    new_id = svc.create(payload)
    data = svc.get(new_id)
    return AccountEntryOut(**data)  # type: ignore[arg-type]

@router.get("/{item_id}", response_model=AccountEntryOut)
def get_account_entry(account_entry_id: str, svc: AccountEntryService = Depends(get_account_entry_service)):
    data = svc.get(account_entry_id)
    if not data: raise HTTPException(404, "Item not found")
    return AccountEntryOut(**data)  # type: ignore[arg-type]

@router.patch("/{item_id}", response_model=AccountEntryOut)
def patch_account_entry(account_entry_id: str, patch: AccountEntryPatch, svc: AccountEntryService = Depends(get_account_entry_service)):
    if not svc.patch(account_entry_id, patch): raise HTTPException(400, "No valid fields to update")
    return AccountEntryOut(**svc.get(account_entry_id))  # type: ignore[arg-type]

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account_entry(account_entry_id: str, svc: AccountEntryService = Depends(get_account_entry_service)):
    if not svc.delete(account_entry_id): raise HTTPException(404, "Item not found")

# 관계 생성: POST /account-entries/{from_id}/relations
@router.post("/{from_id}/relations", status_code=status.HTTP_201_CREATED, response_model=RelationOut)
def create_relation(
    from_id: str,
    payload: RelationCreate,
    service: AccountEntryService = Depends(get_account_entry_service),
):
    kind = service.link(from_id, payload)
    return RelationOut(from_id=from_id, to_id=payload.to_id, kind=kind, props=payload.props or {})

# 관계 목록: GET /account-entries/{account_entry_id}/relations
@router.get("/{account_entry_id}/relations", response_model=RelationList)
def list_relations(
    account_entry_id: str,
    service: AccountEntryService = Depends(get_account_entry_service),
):
    rels = service.list_links(account_entry_id)
    return RelationList(
        outgoing=[RelationOut(**r) for r in rels["outgoing"]],
        incoming=[RelationOut(**r) for r in rels["incoming"]],
    )

# 관계 삭제: DELETE /account-entries/{from_id}/relations/{kind}/{to_id}
@router.delete("/{from_id}/relations/{kind}/{to_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation(
    from_id: str,
    kind: RelKind,
    to_id: str,
    service: AccountEntryService = Depends(get_account_entry_service),
):
    cnt = service.unlink(from_id, to_id, kind)
    if cnt == 0:
        raise HTTPException(404, "Relation not found")