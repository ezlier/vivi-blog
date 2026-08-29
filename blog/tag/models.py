from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="标签名称", )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", )

    class Meta:
        db_table = "tags"
        ordering = ["name"]
        verbose_name = "标签"
        verbose_name_plural = "标签"

    def __str__(self):
        return self.name
