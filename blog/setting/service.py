from blog.setting.Repository import SettingRepository
from core import MediaStorage


class SettingService:
    @staticmethod
    def get():
        setting = SettingRepository.get()

        if setting is None:
            raise Exception
        print(type(setting))
        return setting


class AdminSettingService:
    @staticmethod
    def update(
            name: str,
            web_name: str,
            about_md: str,
            footer_text1: str,
            footer_text2: str,
            name_avatar=None,
            create_time=None
    ):
        # 只更新传入的非空字段
        update_fields = {}

        if name:
            update_fields["name"] = name
        if web_name:
            update_fields["web_name"] = web_name
        if about_md:
            update_fields["about_md"] = about_md
        if footer_text1:
            update_fields["footer_text1"] = footer_text1
        if footer_text2:
            update_fields["footer_text2"] = footer_text2
        if create_time:
            update_fields["create_time"] = create_time

        # 上传了新头像才更新，并覆盖原图片
        if name_avatar:
            old_avatar = SettingRepository.getNameAvatar()
            update_fields["name_avatar"] = MediaStorage.saveAvatar(
                name_avatar, old_path=old_avatar
            )

        if not update_fields:
            return

        SettingRepository.update(**update_fields)
