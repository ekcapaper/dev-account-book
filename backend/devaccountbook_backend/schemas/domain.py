
# devaccountbook_backend/schemas/account_entry_models.py
from __future__ import annotations

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

# 이미 프로젝트에 있는 Enum
from devaccountbook_backend.schemas.common_enum import RelKind

# -------------------------------
# Entry (노드) 모델
# -------------------------------
class AccountEntry(BaseModel):
    """DB에서 읽어온 AccountEntry 엔티티(정규화된 최종 형태)."""
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    desc: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    # neo4j.time.DateTime -> datetime (tz-aware, 보통 UTC)
    @field_validator("createdAt", "updatedAt", mode="before")
    @classmethod
    def _coerce_neo4j_datetime(cls, v):
        # None 허용
        if v is None:
            return None
        try:
            # neo4j.time.DateTime 객체면 .to_native()로 변환
            from neo4j.time import DateTime as Neo4jDateTime
            if isinstance(v, Neo4jDateTime):
                return v.to_native()  # timezone-aware datetime(UTC)
        except Exception:
            pass
        return v


class AccountEntryCreate(BaseModel):
    """생성용 DTO (입력)."""
    model_config = ConfigDict(extra="forbid")

    title: str
    desc: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class AccountEntryPatch(BaseModel):
    """부분 수정용 DTO (입력). 기존 ALLOWED_KEYS를 대체합니다."""
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    desc: Optional[str] = None
    tags: Optional[List[str]] = None


# -------------------------------
# Relation(관계) 모델
# -------------------------------
class RelationProps(BaseModel):
    """
    관계에 붙는 추가 속성 컨테이너.
    - 프로젝트가 향후 임의 키를 붙일 수 있으므로 extra='allow'로 둡니다.
      (현재는 note/createdAt/updatedAt 예시만 명시)
    """
    model_config = ConfigDict(extra="allow")

    note: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class RelationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_id: str
    to_id: str
    kind: RelKind
    props: RelationProps = Field(default_factory=RelationProps)


class Relation(BaseModel):
    """단일 관계 레코드."""
    model_config = ConfigDict(extra="forbid")

    from_id: str
    to_id: str
    kind: RelKind
    props: RelationProps = Field(default_factory=RelationProps)

class RelationDelete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    from_id: str
    to_id: str
    kind: RelKind


class NodeRelations(BaseModel):
    """outgoing / incoming 관계 목록 래퍼."""
    model_config = ConfigDict(extra="forbid")

    outgoing: List[Relation]
    incoming: List[Relation]


# -------------------------------
# 트리 모델
# -------------------------------
class AccountEntryTreeNode(BaseModel):
    """
    Entry 트리 노드 (normalize_to_children 결과를 수용).
    children은 동일 타입의 재귀 구조.
    """
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    desc: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    children: List["TreeNode"] = Field(default_factory=list)


# 재귀 모델 선언 마감
AccountEntryTreeNode.model_rebuild()


