import uuid
from typing import Optional, Dict, Any
from neo4j import Session

import re
from typing import Dict, Any, List
from neo4j import Session

from devaccountbook_backend.repositories.normalize_neo import normalize_neo
from devaccountbook_backend.schemas.account_entry_schemas import RelKind
from devaccountbook_backend.schemas.domain import AccountEntry, AccountEntryCreate, AccountEntryPatch, RelationCreate, \
    RelationProps, NodeRelations, Relation, RelationDelete, AccountEntryTreeNode
from devaccountbook_backend.utils.normalize_antd import normalize_to_children

ALLOWED_KEYS = {"title", "desc", "tags"}

# temp code


class AccountEntryRepository:
    def __init__(self, session: Session):
        self.s = session

    def _ensure_constraints(self) -> None:
        q = "CREATE CONSTRAINT IF NOT EXISTS FOR (n:AccountEntry) REQUIRE n.id IS UNIQUE"
        self.s.execute_write(lambda tx: tx.run(q))

    def bootstrap(self) -> None:
        self._ensure_constraints()

    #  집계 함수
    def get_entries(self, *, limit: int = 50, offset: int = 0) -> List[AccountEntry]:
        q = """
        MATCH (n:AccountEntry)
        RETURN n
        ORDER BY coalesce(n.createdAt, datetime({epochSeconds:0})) DESC
        SKIP $offset
        LIMIT $limit
        """
        rows = self.s.execute_read(lambda tx: list(tx.run(q, offset=offset, limit=limit)))
        return [AccountEntry.model_validate(dict(row["n"])) for row in rows]

    def count_entries(self) -> int:
        q = "MATCH (n:AccountEntry) RETURN count(n) AS cnt"
        rec = self.s.execute_read(lambda tx: tx.run(q).single())
        return int(rec["cnt"])

    # CRUD
    def create_entry(self, account_entry_create: AccountEntryCreate) -> str:
        nid = str(uuid.uuid4())
        q = """
        CREATE (n:AccountEntry {id:$id, title:$title, desc:$desc, tags:$tags, createdAt:datetime()})
        RETURN n.id AS id
        """
        rec = self.s.execute_write(lambda tx: tx.run(
            q,
            id=nid,
            title=account_entry_create.title,
            desc=account_entry_create.desc,
            tags=account_entry_create.tags
        ).single())
        return rec["id"]

    def get_entry(self, account_entry_id: str) ->  AccountEntry | None:
        q = "MATCH (n:AccountEntry {id:$id}) RETURN n"
        rec = self.s.execute_read(lambda tx: tx.run(q, id=account_entry_id).single())
        if rec is None:
            return None
        else:
            node = rec["n"]
            entry = AccountEntry.model_validate(dict(node))
            return entry

    def update_entry(self, account_entry_id: str, account_entry_patch: AccountEntryPatch) -> bool:
        props = account_entry_patch.model_dump(exclude_unset=True, exclude_none=True)
        if len(props.keys()) == 0:
            return False
        q = """
        MATCH (n:AccountEntry {id:$id})
        SET n += $props, n.updatedAt = datetime()
        RETURN n.id AS id
        """
        rec = self.s.execute_write(lambda tx: tx.run(q, id=account_entry_id, props=props).single())
        return rec is not None

    def delete_entry(self, account_entry_id: str) -> bool:
        q = "MATCH (n:AccountEntry {id:$id}) DETACH DELETE n"
        rec = self.s.execute_write(lambda tx: tx.run(q, id=account_entry_id).single())
        return True

    # Relation
    def add_relation(
            self, relation_create: RelationCreate
    ) -> str:
        # 관계 타입은 파라미터 바인딩 불가 → Enum 기반 f-string 삽입(화이트리스트)
        q = f"""
        MATCH (a:AccountEntry {{id:$from_id}}), (b:AccountEntry {{id:$to_id}})
        MERGE (a)-[r:{relation_create.kind.value}]->(b)
        ON CREATE SET r.createdAt = datetime()
        SET r += $props
        RETURN type(r) AS kind
        """
        rec = self.s.execute_write(lambda tx: tx.run(
            q, from_id=relation_create.from_id, to_id=relation_create.to_id, props=RelationProps.model_dump(relation_create.props) or {}
        ).single())
        return rec["kind"]

    # --- 관계 목록 조회 (outgoing / incoming) ---
    def get_relations(self, entry_id: str) -> NodeRelations:
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

        to_relation = lambda rows: [
            Relation.model_validate({
                "kind": row["kind"],
                "from_id": row["from_id"],
                "to_id": row["to_id"],
                "props": normalize_neo(row["props"] or {})
            })
            for row in rows
        ]
        return NodeRelations.model_validate({"outgoing": to_relation(rows_out), "incoming": to_relation(rows_in)})

    # --- 관계 삭제 ---
    def delete_relation(self, relation_delete:RelationDelete) -> int:
        q = f"""
        MATCH (a:AccountEntry {{id:$from_id}})-[r:{relation_delete.kind.value}]->(b:AccountEntry {{id:$to_id}})
        DELETE r
        RETURN count(*) AS cnt
        """
        rec = self.s.execute_write(lambda tx: tx.run(
            q, from_id=relation_delete.from_id, to_id=relation_delete.to_id
        ).single())
        return rec["cnt"]

    # Function
    def get_entry_tree(self, start_id) -> AccountEntryTreeNode:
        q = Q_TREE = """
        MATCH p = (root:AccountEntry {id:$id})-[:RELATES_TO*1..]->(n:AccountEntry)
        WITH collect(p) AS paths
        CALL apoc.paths.toJsonTree(paths) YIELD value
        RETURN value
        """
        rec = self.s.execute_read(lambda tx: tx.run(Q_TREE, id=start_id).single())
        print(rec["value"])
        print(type(rec["value"]))
        return normalize_to_children(rec["value"]) if rec else None


# Depends 팩토리
from fastapi import Depends
from devaccountbook_backend.db.neo import get_neo4j_session

def get_item_repo(session: Session = Depends(get_neo4j_session)) -> AccountEntryRepository:
    repo = AccountEntryRepository(session)
    return repo
