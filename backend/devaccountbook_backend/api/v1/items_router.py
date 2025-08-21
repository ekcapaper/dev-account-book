from fastapi import APIRouter, Depends, HTTPException, status
from devaccountbook_backend.schemas.item_schemas import ItemCreate, ItemPatch, ItemOut
from devaccountbook_backend.services.item_service import ItemService, get_item_service
# 서비스 생략 버전: repo를 가져오려면 아래를 사용
# from devaccountbook_backend.repositories.item_repo import ItemRepository
# from devaccountbook_backend.db.neo import get_neo4j_session

router = APIRouter(prefix="/items", tags=["items"])

@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, svc: ItemService = Depends(get_item_service)):
    new_id = svc.create(payload)
    data = svc.get(new_id)
    return ItemOut(**data)  # type: ignore[arg-type]

@router.get("/{item_id}", response_model=ItemOut)
def get_item(item_id: str, svc: ItemService = Depends(get_item_service)):
    data = svc.get(item_id)
    if not data: raise HTTPException(404, "Item not found")
    return ItemOut(**data)  # type: ignore[arg-type]

@router.patch("/{item_id}", response_model=ItemOut)
def patch_item(item_id: str, patch: ItemPatch, svc: ItemService = Depends(get_item_service)):
    if not svc.patch(item_id, patch): raise HTTPException(400, "No valid fields to update")
    return ItemOut(**svc.get(item_id))  # type: ignore[arg-type]

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, svc: ItemService = Depends(get_item_service)):
    if not svc.delete(item_id): raise HTTPException(404, "Item not found")
