from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name="标题")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="Slug")
    tags = models.ManyToManyField("tag.Tag", blank=True, null=True, related_name="articles", verbose_name="标签", )
    cover = models.ImageField(upload_to="articles/covers/%Y/%m/", blank=True, null=True, verbose_name="封面")
    content = models.TextField(verbose_name="正文")
    is_draft = models.BooleanField(default=True, verbose_name="是否草稿")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "articles"
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self):
        return self.title
