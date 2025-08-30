from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from devaccountbook_backend.schemas.common_schema import CamelModel


class AccountEntryCreate(CamelModel):
    title: str
    desc: Optional[str] = None
    tags: List[str] = []


class AccountEntryPatch(CamelModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    tags: Optional[List[str]] = None


class AccountEntryOut(CamelModel):
    id: str
    title: str
    desc: str | None = None
    tags: list[str] = []


from typing import Optional, List
from pydantic import BaseModel
from devaccountbook_backend.schemas.common_enum import RelKind


class RelationProps(CamelModel):
    """
    관계에 붙는 추가 속성 컨테이너.
    - 프로젝트가 향후 임의 키를 붙일 수 있으므로 extra='allow'로 둡니다.
      (현재는 note/createdAt/updatedAt 예시만 명시)
    """
    model_config = ConfigDict(extra="allow")

    note: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class RelationCreate(CamelModel):
    to_id: str
    kind: RelKind
    props: Optional[RelationProps] = None  # 필요 없으면 생략 가능


class RelationOut(CamelModel):
    from_id: str
    to_id: str
    kind: RelKind
    props: RelationProps = Field(default_factory=RelationProps)


class RelationList(CamelModel):
    outgoing: List[RelationOut] = Field(default_factory=list)
    incoming: List[RelationOut] = Field(default_factory=list)


class CountOut(CamelModel):
    total: int
