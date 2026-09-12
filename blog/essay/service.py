import math
import random
import string

from blog.essay.repository import EssayRepository
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from core import MediaStorage


class UserEssayService:

    @staticmethod
    def getEssayList(request, page: int = 1, page_size: int = 10, ):
        offset = (page - 1) * page_size
        essayListBase = EssayRepository.getEssayList(offset, page_size)
        total = EssayRepository.getEssayCount()

        total_pages = math.ceil(
            total / page_size
        ) if total > 0 else 0

        essayList = []

        media_url = settings.MEDIA_URL.rstrip("/")
        base_url = str(request.base_url).rstrip("/")

        for essay in essayListBase:
            essay.imgs = MediaStorage.getImgs(imgs_Path=essay.imgs)

            imgs = []
            for img in essay.imgs:
                imgs.append(f"{base_url}{media_url}/{img.lstrip('/')}")

            essay.imgs = imgs
            essayList.append(essay)

        return {
            "essayList": {
                "items": essayList,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }
        }


class AdminEssayService:
    @staticmethod
    def getEssayBySlug(slug: str):
        essay = EssayRepository.getEssayBySlug(slug)
        if essay is None:
            raise ValueError("笔记不存在")
        return essay

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
            imgs=cover_path,
        )

        return {
            "title": Essay.title,
            "slug": Essay.slug,
            "imgs": cover_path,
            "content": Essay.content,
            "is_draft": Essay.is_draft,
            "created_at": Essay.created_at,
            "updated_at": Essay.updated_at,
        }

    @staticmethod
    def deleteEssay(slugs: list[str], ):
        slugs = list(set(slugs))

        if not slugs:
            return 0

        imgs = EssayRepository.getImgsBySlugs(slugs)

        deleted_count = EssayRepository.deleteEssayBySlugs(slugs)

        for imgPath in imgs:
            MediaStorage.delete(imgPath)

        return deleted_count

    @staticmethod
    def updateEssayBySlug(
            *,
            slug: str,
            title: str | None = None,
            content: str | None = None,
            imgs=None,
            created_at=None,
            is_draft: bool | None = None,
    ):
        with transaction.atomic():
            essay = EssayRepository.getEssayBySlugForUpdate(slug)
            if essay is None:
                raise ValueError("笔记不存在")

            update_fields = {}

            if title is not None:
                update_fields["title"] = title
            if content is not None:
                update_fields["content"] = content
            if created_at is not None:
                update_fields["created_at"] = created_at
            if is_draft is not None:
                update_fields["is_draft"] = is_draft

            if imgs:
                old_imgs_path = essay.imgs

                if len(imgs) > MediaStorage.MAX_IMAGE_COUNT:
                    raise MediaStorage.ImageValidationError(
                        f"最多上传 {MediaStorage.MAX_IMAGE_COUNT} 张图片"
                    )

                # 先校验全部新图片，避免校验失败时删除原图片。
                for image in imgs:
                    MediaStorage.validate_image(image)

                if old_imgs_path:
                    MediaStorage.delete(old_imgs_path)

                update_fields["imgs"] = MediaStorage.saveImgs(imgs, slug=slug)

            if update_fields:
                update_fields["updated_at"] = now()
                for field, value in update_fields.items():
                    setattr(essay, field, value)
                essay.save(update_fields=list(update_fields))

        return essay
