from fastapi import APIRouter

from .article import router as article_router
from .setting import router as setting_router
from .message import router as message_router
from .user import router as user_router

router = APIRouter(prefix="/api/v1")

router.include_router(article_router)
router.include_router(setting_router)
router.include_router(user_router)
router.include_router(message_router)