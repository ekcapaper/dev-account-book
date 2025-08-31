# dev-accountbook-backend

## Neo4j 실행 (Docker 사용)
```
docker run \
  --publish=7474:7474 --publish=7687:7687 \
  --volume=$HOME/neo4j/data:/data \
  neo4j
```

Neo4j를 도커 컨테이너로 실행합니다.

웹 브라우저: http://localhost:7474

Bolt 드라이버: bolt://localhost:7687

## 실행 파일 빌드 (PyInstaller)
```
pyinstaller --onefile --name devab `
  --add-data "devaccountbook_backend\static;devaccountbook_backend/static" `
  --hidden-import anyio --hidden-import sniffio --hidden-import pydantic_core `
  --exclude-module uvloop --exclude-module watchfiles `
  run_server.py
```

Windows에서는 dist/devab.exe가 생성됩니다.

Linux/macOS에서는 dist/devab가 생성됩니다.

## 환경 설정 (.env 파일)

main.py 또는 run_server.exe와 동일한 경로에 .env 파일을 생성하고, Neo4j 접속 정보를 작성합니다:
```
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4jneo4j
```

## 사용 방법

1. Neo4j 설치 또는 Docker를 이용해 Neo4j 실행
2. .env 파일에 Neo4j 사용자명(ID)과 비밀번호 정의
3. 프로그램 실행

### 개발 환경에서 직접 실행
```
python run_server.py
```
```
uvicorn devaccountbook_backend.main:app --host 127.0.0.1 --port 8000
```

### 패키징된 실행 파일 실행
```
./dist/devab.exe   # Windows
./dist/devab       # Linux/macOS
```
