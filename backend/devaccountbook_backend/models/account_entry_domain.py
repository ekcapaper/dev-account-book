
# devaccountbook_backend/schemas/account_entry_domain.py
from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator

from devaccountbook_backend.dtos.account_entry_dto import AccountEntryTreeNodeDTO


# 이미 프로젝트에 있는 Enum

# -------------------------------
# Entry (노드) 모델
# -------------------------------
class AccountEntryNode(BaseModel):
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






