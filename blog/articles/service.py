import random
import string

from django.db import transaction
from django.utils.timezone import now

from blog.articles.repository import ArticlesRepository
from blog.tag.service import TagService
from core import MediaStorage


class ArticlesService:

    @staticmethod
    def _to_article_data(article):
        return {
            "title": article.title,
            "slug": article.slug,
            "cover": str(article.cover) if article.cover else None,
            "content": article.content,
            "is_draft": article.is_draft,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
            "tags": [
                {
                    "id": tag.id,
                    "name": tag.name,
                }
                for tag in article.tags.all()
            ],
        }

    @staticmethod
    def getArticlesList():
        articles = ArticlesRepository.getArticlesList()

        return [
            ArticlesService._to_article_data(article)
            for article in articles
        ]

    @staticmethod
    def getArticleBySlug(slug: str):
        article = ArticlesRepository.getArticleBySlug(slug)
        if article is None:
            raise ValueError("文章不存在")

        return article

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
            tag_names: list[str] | None = None,
    ):
        with transaction.atomic():
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

            if tag_names is not None:
                article.tags.set(TagService.resolve_names(tag_names))

        return article

    @staticmethod
    def deleteArticleBySlugs(slugs: list[str], ):
        # 去重
        slugs = list(set(slugs))

        if not slugs:
            return 0

        # 删除前取出封面路径，用于同步删除文件
        covers = ArticlesRepository.getCoversBySlugs(slugs)

        deleted_count = ArticlesRepository.deleteArticleBySlugs(slugs)

        for cover in covers:
            if cover:
                MediaStorage.delete(cover)

        return deleted_count

    @staticmethod
    def updateArticleBySlugs(
            *,
            slug: str,
            title: str,
            content: str,
            is_draft: bool,
            cover=None,
            created_at=None,
            tag_names: list[str] | None = None,
    ):
        with transaction.atomic():
            article = ArticlesRepository.getArticleBySlugForUpdate(slug)
            if article is None:
                raise ValueError("文章不存在")

            # 只更新传入的非空字段
            update_fields = {}

            if title:
                update_fields["title"] = title
            if content:
                update_fields["content"] = content
            if is_draft is not None:
                update_fields["is_draft"] = is_draft
            if created_at:
                update_fields["created_at"] = created_at

            # 上传了新封面才更新，并覆盖原图片
            if cover:
                old_cover = article.cover.name if article.cover else None
                update_fields["cover"] = MediaStorage.updateCover(
                    cover, title=slug, old_path=old_cover
                )

            if update_fields:
                update_fields["updated_at"] = now()

                for field, value in update_fields.items():
                    setattr(article, field, value)

                article.save(update_fields=list(update_fields.keys()))

            if tag_names is not None:
                article.tags.set(TagService.resolve_names(tag_names))

        return article
