from django.db.models import F

from blog.comment.models import Comment


class CommentRepository:
    @staticmethod
    def find_by_article(article,
                        offset: int,
                        limit: int,
                        ):
        return Comment.objects.filter(article=article).order_by("created_at")[offset:offset + limit]

    @staticmethod
    def count_by_article(article, ) -> int:
        return Comment.objects.filter(article=article).count()

    @staticmethod
    def create(**data):
        return Comment.objects.create(**data)

    @staticmethod
    def find_all(offset: int, limit: int):
        return (
            Comment.objects
            .order_by("-created_at")
            .values(
                "id",
                "IP",
                "nickname",
                "email",
                "QQ",
                "content",
                "created_at",
                article_title=F("article__title"),
            )[offset:offset + limit]
        )

    @staticmethod
    def count_all() -> int:
        return Comment.objects.all().count()

    @staticmethod
    def delete_by_ids(ids: list[int]):
        deleted_count, _ = Comment.objects.filter(id__in=ids).delete()
        return deleted_count
