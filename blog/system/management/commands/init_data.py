import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from blog.setting.models import WebSetting

User = get_user_model()


class Command(BaseCommand):

    help = "初始化系统默认数据"

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            "开始初始化数据..."
        )

        self.create_superuser()
        self.create_default_setting()

        self.stdout.write(
            self.style.SUCCESS(
                "数据初始化完成"
            )
        )

    def create_superuser(self):
        username = os.getenv(
            "DJANGO_SUPERUSER_USERNAME",
            "admin",
        )

        password = os.getenv(
            "DJANGO_SUPERUSER_PASSWORD"
        )

        email = os.getenv(
            "DJANGO_SUPERUSER_EMAIL",
            "",
        )

        if not password:
            raise RuntimeError(
                "未配置 DJANGO_SUPERUSER_PASSWORD"
            )

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()

            self.stdout.write(
                f"创建超级管理员：{username}"
            )

        else:
            self.stdout.write(
                f"超级管理员已存在：{username}"
            )

    def create_default_setting(self):

        setting, created = WebSetting.objects.get_or_create(
            id=1,
            defaults={
                "name": "name",
                "web_name": "我的博客",
                "name_avatar": "cover/avatar/avatar.png",
                "about_md": "一个 Django + FastAPI 博客",
                "footer_text1": "text1",
                "footer_text2": "text2",
                "create_time": timezone.now(),
            },
        )

        if created:
            self.stdout.write(
                "创建默认网站设置"
            )
        else:
            self.stdout.write(
                "网站设置已存在"
            )