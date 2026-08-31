from fastapi import APIRouter

from .essay import router as essay_router
from .comment import router as comment_router
from .article import router as article_router
from .setting import router as setting_router
from .message import router as message_router
from .auth import router as auth_router
from .visitor import router as visitor_router
from .tag import router as tag_router
from .user import router as user_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(setting_router)
router.include_router(message_router)
router.include_router(essay_router)
router.include_router(visitor_router)
router.include_router(tag_router)
router.include_router(comment_router)
router.include_router(article_router)
router.include_router(user_router)
