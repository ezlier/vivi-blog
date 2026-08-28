import os
from datetime import datetime
from pathlib import Path

from django.conf import settings


def save(cover_file, title: str) -> str:
    # 从上传文件名中提取扩展名（没有扩展名时默认 .jpg）
    ext = os.path.splitext(cover_file.filename)[1].lower() or ".jpg"

    # 文件名与 title 相同，仅去除文件名中不允许的字符
    safe_title = _sanitize_filename(title) or "cover"

    # 按年月分目录：cover/YYYY/MM/
    now = datetime.now()
    relative_path = f"cover/{now:%Y}/{now:%m}/{safe_title}{ext}"

    target = Path(settings.MEDIA_ROOT) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)

    target.write_bytes(cover_file.file.read())

    return relative_path


def updateCover(cover_file, title: str, old_path: str | None = None) -> str:
    # 存在原图则覆盖原图，否则按新文件保存
    if old_path:
        _overwrite(old_path, cover_file)
        return old_path

    return save(cover_file, title=title)


def saveAvatar(avatar_file, old_path: str | None = None) -> str:
    # 头像固定保存到 cover/avatar/ 并重命名为 avatar
    ext = os.path.splitext(avatar_file.filename)[1].lower() or ".jpg"
    relative_path = f"cover/avatar/avatar{ext}"

    target = Path(settings.MEDIA_ROOT) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(avatar_file.file.read())

    # 旧头像若不在固定路径，删除旧文件避免残留
    if old_path and old_path != relative_path:
        delete(old_path)

    return relative_path


def delete(relative_path: str) -> None:
    if not relative_path:
        return

    media_root = Path(settings.MEDIA_ROOT)
    target = media_root / relative_path
    target.unlink(missing_ok=True)

    # 清理空目录
    parent = target.parent
    while parent != media_root:
        try:
            parent.rmdir()
        except OSError:
            break
        parent = parent.parent


def _overwrite(relative_path: str, file) -> None:
    target = Path(settings.MEDIA_ROOT) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(file.file.read())


def _sanitize_filename(name: str) -> str:
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "")
    return name.strip()


def saveImgs(imgs, slug):
    return None