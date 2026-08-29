from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实 IP。

    优先使用 Cloudflare 提供的 CF-Connecting-IP，
    但前提是你的服务只允许可信的 Cloudflare / Nginx 代理访问。
    """

    cf_ip = request.headers.get("CF-Connecting-IP")

    if cf_ip:
        return cf_ip

    if request.client:
        return request.client.host

    return "0.0.0.0"
