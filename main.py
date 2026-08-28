import os

import uvicorn

from core.openapi import setup_openapi
from middleware.addClientIP import ClientIPMiddleware

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.router import router

app = FastAPI(
    title="BlogAPI",
    version="1.0",
)

app.mount("/media", StaticFiles(directory="media"), name="media")

app.add_middleware(ClientIPMiddleware)


@app.get("/")
def hello():
    return {"message": "FastAPI + Django"}


setup_openapi(app)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)