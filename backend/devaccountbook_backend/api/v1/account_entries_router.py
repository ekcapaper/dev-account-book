from typing import List

# 서비스 생략 버전: repo를 가져오려면 아래를 사용
# from devaccountbook_backend.repositories.item_repo import ItemRepository
# from devaccountbook_backend.db.neo import get_neo4j_session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Query

from devaccountbook_backend.schemas.account_entry_schemas import (
    AccountEntryCreate, AccountEntryPatch, AccountEntryOut,
    RelationCreate, RelationOut, RelationList, RelKind
)
from devaccountbook_backend.schemas.account_entry_schemas import CountOut, RelationProps
from devaccountbook_backend.services.account_entry_service import (
    AccountEntryService
)
from devaccountbook_backend.services.account_entry_service import get_account_entry_service

router = APIRouter(prefix="/account-entries", tags=["items"])


# 전체
# GET /v1/account-entries?limit=50&offset=0
@router.get("", response_model=List[AccountEntryOut])
def list_account_entries(
        limit: int = Query(50, ge=1, le=200),
        offset: int = Query(0, ge=0),
        service: AccountEntryService = Depends(get_account_entry_service),
):
    account_entry_out_list = service.list(limit=limit, offset=offset)
    return account_entry_out_list


@router.get("/{start_account_entry_id}/explore-start-leaf")
def get_start_to_end_node(start_account_entry_id: str, svc: AccountEntryService = Depends(get_account_entry_service)):
    return svc.get_start_to_end_node(start_account_entry_id)


@router.get("/count", response_model=CountOut)
def count_account_entries(
        service: AccountEntryService = Depends(get_account_entry_service),
):
    return CountOut(total=service.count())


# CRUD
@router.post("", response_model=AccountEntryOut, status_code=status.HTTP_201_CREATED)
def create_account_entry(payload: AccountEntryCreate, svc: AccountEntryService = Depends(get_account_entry_service)):
    new_id = svc.create(payload)
    account_entry_out = svc.get(new_id)
    return account_entry_out


@router.get("/{account_entry_id}", response_model=AccountEntryOut)
def get_account_entry(account_entry_id: str, svc: AccountEntryService = Depends(get_account_entry_service)):
    account_entry_out = svc.get(account_entry_id)
    if not account_entry_out: raise HTTPException(404, "Item not found")
    return account_entry_out


@router.patch("/{account_entry_id}", response_model=AccountEntryOut)
def patch_account_entry(account_entry_id: str, patch: AccountEntryPatch,
                        svc: AccountEntryService = Depends(get_account_entry_service)):
    if not svc.patch(account_entry_id, patch): raise HTTPException(400, "No valid fields to update")
    return svc.get(account_entry_id)


@router.delete("/{account_entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account_entry(account_entry_id: str, svc: AccountEntryService = Depends(get_account_entry_service)):
    if not svc.delete(account_entry_id): raise HTTPException(404, "Item not found")


# 관계 생성: POST /account-entries/{from_id}/relations
@router.post("/{from_id}/relations", status_code=status.HTTP_201_CREATED, response_model=RelationOut)
def create_relation(
        from_id: str,
        payload: RelationCreate,
        service: AccountEntryService = Depends(get_account_entry_service),
):
    service.link(from_id, payload)
    return RelationOut(from_id=from_id, to_id=payload.to_id, kind=payload.kind, props=RelationProps())


# 관계 목록: GET /account-entries/{account_entry_id}/relations
@router.get("/{account_entry_id}/relations", response_model=RelationList)
def list_relations(
        account_entry_id: str,
        service: AccountEntryService = Depends(get_account_entry_service),
):
    relation_list = service.list_links(account_entry_id)
    return relation_list


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
