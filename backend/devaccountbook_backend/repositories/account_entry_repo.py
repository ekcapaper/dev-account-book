import uuid
from typing import Optional, Dict, Any
from neo4j import Session

ALLOWED_KEYS = {"title", "desc", "tags"}

class AccountEntryRepository:
    def __init__(self, session: Session):
        self.s = session

    def bootstrap(self) -> None:
        q = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Item) REQUIRE n.id IS UNIQUE"
        self.s.execute_write(lambda tx: tx.run(q))

    def create(self, title: str, desc: Optional[str], tags: list[str]) -> str:
        nid = str(uuid.uuid4())
        q = """
        CREATE (n:Item {id:$id, title:$title, desc:$desc, tags:$tags, createdAt:datetime()})
        RETURN n.id AS id
        """
        rec = self.s.execute_write(lambda tx: tx.run(q, id=nid, title=title, desc=desc, tags=tags).single())
        return rec["id"]

    def get(self, item_id: str) -> Dict[str, Any] | None:
        q = "MATCH (n:Item {id:$id}) RETURN n"
        rec = self.s.execute_read(lambda tx: tx.run(q, id=item_id).single())
        return dict(rec["n"]) if rec else None

    def patch(self, item_id: str, props: Dict[str, Any]) -> bool:
        safe = {k: v for k, v in props.items() if k in ALLOWED_KEYS and v is not None}
        if not safe:
            return False
        q = """
        MATCH (n:Item {id:$id})
        SET n += $props, n.updatedAt = datetime()
        RETURN n.id AS id
        """
        rec = self.s.execute_write(lambda tx: tx.run(q, id=item_id, props=safe).single())
        return rec is not None

    def delete(self, item_id: str) -> bool:
        q = "MATCH (n:Item {id:$id}) DETACH DELETE n RETURN 1 AS ok"
        rec = self.s.execute_write(lambda tx: tx.run(q, id=item_id).single())
        return rec is not None

# Depends 팩토리
from fastapi import Depends
from devaccountbook_backend.db.neo import get_neo4j_session

def get_item_repo(session: Session = Depends(get_neo4j_session)) -> AccountEntryRepository:
    repo = AccountEntryRepository(session)
    return repo
