from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "neo4jneo4j")
    cors_origins: list[str] = [o for o in os.getenv("API_CORS_ORIGINS", "").split(",") if o] or ["*"]

settings = Settings()
