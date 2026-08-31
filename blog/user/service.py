from fastapi import HTTPException


class UserService:

    @staticmethod
    def rename(user, newName):
        user.username = newName
        user.save()

    @staticmethod
    def repwd(user, pwd, newPwd):
        if not user.check_password(pwd):
            raise HTTPException(status_code=401, detail="Old Password error")

        user.set_password(newPwd)
        user.save()
