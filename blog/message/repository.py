from blog.message.models import Message


class MessageRepository:
    @staticmethod
    def getArticlesList():
        return Message.objects.all().order_by('-created_at')

    @staticmethod
    def UserCreateMessage(**data):
        return Message.objects.create(**data)
