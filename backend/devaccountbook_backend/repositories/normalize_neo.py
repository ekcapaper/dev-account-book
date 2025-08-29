# repositories/_normalize.py (새 파일로 두거나 repo 안에 함수로)
from neo4j.time import DateTime as NeoDateTime, Date as NeoDate, Time as NeoTime, Duration as NeoDuration


def normalize_neo(v):
    # Neo4j temporal → Python 표준 타입
    if isinstance(v, (NeoDateTime, NeoDate, NeoTime, NeoDuration)):
        return v.to_native()
    if isinstance(v, list):
        return [normalize_neo(x) for x in v]
    if isinstance(v, dict):
        return {k: normalize_neo(x) for k, x in v.items()}
    return v
