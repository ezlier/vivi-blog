from blog.setting.models import WebSetting


class SettingRepository:
    @staticmethod
    def get():
        return WebSetting.objects.first()

    @staticmethod
    def getNameAvatar():
        return WebSetting.objects.values_list("name_avatar", flat=True).first()

    @staticmethod
    def update(**data):
        return WebSetting.objects.filter(id=1).update(**data)
