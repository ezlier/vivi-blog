from blog.articles.models import Article
from blog.comment.models import Comment


class CommentRepository:
    @staticmethod
    def find_by_article(article):
        return Comment.objects.filter(article=article).order_by("created_at")

    @staticmethod
    def create(**data):
        return Comment.objects.create(**data)

