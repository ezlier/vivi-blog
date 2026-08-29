from django.conf import settings
from django.db import models


class VisitorLog(models.Model):
    """
    访客访问记录
    """

    ip_address = models.GenericIPAddressField(protocol="both", unpack_ipv4=True, db_index=True, verbose_name="IP地址", )
    user_agent = models.TextField(blank=True, verbose_name="User-Agent", )
    device_type = models.CharField(max_length=20, blank=True, verbose_name="设备类型", )
    visited_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="访问时间", )

    class Meta:
        db_table = "visitor_logs"
        ordering = ["-visited_at", ]
        indexes = [
            models.Index(
                fields=[
                    "ip_address",
                    "-visited_at",
                ],
                name="idx_visitor_ip_time",
            ),
        ]

        verbose_name = "访客记录"
        verbose_name_plural = "访客记录"

    def __str__(self):
        return f"{self.ip_address} - {self.visited_at}"


class IPBlacklist(models.Model):
    """
    IP 黑名单
    """

    ip_address = models.GenericIPAddressField(protocol="both", unpack_ipv4=True, unique=True, verbose_name="IP地址", )
    reason = models.CharField(max_length=255, blank=True, verbose_name="封禁原因", )
    is_active = models.BooleanField(default=True, verbose_name="是否启用", )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_ip_blacklists",
        verbose_name="创建人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", )
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="过期时间", )

    class Meta:
        db_table = "ip_blacklist"
        ordering = ["-created_at", ]
        verbose_name = "IP黑名单"
        verbose_name_plural = "IP黑名单"

    def __str__(self):
        return self.ip_address
