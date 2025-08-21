from neo4j import GraphDatabase, basic_auth, Driver
from typing import Optional

driver = None  # type: Optional[Driver]

def init_driver(uri: str, user: str, password: str):
    global driver
    driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))

def close_driver():
    global driver
    if driver:
        driver.close()
        driver = None
