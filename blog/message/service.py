import math

from blog.message.repository import MessageRepository


class MessageService:
    @staticmethod
    def getMessageList(page: int = 1, page_size: int = 10):
        offset = (page - 1) * page_size
        MessageList = MessageRepository.getArticlesList(
            offset=offset,
            limit=page_size,
        )
        total = MessageRepository.count_all()

        total_pages = math.ceil(total / page_size) if total > 0 else 0
        return {
            "messages": {
                "items": list(MessageList),
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
            }
        }

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
    def deleteMessageByids(ids):
        ids = list(set(ids))
        if not ids:
            return 0

        deleted_count = MessageRepository.deleteMessageByIds(ids)
        return deleted_count
