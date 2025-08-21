from typing import Dict, Any
from fastapi import Depends
from devaccountbook_backend.db.neo import get_neo4j_session
from devaccountbook_backend.schemas.account_entry_schemas import AccountEntryCreate, AccountEntryPatch
from devaccountbook_backend.repositories.account_entry_repo import AccountEntryRepository

class AccountEntryService:
    def __init__(self, repo: AccountEntryRepository) -> None:
        self.repo = repo
        self.repo.bootstrap()

    def create(self, p: AccountEntryCreate) -> str: return self.repo.create(p.title, p.desc, p.tags)
    def get(self, account_entry_id: str) -> Dict[str, Any] | None: return self.repo.get(account_entry_id)
    def patch(self, account_entry_id: str, p: AccountEntryPatch) -> bool: return self.repo.patch(account_entry_id, p.model_dump(exclude_none=True))
    def delete(self, account_entry_id: str) -> bool: return self.repo.delete(account_entry_id)

def get_item_service(session = Depends(get_neo4j_session)) -> AccountEntryService:
    return AccountEntryService(AccountEntryRepository(session))
