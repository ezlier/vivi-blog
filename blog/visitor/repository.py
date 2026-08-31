from datetime import datetime

from django.db.models import Q

from core.blacklist import matching_blacklist_targets

from .models import IPBlacklist, VisitorLog


class VisitorRepository:

    @staticmethod
    def create(
            *,
            ip_address: str,
            user_agent: str,
            device_type: str,
    ):
        return VisitorLog.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            device_type=device_type,
        )

    @staticmethod
    def find_recent(
            *,
            page: int,
            page_size: int,
    ):
        offset = (page - 1) * page_size

        return VisitorLog.objects.order_by("-visited_at")[offset:offset + page_size]

    @staticmethod
    def count():
        return VisitorLog.objects.count()


class IPBlacklistRepository:

    @staticmethod
    def is_blocked(ip_address: str, now: datetime, ) -> bool:
        return IPBlacklist.objects.filter(
            ip_address__in=matching_blacklist_targets(ip_address),
            is_active=True,
        ).filter(
            Q(expires_at__isnull=True)
            | Q(expires_at__gt=now)
        ).exists()

    @staticmethod
    def find_all():
        return IPBlacklist.objects.all()

    @staticmethod
    def find_active(now: datetime):
        return IPBlacklist.objects.filter(
            is_active=True,
        ).filter(
            Q(expires_at__isnull=True)
            | Q(expires_at__gt=now)
        )

    @staticmethod
    def find_recent(
            *,
            page: int,
            page_size: int,
    ):
        offset = (page - 1) * page_size

        return IPBlacklist.objects.order_by("-created_at")[offset:offset + page_size]

    @staticmethod
    def count():
        return IPBlacklist.objects.count()

    @staticmethod
    def get_by_id(blacklist_id: int):
        return IPBlacklist.objects.filter(id=blacklist_id).first()

    @staticmethod
    def create(
            *,
            ip_address: str,
            reason: str,
            expires_at,
            created_by,
    ):
        return IPBlacklist.objects.create(
            ip_address=ip_address,
            reason=reason,
            expires_at=expires_at,
            created_by=created_by,
        )

    @staticmethod
    def update(blacklist, **data):
        for field, value in data.items():
            setattr(blacklist, field, value)

        blacklist.save(update_fields=list(data.keys()))
        return blacklist

    @staticmethod
    def delete(blacklist):
        blacklist.delete()

    @staticmethod
    def delete_blacklists(ids: list[int]):
        deleted_count, _ = (IPBlacklist.objects.filter(id__in=ids).delete())
        return deleted_count

    # Keep the old name temporarily for callers outside this module.
    deleteArticleBySlugs = delete_blacklists
