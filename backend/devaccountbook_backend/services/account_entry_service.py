from typing import Dict, Any
from fastapi import Depends
from devaccountbook_backend.db.neo import get_neo4j_session
from devaccountbook_backend.schemas.account_entry_schemas import AccountEntryCreate, AccountEntryPatch, RelationCreate, RelKind
from devaccountbook_backend.repositories.account_entry_repo import AccountEntryRepository

class AccountEntryService:
    def __init__(self, repo: AccountEntryRepository) -> None:
        self.repo = repo
        self.repo.bootstrap()

    # 전체
    def list(self, *, limit: int = 50, offset: int = 0) -> list[dict]:
        items = self.repo.list_all(limit=limit, offset=offset)
        return items

    def count(self) -> int:
        return self.repo.count_all()

    # CRUD
    def create(self, p: AccountEntryCreate) -> str: return self.repo.create(p.title, p.desc, p.tags)
    def get(self, account_entry_id: str) -> Dict[str, Any] | None: return self.repo.get(account_entry_id)
    def patch(self, account_entry_id: str, p: AccountEntryPatch) -> bool: return self.repo.patch(account_entry_id, p.model_dump(exclude_none=True))
    def delete(self, account_entry_id: str) -> bool: return self.repo.delete(account_entry_id)

    # 관계 생성 (from_id -> to_id)
    def link(self, from_id: str, payload: RelationCreate) -> str:
        return self.repo.create_relation(
            from_id=from_id,
            to_id=payload.to_id,
            kind=payload.kind,
            props=payload.props or {}
        )

    # 관계 목록 조회 (in/out 분리)
    def list_links(self, entry_id: str) -> Dict[str, Any]:
        return self.repo.list_relations(entry_id)

    # 관계 삭제
    def unlink(self, from_id: str, to_id: str, kind: RelKind) -> int:
        return self.repo.delete_relation(from_id, to_id, kind)

    # 처음부터 끝까지 조회
    def get_start_to_end_node(self, start_id):
        return self.repo.get_start_to_end_node(start_id)



def get_account_entry_service(session = Depends(get_neo4j_session)) -> AccountEntryService:
    return AccountEntryService(AccountEntryRepository(session))
