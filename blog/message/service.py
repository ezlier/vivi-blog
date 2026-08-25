from blog.message.repository import MessageRepository


class MessageService:
    @staticmethod
    def getMessageList():
        MessageList = MessageRepository.getArticlesList()
        return list(
            MessageList.values(
                "id",
                "IP",
                "nickname",
                "email",
                "content",
                "QQ",
                "created_at"
            )
        )

    @staticmethod
    def userCreateMessage(
            nickname: str,
            content: str,
            IP: str,
            email=None,
            QQ=None,

    ):
        MessageRepository.UserCreateMessage(
            nickname=nickname,
            content=content,
            email=email,
            QQ=QQ,
            IP=IP
        )

    @staticmethod
    def deleteMessageBySlugs(ids):
        ids = list(set(ids))
        if not ids:
            return 0

        deleted_count = MessageRepository.deleteMessageBySlugs(ids)
        return deleted_count
