from blog.message.models import Message


class MessageRepository:
    @staticmethod
    def getArticlesList(offset: int, limit: int):
        return Message.objects.all().order_by('-created_at')[offset:offset + limit]

    @staticmethod
    def UserCreateMessage(**data):
        return Message.objects.create(**data)

    @staticmethod
    def deleteMessageByIds(ids: list[int]):
        deleted_count, _ = (Message.objects.filter(id__in=ids).delete())
        return deleted_count

    @staticmethod
    def count_all():
        return Message.objects.count()
