from django.db import models

class Essay(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="Slug")
    content = models.TextField(verbose_name="正文")
    imgs = models.ImageField(upload_to="essay/imgs/%Y/%m/", blank=True, null=True, verbose_name="配图")
    is_draft = models.BooleanField(default=True, verbose_name="是否草稿")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "essay"
        verbose_name = "笔记"
        verbose_name_plural = "笔记"

    def __str__(self):
        return self.title
