from blog.essay.models import Essay


class EssayRepository:
    @staticmethod
    def getEssayList(offset: int, limit: int,):
        return Essay.objects.all().order_by("-created_at")[offset:offset + limit]

    @staticmethod
    def getEssayCount():
        return Essay.objects.all().count()

    @staticmethod
    def create(**data):
        return Essay.objects.create(**data)