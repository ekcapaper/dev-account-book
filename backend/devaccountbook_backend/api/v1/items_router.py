from fastapi import APIRouter, Depends, HTTPException, status
from devaccountbook_backend.schemas.account_entry_schemas import AccountEntryCreate, AccountEntryPatch, AccountEntryOut
from devaccountbook_backend.services.account_entry_service import AccountEntryService, get_item_service
# 서비스 생략 버전: repo를 가져오려면 아래를 사용
# from devaccountbook_backend.repositories.item_repo import ItemRepository
# from devaccountbook_backend.db.neo import get_neo4j_session

router = APIRouter(prefix="/items", tags=["items"])

@router.post("", response_model=AccountEntryOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: AccountEntryCreate, svc: AccountEntryService = Depends(get_item_service)):
    new_id = svc.create(payload)
    data = svc.get(new_id)
    return AccountEntryOut(**data)  # type: ignore[arg-type]

@router.get("/{item_id}", response_model=AccountEntryOut)
def get_item(account_entry_id: str, svc: AccountEntryService = Depends(get_item_service)):
    data = svc.get(account_entry_id)
    if not data: raise HTTPException(404, "Item not found")
    return AccountEntryOut(**data)  # type: ignore[arg-type]

@router.patch("/{item_id}", response_model=AccountEntryOut)
def patch_item(account_entry_id: str, patch: AccountEntryPatch, svc: AccountEntryService = Depends(get_item_service)):
    if not svc.patch(account_entry_id, patch): raise HTTPException(400, "No valid fields to update")
    return AccountEntryOut(**svc.get(account_entry_id))  # type: ignore[arg-type]

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(account_entry_id: str, svc: AccountEntryService = Depends(get_item_service)):
    if not svc.delete(account_entry_id): raise HTTPException(404, "Item not found")
