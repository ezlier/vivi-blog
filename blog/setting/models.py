from django.db import models


class WebSetting(models.Model):
    name = models.CharField(max_length=50)
    web_name = models.CharField(max_length=50)
    name_avatar = models.CharField(max_length=50)
    about_md = models.TextField(blank=True)
    footer_text1 = models.CharField(max_length=100, blank=True)
    footer_text2 = models.CharField(max_length=100, blank=True)

    create_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        if self.pk:
            old = WebSetting.objects.get(pk=self.pk)
            if old.name_avatar and old.name_avatar != self.name_avatar:
                old.name_avatar.delete(save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.web_name
