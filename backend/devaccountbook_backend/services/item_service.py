from typing import Dict, Any
from fastapi import Depends
from devaccountbook_backend.db.neo import get_neo4j_session
from devaccountbook_backend.schemas.item_schemas import ItemCreate, ItemPatch
from devaccountbook_backend.repositories.item_repo import ItemRepository

class ItemService:
    def __init__(self, repo: ItemRepository) -> None:
        self.repo = repo
        self.repo.bootstrap()

    def create(self, p: ItemCreate) -> str: return self.repo.create(p.title, p.desc, p.tags)
    def get(self, item_id: str) -> Dict[str, Any] | None: return self.repo.get(item_id)
    def patch(self, item_id: str, p: ItemPatch) -> bool: return self.repo.patch(item_id, p.model_dump(exclude_none=True))
    def delete(self, item_id: str) -> bool: return self.repo.delete(item_id)

def get_item_service(session = Depends(get_neo4j_session)) -> ItemService:
    return ItemService(ItemRepository(session))
