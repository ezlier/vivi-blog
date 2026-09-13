import os
import uvicorn
from core.openapi import setup_openapi
from core.db import db_connection

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()

from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from api.router import router
from middleware.addClientIP import ClientIPMiddleware
from middleware.blackList import visitor_blacklist_middleware

docs_enabled = (os.getenv("DJANGO_DEBUG", "False", ).lower() == "true")

app = FastAPI(
    title="BlogAPI",
    version="1.0",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
    dependencies=[Depends(db_connection)],
)

app.mount("/media", StaticFiles(directory="media"), name="media")

app.add_middleware(ClientIPMiddleware)
app.middleware("http")(visitor_blacklist_middleware)


@app.get("/")
def hello():
    return {"message": "FastAPI + Django"}


setup_openapi(app)

app.include_router(router)

# if __name__ == '__main__':
#     uvicorn.run("main:app", host="0.0.0.0", port=8000)