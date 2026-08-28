from blog.essay.models import Essay


class EssayRepository:
    @staticmethod
    def getEssayList(offset: int, limit: int,):
        return Essay.objects.filter(is_draft=False).order_by("-created_at")[offset:offset + limit]

    @staticmethod
    def getEssayCount():
        return Essay.objects.all().count()

    @staticmethod
    def create(**data):
        return Essay.objects.create(**data)

    @staticmethod
    def getImgsBySlugs(slugs: list[str]):
        return list(Essay.objects.filter(slug__in=slugs).values_list("imgs", flat=True))

    @staticmethod
    def deleteEssayBySlugs(slugs: list[str]):
        deleted_count, _ = (Essay.objects.filter(slug__in=slugs).delete())
        return deleted_count
