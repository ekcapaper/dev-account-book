
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
