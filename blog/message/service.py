from blog.message.repository import MessageRepository


class MessageService:
    @staticmethod
    def getMessageList():
        MessageList = MessageRepository.getArticlesList()
        return list(
            MessageList.values(
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
            email=None,
            QQ=None,
    ):
        IP = None

        MessageRepository.UserCreateMessage(
            nickname=nickname,
            content=content,
            email=email,
            QQ=QQ,
            IP=IP
        )
