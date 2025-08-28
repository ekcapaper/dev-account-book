from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field

from devaccountbook_backend.schemas.common_enum import RelKind


class AccountEntryNodeCreateDTO(BaseModel):
    """생성용 DTO (입력)."""
    model_config = ConfigDict(extra="forbid")

    title: str
    desc: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class AccountEntryNodePatchDTO(BaseModel):
    """부분 수정용 DTO (입력). 기존 ALLOWED_KEYS를 대체합니다."""
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    desc: Optional[str] = None
    tags: Optional[List[str]] = None


class AccountEntryRelationPropsDTO(BaseModel):
    """
    관계에 붙는 추가 속성 컨테이너.
    - 프로젝트가 향후 임의 키를 붙일 수 있으므로 extra='allow'로 둡니다.
      (현재는 note/createdAt/updatedAt 예시만 명시)
    """
    model_config = ConfigDict(extra="allow")

    note: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class AccountEntryRelationCreateDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_id: str
    to_id: str
    kind: RelKind
    props: AccountEntryRelationPropsDTO = Field(default_factory=AccountEntryRelationPropsDTO)


class AccountEntryRelationDTO(BaseModel):
    """단일 관계 레코드."""
    model_config = ConfigDict(extra="forbid")

    from_id: str
    to_id: str
    kind: RelKind
    props: AccountEntryRelationPropsDTO = Field(default_factory=AccountEntryRelationPropsDTO)


class AccountEntryRelationDeleteDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    from_id: str
    to_id: str
    kind: RelKind


class AccountEntryRelationsDTO(BaseModel):
    """outgoing / incoming 관계 목록 래퍼."""
    model_config = ConfigDict(extra="forbid")

    outgoing: List[AccountEntryRelationDTO]
    incoming: List[AccountEntryRelationDTO]


class AccountEntryTreeNodeDTO(BaseModel):
    """
    Entry 트리 노드 (normalize_to_children 결과를 수용).
    children은 동일 타입의 재귀 구조.
    """
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    desc: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    children: List["AccountEntryTreeNodeDTO"] = Field(default_factory=list)

AccountEntryTreeNodeDTO.model_rebuild()

def convert_account_entry_tree_node(input_data: dict):
    print(type(input_data))
    id_data = input_data.get("id")
    title = input_data.get("title")
    desc = input_data.get("desc")
    tags = input_data.get("tags") or []
    children = []
    if "relates_to" in input_data.keys():
        for child in input_data["relates_to"]:
            children.append(convert_account_entry_tree_node(child))
    return (
        AccountEntryTreeNodeDTO(
            id=id_data,
            title=title,
            desc=desc,
            tags=tags,
            children=children,
        )
    )
