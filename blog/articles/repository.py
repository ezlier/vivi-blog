from blog.articles.models import Article


class ArticlesRepository:
    @staticmethod
    def getArticlesList():
        return Article.objects.filter(is_draft=False).order_by("-created_at")

    @staticmethod
    def getArticleBySlug(slug: str):
        return (
            Article.objects
            .filter(
                slug=slug,
                is_draft=False,
            )
            .first()
        )

    @staticmethod
    def create(**data):
        return Article.objects.create(**data)