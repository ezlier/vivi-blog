from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def _to_binary_format(node):
    """
    递归将：

        contentMediaType: application/octet-stream

    转换为 Swagger UI 更兼容的：

        format: binary
    """
    if isinstance(node, dict):
        if node.get("contentMediaType") == "application/octet-stream":
            node.pop("contentMediaType", None)
            node["format"] = "binary"

        for value in node.values():
            _to_binary_format(value)

    elif isinstance(node, list):
        for item in node:
            _to_binary_format(item)


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    _to_binary_format(schema)

    app.openapi_schema = schema

    return schema


def setup_openapi(app: FastAPI):
    """
    配置自定义 OpenAPI 生成器。
    """
    app.openapi = lambda: custom_openapi(app)