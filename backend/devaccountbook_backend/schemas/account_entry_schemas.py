
from typing import Optional, List
from pydantic import BaseModel

class AccountEntryCreate(BaseModel):
    title: str
    desc: Optional[str] = None
    tags: List[str] = []

class AccountEntryPatch(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    tags: Optional[List[str]] = None

class AccountEntryOut(BaseModel):
    id: str
    title: str
    desc: str | None = None
    tags: list[str] = []

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from devaccountbook_backend.schemas.common_enum import RelKind


class RelationCreate(BaseModel):
    to_id: str
    kind: RelKind
    props: Optional[Dict[str, Any]] = None  # 필요 없으면 생략 가능

class RelationOut(BaseModel):
    from_id: str
    to_id: str
    kind: RelKind
    props: Dict[str, Any] = {}

class RelationList(BaseModel):
    outgoing: List[RelationOut] = []
    incoming: List[RelationOut] = []

class CountOut(BaseModel):
    total: int
