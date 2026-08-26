from blog.articles.repository import ArticlesRepository
from blog.comment.repository import CommentRepository


class UserCommentService:
    @staticmethod
    def getCommentBySlug(slug: str):
        article = (ArticlesRepository.getArticleBySlug(slug))

        if article is None:
            raise ValueError("文章不存在")

        return CommentRepository.find_by_article(article)

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



