import uuid
from typing import Optional, Dict, Any
from neo4j import Session

import re
from typing import Dict, Any, List
from neo4j import Session

from devaccountbook_backend.repositories.normalize_neo import normalize_neo
from devaccountbook_backend.schemas.account_entry_schemas import RelKind

ALLOWED_KEYS = {"title", "desc", "tags"}

class AccountEntryRepository:
    def __init__(self, session: Session):
        self.s = session

    def bootstrap(self) -> None:
        q = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AccountEntry) REQUIRE n.id IS UNIQUE"
        self.s.execute_write(lambda tx: tx.run(q))
    
    # 집계 함수
    def list_all(self, *, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        q = """
        MATCH (n:AccountEntry)
        RETURN n
        ORDER BY coalesce(n.createdAt, datetime({epochSeconds:0})) DESC
        SKIP $offset
        LIMIT $limit
        """
        rows = self.s.execute_read(lambda tx: list(tx.run(q, offset=offset, limit=limit)))
        return [normalize_neo(dict(row["n"])) for row in rows]

    def count_all(self) -> int:
        q = "MATCH (n:AccountEntry) RETURN count(n) AS cnt"
        rec = self.s.execute_read(lambda tx: tx.run(q).single())
        return int(rec["cnt"])

    def create(self, title: str, desc: Optional[str], tags: list[str]) -> str:
        nid = str(uuid.uuid4())
        q = """
        CREATE (n:AccountEntry {id:$id, title:$title, desc:$desc, tags:$tags, createdAt:datetime()})
        RETURN n.id AS id
        """
        rec = self.s.execute_write(lambda tx: tx.run(q, id=nid, title=title, desc=desc, tags=tags).single())
        return rec["id"]

    def get(self, account_entry_id: str) -> Dict[str, Any] | None:
        q = "MATCH (n:AccountEntry {id:$id}) RETURN n"
        rec = self.s.execute_read(lambda tx: tx.run(q, id=account_entry_id).single())
        return normalize_neo(dict(rec["n"])) if rec else None

    def patch(self, account_entry_id: str, props: Dict[str, Any]) -> bool:
        safe = {k: v for k, v in props.items() if k in ALLOWED_KEYS and v is not None}
        if not safe:
            return False
        q = """
        MATCH (n:AccountEntry {id:$id})
        SET n += $props, n.updatedAt = datetime()
        RETURN n.id AS id
        """
        rec = self.s.execute_write(lambda tx: tx.run(q, id=account_entry_id, props=safe).single())
        return rec is not None

    def delete(self, account_entry_id: str) -> bool:
        print(account_entry_id)
        q = "MATCH (n:AccountEntry {id:$id}) DETACH DELETE n"
        rec = self.s.execute_write(lambda tx: tx.run(q, id=account_entry_id).single())
        return rec is not None

    # --- 관계 생성 ---
    def create_relation(
            self, from_id: str, to_id: str, kind: RelKind, props: Dict[str, Any] | None = None
    ) -> str:
        # 관계 타입은 파라미터 바인딩 불가 → Enum 기반 f-string 삽입(화이트리스트)
        q = f"""
        MATCH (a:AccountEntry {{id:$from_id}}), (b:AccountEntry {{id:$to_id}})
        MERGE (a)-[r:{kind.value}]->(b)
        ON CREATE SET r.createdAt = datetime()
        SET r += $props
        RETURN type(r) AS kind
        """
        rec = self.s.execute_write(lambda tx: tx.run(
            q, from_id=from_id, to_id=to_id, props=props or {}
        ).single())
        return rec["kind"]

    # --- 관계 목록 조회 (outgoing / incoming) ---
    def list_relations(self, entry_id: str) -> Dict[str, List[Dict[str, Any]]]:
        q_out = """
        MATCH (a:AccountEntry {id:$id})-[r]->(b:AccountEntry)
        RETURN type(r) AS kind, a.id AS from_id, b.id AS to_id, properties(r) AS props
        ORDER BY kind, to_id
        """
        q_in = """
        MATCH (a:AccountEntry)-[r]->(b:AccountEntry {id:$id})
        RETURN type(r) AS kind, a.id AS from_id, b.id AS to_id, properties(r) AS props
        ORDER BY kind, from_id
        """
        rows_out = self.s.execute_read(lambda tx: list(tx.run(q_out, id=entry_id)))
        rows_in = self.s.execute_read(lambda tx: list(tx.run(q_in, id=entry_id)))

        to_dicts = lambda rows: [
            {
                "kind": row["kind"],
                "from_id": row["from_id"],
                "to_id": row["to_id"],
                "props": normalize_neo(row["props"] or {})
            }
            for row in rows
        ]
        return {"outgoing": to_dicts(rows_out), "incoming": to_dicts(rows_in)}

    # --- 관계 삭제 ---
    def delete_relation(self, from_id: str, to_id: str, kind: RelKind) -> int:
        q = f"""
        MATCH (a:AccountEntry {{id:$from_id}})-[r:{kind.value}]->(b:AccountEntry {{id:$to_id}})
        DELETE r
        RETURN count(*) AS cnt
        """
        rec = self.s.execute_write(lambda tx: tx.run(
            q, from_id=from_id, to_id=to_id
        ).single())
        return rec["cnt"]


# Depends 팩토리
from fastapi import Depends
from devaccountbook_backend.db.neo import get_neo4j_session

def get_item_repo(session: Session = Depends(get_neo4j_session)) -> AccountEntryRepository:
    repo = AccountEntryRepository(session)
    return repo
