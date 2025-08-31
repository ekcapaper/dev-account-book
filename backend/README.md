## dev-accountbook-backend

```
docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    neo4j
```

```
pyinstaller --onefile --name devab `
  --add-data "devaccountbook_backend\static;devaccountbook_backend/static" `
  --hidden-import anyio --hidden-import sniffio --hidden-import pydantic_core `
  --exclude-module uvloop --exclude-module watchfiles `
  run_server.py
'''