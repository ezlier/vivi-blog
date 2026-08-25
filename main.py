import os
from pathlib import Path

from middleware.addClientIP import ClientIPMiddleware

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

import django

django.setup()

from django.conf import settings
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.router import router

app = FastAPI(
    title="BlogAPI",
    version="1.0",
)

# 确保媒体目录存在，并挂载静态文件服务供封面访问
Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")

app.add_middleware(ClientIPMiddleware)


@app.get("/")
def hello():
    return {"message": "FastAPI + Django"}


app.include_router(router)
