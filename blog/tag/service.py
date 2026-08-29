from collections.abc import Iterable

from django.db import transaction

from .models import Tag
from .repository import TagRepository
from .schema import normalize_tag_name


class TagService:

    @staticmethod
    def normalize_names(names: Iterable[str] | None) -> list[str]:
        normalized_names = []
        seen = set()

        for name in names or []:
            name = name.strip()
            if not name or name in seen:
                continue

            if len(name) > 50:
                raise ValueError("标签名称不能超过 50 个字符")

            seen.add(name)
            normalized_names.append(name)

        return normalized_names

    @staticmethod
    def resolve_names(names: Iterable[str] | None) -> list[Tag]:
        return [
            TagRepository.get_or_create(name)[0]
            for name in TagService.normalize_names(names)
        ]

    @staticmethod
    def get_tags(page: int, page_size: int):
        tags = list(TagRepository.find_recent(
            page=page,
            page_size=page_size,
        ))
        total = TagRepository.count()

        return {
            "tags": {
                "items": tags,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": ((total + page_size - 1) // page_size),
            }
        }

    @staticmethod
    @transaction.atomic
    def create_tag(name: str):
        name = normalize_tag_name(name)
        tag, _ = TagRepository.get_or_create(name)

        return TagRepository.get_by_id_with_article_count(tag.id)

    @staticmethod
    @transaction.atomic
    def update_tag(tag_id: int, name: str):
        name = normalize_tag_name(name)
        tag = TagRepository.get_by_id(tag_id)
        if tag is None:
            raise LookupError("标签不存在")

        target = TagRepository.get_by_name_excluding(name, tag_id)
        if target is not None:
            target.articles.add(*tag.articles.all())
            tag.delete()
            return TagRepository.get_by_id_with_article_count(target.id)

        TagRepository.update(tag, name)
        return TagRepository.get_by_id_with_article_count(tag.id)

    @staticmethod
    @transaction.atomic
    def delete_tag(tag_id: int):
        tag = TagRepository.get_by_id(tag_id)
        if tag is None:
            raise LookupError("标签不存在")

        TagRepository.delete(tag)
