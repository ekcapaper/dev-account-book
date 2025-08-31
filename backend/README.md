## dev-accountbook-backend

```
pyinstaller --onefile --name devab `
  --add-data "devaccountbook_backend\static;devaccountbook_backend/static" `
  --hidden-import anyio --hidden-import sniffio --hidden-import pydantic_core `
  --exclude-module uvloop --exclude-module watchfiles `
  run_server.py
'''