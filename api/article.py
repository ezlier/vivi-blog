from fastapi import APIRouter, Depends, Request, UploadFile, Form, File, HTTPException

from blog.articles.schema import ArticleListResponse, ArticleResponse
from blog.articles.service import ArticlesService
from core.dependencies import get_current_superuser
from core.response import ApiResponse

router = APIRouter(
    prefix="/articles",
    tags=["文章"]
)


@router.get("/test")
def admintest(current_user=Depends(get_current_superuser)):
    return {"message": "admin"}


@router.get("/{slug}", response_model=ApiResponse[ArticleResponse])
def getArticleBySlug(slug: str, request: Request):
    articleBase = ArticlesService.getArticleBySlug(slug)

    cover_url = None

    if articleBase.cover:
        cover_url = request.base_url._url.rstrip("/") + articleBase.cover.url

    article = {
        "title": articleBase.title,
        "slug": articleBase.slug,
        "cover": cover_url,
        "content": articleBase.content,
        "is_draft": articleBase.is_draft,
        "created_at": articleBase.created_at,
        "updated_at": articleBase.updated_at,
    }

    return ApiResponse(data=article)


@router.get("/", response_model=ApiResponse[list[ArticleListResponse]])
def getArticlesList():
    return ApiResponse(data=ArticlesService.getArticlesList())


# ============================
# ==========管理员接口==========
# ============================


@router.post("/", response_model=ApiResponse[ArticleResponse])
def create_article(
        title: str = Form(...),
        content: str = Form(...),
        is_draft: bool = Form(True),
        cover: UploadFile | None = File(None),

        # current_user=Depends(get_current_superuser)
):
    try:
        article = ArticlesService.create_article(
            title=title,
            content=content,
            is_draft=is_draft,
            cover_file=cover,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return ApiResponse(data=article)
