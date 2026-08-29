from django.utils import timezone

from .repository import (
    IPBlacklistRepository,
    VisitorRepository,
)


class VisitorService:

    @staticmethod
    def get_logs(page: int, page_size: int, ):

        visitors = list(VisitorRepository.find_recent(
            page=page,
            page_size=page_size,
        ))

        total = VisitorRepository.count()

        return {
            "logs": {
                "items": visitors,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": ((total + page_size - 1)
                                // page_size
                                ),
            }
        }

    @staticmethod
    def record_visitor(
            *,
            ip_address: str,
            user_agent: str,
            device_type: str | None,
    ):
        if not device_type:
            device_type = VisitorService.detect_device(user_agent)

        return VisitorRepository.create(
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
        )

    @staticmethod
    def detect_device(user_agent: str, ) -> str:
        ua = user_agent.lower()
        if "mobile" in ua:
            return "mobile"
        if "tablet" in ua:
            return "tablet"
        return "desktop"

    @staticmethod
    def is_blocked(ip_address: str, ) -> bool:
        return IPBlacklistRepository.is_blocked(
            ip_address=ip_address,
            now=timezone.now(),
        )

    @staticmethod
    def add_blacklist(
            *,
            ip_address: str,
            reason: str,
            expires_at=None,
            created_by,
    ):

        return IPBlacklistRepository.create(
            ip_address=ip_address,
            reason=reason,
            expires_at=expires_at,
            created_by=created_by,
        )

    @staticmethod
    def get_blacklists(page: int, page_size: int):
        blacklists = list(IPBlacklistRepository.find_recent(
            page=page,
            page_size=page_size,
        ))

        total = IPBlacklistRepository.count()

        return {
            "blacklists": {
                "items": blacklists,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": ((total + page_size - 1)
                                // page_size
                                ),
            }
        }

    @staticmethod
    def update_blacklist(blacklist_id: int, **data):
        blacklist = IPBlacklistRepository.get_by_id(blacklist_id)
        if blacklist is None:
            raise LookupError("黑名单记录不存在")

        if not data:
            raise ValueError("至少提供一个需要更新的字段")

        if "ip_address" in data and data["ip_address"] is None:
            raise ValueError("ip_address 不能为空")

        if "is_active" in data and data["is_active"] is None:
            raise ValueError("is_active 不能为空")

        if "reason" in data and data["reason"] is None:
            data["reason"] = ""

        return IPBlacklistRepository.update(blacklist, **data)

    @staticmethod
    def deleteArticleBySlugs(ids: list[int]):
        ids = list(set(ids))
        return IPBlacklistRepository.deleteArticleBySlugs(ids)
