from typing import Generator
from .driver import driver

def get_neo4j_session() -> Generator:
    # 요청 단위 세션 (자동 close)
    with driver.session() as session:   # type: ignore[attr-defined]
        yield session
