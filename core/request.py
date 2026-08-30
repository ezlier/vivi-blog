import ipaddress

from django.conf import settings
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实 IP。

    只有明确配置 TRUST_PROXY_HEADERS=True 时才读取代理头。
    开启前必须确保应用只能通过可信的 Cloudflare / Nginx 代理访问，
    否则客户端可以伪造请求头绕过基于 IP 的限制。
    """

    if getattr(settings, "TRUST_PROXY_HEADERS", False):
        cf_ip = _normalize_ip(request.headers.get("CF-Connecting-IP"))
        if cf_ip:
            return cf_ip

        forwarded_for = request.headers.get("X-Forwarded-For", "")
        forwarded_ip = _normalize_ip(forwarded_for.split(",", 1)[0])
        if forwarded_ip:
            return forwarded_ip

    if request.client:
        return request.client.host

    return "0.0.0.0"


def _normalize_ip(value: str | None) -> str | None:
    if not value:
        return None

    value = value.strip()
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        return None
