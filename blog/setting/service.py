from blog.setting.Repository import SettingRepository


class SettingService:
    @staticmethod
    def get():
        setting = SettingRepository.get()

        if setting is None:
            raise Exception
        print(type(setting))
        return setting