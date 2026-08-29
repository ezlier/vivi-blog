from django.db.models import Count

from .models import Tag


class TagRepository:

    @staticmethod
    def find_recent(*, page: int, page_size: int):
        offset = (page - 1) * page_size

        return (
            Tag.objects
            .annotate(article_count=Count("articles", distinct=True))
            .order_by("name")[offset:offset + page_size]
        )

    @staticmethod
    def count():
        return Tag.objects.count()

    @staticmethod
    def get_by_id(tag_id: int):
        return Tag.objects.filter(id=tag_id).first()

    @staticmethod
    def get_by_id_with_article_count(tag_id: int):
        return (
            Tag.objects
            .annotate(article_count=Count("articles", distinct=True))
            .filter(id=tag_id)
            .first()
        )

    @staticmethod
    def get_by_name(name: str):
        return Tag.objects.filter(name=name).first()

    @staticmethod
    def get_by_name_excluding(name: str, tag_id: int):
        return Tag.objects.filter(name=name).exclude(id=tag_id).first()

    @staticmethod
    def get_or_create(name: str):
        return Tag.objects.get_or_create(name=name)

    @staticmethod
    def create(name: str):
        return Tag.objects.create(name=name)

    @staticmethod
    def update(tag: Tag, name: str):
        tag.name = name
        tag.save(update_fields=["name"])
        return tag

    @staticmethod
    def delete(tag: Tag):
        tag.delete()
