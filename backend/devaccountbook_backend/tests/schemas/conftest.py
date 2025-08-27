# tests/conftest.py
from typing import Any, Generator

import pytest
from neo4j import Session

from devaccountbook_backend.db.driver import init_driver
from devaccountbook_backend.core.config import settings
from devaccountbook_backend.db.neo import get_neo4j_session
from devaccountbook_backend.repositories.account_entry_repo import AccountEntryRepository

@pytest.fixture(scope="session")
def neo4j_session() -> Generator[Session, None, None]:
    init_driver(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    """
    실제 테스트용 Neo4j Session.
    - devaccountbook_backend.db.neo.get_neo4j_session 을 그대로 사용
    - 테스트 세션은 세션 종료 시 close 시도
    """
    gen = get_neo4j_session()  # generator 객체
    session = next(gen)  # yield된 실제 Session
    try:
        yield session
    finally:
        # generator의 종료 부분 실행 (with driver.session() 빠지면서 close)
        try:
            next(gen)
        except StopIteration:
            pass

@pytest.fixture(autouse=True)
def _cleanup_db(neo4j_session: Session):
    """
    각 테스트 전/후로 DB 깨끗하게 비우기.
    """
    neo4j_session.run("MATCH (n) DETACH DELETE n")
    yield
    neo4j_session.run("MATCH (n) DETACH DELETE n")

@pytest.fixture
def repo(neo4j_session: Session) -> AccountEntryRepository:
    """
    실제 세션으로 Repo 구성 + 제약 조건 부트스트랩.
    """
    r = AccountEntryRepository(neo4j_session)
    r.bootstrap()
    return r

@pytest.fixture
def has_apoc(neo4j_session: Session) -> bool:
    """
    APOC 설치 여부 확인 (apoc.paths.toJsonTree 존재 여부).
    """
    try:
        q = """
        CALL dbms.procedures() YIELD name
        WITH name WHERE name = 'apoc.paths.toJsonTree'
        RETURN count(*) AS cnt
        """
        rec = neo4j_session.run(q).single()
        return rec and rec["cnt"] > 0
    except Exception:
        return False
