import math
import random
import string

from blog.essay.repository import EssayRepository
from core import MediaStorage


class UserEssayService:
    @staticmethod
    def getEssayList(page: int = 1, page_size: int = 10):
        offset = (page - 1) * page_size
        essayList = EssayRepository.getEssayList(offset, page_size)
        total = EssayRepository.getEssayCount()

        total_pages = math.ceil(
            total / page_size
        ) if total > 0 else 0

        return {
            "essayList": {
                "items": essayList,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }
        }

    @staticmethod
    def getEssayBySlug(slug: str):
        pass

    @staticmethod
    def createEssay(
            *,
            title: str,
            content: str,
            is_draft: bool,
            imgs=None,
    ):
        # 1. 生成随机字符串
        slug = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # 2. 保存封面文件
        cover_path = None

        if imgs:
            cover_path = MediaStorage.saveImgs(imgs, slug=slug)

        # 3. 保存数据库
        Essay = EssayRepository.create(
            title=title,
            slug=slug,
            content=content,
            is_draft=is_draft,
            cover=cover_path,
        )

        return {
            "title": Essay.title,
            "slug": Essay.slug,
            "cover": cover_path,
            "content": Essay.content,
            "is_draft": Essay.is_draft,
            "created_at": Essay.created_at,
            "updated_at": Essay.updated_at,
        }
