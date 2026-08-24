import random
import string

from django.core.files.base import ContentFile

from blog.articles.models import Article
from blog.articles.repository import ArticlesRepository
from core import MediaStorage


class ArticlesService:

    @staticmethod
    def getArticlesList():
        articles = ArticlesRepository.getArticlesList()

        return list(
            articles.values(
                "title",
                "slug",
                "cover",
                "is_draft",
                "created_at",
                "updated_at",
            )
        )

    @staticmethod
    def getArticleBySlug(slug: str):
        return ArticlesRepository.getArticleBySlug(slug)
        # article = ArticlesRepository.getArticleBySlug(slug)
        # if article is None:
        #     return None
        #
        # cover_url = None
        #
        # if article.cover:
        #     if request:
        #         cover_url = request.build_absolute_uri(
        #             article.cover.url
        #         )
        #     else:
        #         cover_url = article.cover.url
        #
        # return {
        #     "id": article.id,
        #     "title": article.title,
        #     "slug": article.slug,
        #     "cover": cover_url,
        #     "content": article.content,
        #     "is_draft": article.is_draft,
        #     "created_at": article.created_at,
        #     "updated_at": article.updated_at,
        # }

    @staticmethod
    def create_article(
            *,
            title: str,
            content: str,
            is_draft: bool,
            cover_file=None,
    ):
        # 1. 生成随机字符串
        slug = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # 2. 保存封面文件
        cover_path = None

        if cover_file:
            cover_path = MediaStorage.save(cover_file, title=slug)

        # 3. 保存数据库
        article = ArticlesRepository.create(
            title=title,
            slug=slug,
            content=content,
            is_draft=is_draft,
            cover=cover_path,
        )

        return {
            "title": article.title,
            "slug": article.slug,
            "cover": cover_path,
            "content": article.content,
            "is_draft": article.is_draft,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
        }
