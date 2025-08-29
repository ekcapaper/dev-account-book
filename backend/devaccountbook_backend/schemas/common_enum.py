from enum import Enum


class RelKind(str, Enum):
    RELATES_TO = "RELATES_TO"
    INFLUENCES = "INFLUENCES"
    BLOCKS = "BLOCKS"
    DUPLICATES = "DUPLICATES"
