from django.db import models


class Message(models.Model):
    IP = models.TextField(verbose_name="IP")
    content = models.TextField(verbose_name="评论内容", )
    nickname = models.CharField(max_length=50, verbose_name="昵称", )
    email = models.EmailField(null=True, blank=True, verbose_name="邮箱", )
    QQ = models.IntegerField(null=True, verbose_name="QQ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", )

    class Meta:
        db_table = 'message'
        verbose_name = '留言'

    def __str__(self):
        return f"{self.nickname}: {self.content[:20]}"
