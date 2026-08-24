from blog.setting.models import WebSetting


class SettingRepository:
    @staticmethod
    def get():
        return WebSetting.objects.first()