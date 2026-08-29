from blog.articles.models import Article


class ArticlesRepository:
    @staticmethod
    def getArticlesList():
        return (
            Article.objects
            .filter(is_draft=False)
            .prefetch_related("tags")
            .order_by("-created_at")
        )

    @staticmethod
    def getArticleBySlug(slug: str):
        return (
            Article.objects
            .prefetch_related("tags")
            .filter(
                slug=slug,
                is_draft=False,
            )
            .first()
        )

    @staticmethod
    def getArticleBySlugForUpdate(slug: str):
        return (
            Article.objects
            .select_for_update()
            .prefetch_related("tags")
            .filter(slug=slug)
            .first()
        )

    @staticmethod
    def getCoverBySlug(slug: str):
        return Article.objects.filter(slug=slug).values_list("cover", flat=True).first()

    @staticmethod
    def create(**data):
        return Article.objects.create(**data)

    @staticmethod
    def deleteArticleBySlugs(slugs: list[str]):
        deleted_count, _ = (Article.objects.filter(slug__in=slugs).delete())
        return deleted_count

    @staticmethod
    def getCoversBySlugs(slugs: list[str]):
        return list(
            Article.objects
            .filter(slug__in=slugs)
            .values_list("cover", flat=True)
        )

    @staticmethod
    def updateArticleBySlugs(slug: str, **data):
        return Article.objects.filter(slug=slug).update(**data)
