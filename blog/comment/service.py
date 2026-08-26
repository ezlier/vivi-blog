import math

from blog.articles.repository import ArticlesRepository
from blog.comment.repository import CommentRepository


class UserCommentService:
    @staticmethod
    def getCommentBySlug(slug: str, page: int = 1, page_size: int = 10):
        article = (ArticlesRepository.getArticleBySlug(slug))

        if article is None:
            raise ValueError("文章不存在")

        offset = (page - 1) * page_size

        comments = CommentRepository.find_by_article(
            article=article,
            offset=offset,
            limit=page_size)
        total = CommentRepository.count_by_article(article)

        total_pages = math.ceil(
            total / page_size
        ) if total > 0 else 0

        return {
            "comments": {
                "items": comments,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }
        }

    @staticmethod
    def createComment(*,
                      article_slug: str,
                      nickname: str,
                      email: str | None,
                      QQ: int | None = None,
                      content: str,
                      IP: str,
                      ):

        article = (ArticlesRepository.getArticleBySlug(article_slug))

        if article is None:
            raise ValueError("文章不存在")

        if article.is_draft:
            raise ValueError(
                "不能评论草稿文章"
            )

        return CommentRepository.create(
            article=article,
            nickname=nickname,
            email=email,
            QQ=QQ,
            content=content,
            IP=IP
        )


class AdminCommentService:
    @staticmethod
    def getAllComment(page: int = 1, page_size: int = 10):
        offset = (page - 1) * page_size

        comments = CommentRepository.find_all(
            offset=offset,
            limit=page_size,
        )
        total = CommentRepository.count_all()

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return {
            "comments": {
                "items": list(comments),
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }
        }

    @staticmethod
    def deleteCommentsByIds(ids: list[int]):
        ids = list(set(ids))
        if not ids:
            return 0

        return CommentRepository.delete_by_ids(ids)