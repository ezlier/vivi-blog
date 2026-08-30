from datetime import datetime

from fastapi import APIRouter, Depends, Request, UploadFile, Form, File, HTTPException

from blog.articles.schema import ArticleListResponse, ArticleResponse, ArticleBatchDeleteRequest
from blog.articles.service import ArticlesService
from core.dependencies import get_current_superuser
from core.response import ApiResponse

router = APIRouter(
    prefix="/articles",
    tags=["文章"]
)


def _serialize_article(article, request: Request):
    cover_url = None
    if article.cover:
        cover_url = str(request.base_url).rstrip('/') + article.cover.url

    return {
        "title": article.title,
        "slug": article.slug,
        "cover": cover_url,
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


@router.get("/{slug}", response_model=ApiResponse[ArticleResponse])
def getArticleBySlug(slug: str, request: Request):
    try:
        article = ArticlesService.getArticleBySlug(slug)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="文章不存在",
        )

    return ApiResponse(data=_serialize_article(article, request))


@router.get("/", response_model=ApiResponse[list[ArticleListResponse]])
def getArticlesList(request: Request):
    ArticlesBase = ArticlesService.getArticlesList()
    ArticleList = []
    for article in ArticlesBase:
        ArticleList.append(_serialize_article(article, request))
    return ApiResponse(data=ArticleList)


# ============================
# ==========管理员接口==========
# ============================


@router.get("/test")
def admintest(current_user=Depends(get_current_superuser)):
    return {"message": "admin"}


@router.post("/", response_model=ApiResponse[ArticleResponse])
def create_article(
        request: Request,
        title: str = Form(...),
        content: str = Form(...),
        is_draft: bool = Form(True),
        cover: UploadFile | None = File(None),
        tag_names: list[str] | None = Form(None),

        current_user=Depends(get_current_superuser)
):
    try:
        article = ArticlesService.create_article(
            title=title,
            content=content,
            is_draft=is_draft,
            cover_file=cover,
            tag_names=tag_names,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return ApiResponse(data=_serialize_article(article, request))


@router.delete("/", response_model=ApiResponse)
def deleteArticleBySlug(
        data: ArticleBatchDeleteRequest,
        current_user=Depends(get_current_superuser)
):
    deleted_count = ArticlesService.deleteArticleBySlugs(data.slugs)
    return ApiResponse(data={"deleted_count": deleted_count, })


@router.put("/", response_model=ApiResponse[ArticleResponse])
def updateArticleBySlug(
        request: Request,
        slug: str = Form(),
        title: str = Form(...),
        content: str = Form(...),
        is_draft: bool = Form(True),
        cover: UploadFile | None = File(None),
        created_at: datetime | None = Form(None),
        tag_names: list[str] | None = Form(None),

        current_user=Depends(get_current_superuser)
):
    try:
        article = ArticlesService.updateArticleBySlugs(
            slug=slug,
            title=title,
            content=content,
            is_draft=is_draft,
            cover=cover,
            created_at=created_at,
            tag_names=tag_names,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    return ApiResponse(data=_serialize_article(article, request))
