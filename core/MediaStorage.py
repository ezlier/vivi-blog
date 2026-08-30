import os
import random
import shutil
import string
from datetime import datetime
from pathlib import Path

from django.conf import settings
from PIL import Image, UnidentifiedImageError


MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_IMAGE_COUNT = 6
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".png"}
ALLOWED_IMAGE_FORMATS = {
    "JPEG": ".jpg",
    "PNG": ".png",
}


class ImageValidationError(ValueError):
    pass


def save(cover_file, title: str) -> str:
    ext = validate_image(cover_file)

    # 文件名与 title 相同，仅去除文件名中不允许的字符
    safe_title = _sanitize_filename(title) or "cover"

    # 按年月分目录：cover/YYYY/MM/
    now = datetime.now()
    relative_path = f"cover/{now:%Y}/{now:%m}/{safe_title}{ext}"

    target = Path(settings.MEDIA_ROOT) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)

    _write_upload(target, cover_file)

    return relative_path


def updateCover(cover_file, title: str, old_path: str | None = None) -> str:
    # 存在原图则覆盖原图，否则按新文件保存
    ext = validate_image(cover_file)
    if old_path:
        old_ext = Path(old_path).suffix.lower()
        if old_ext == ext:
            _overwrite(old_path, cover_file)
            return old_path

        new_path = save(cover_file, title=title)
        delete(old_path)
        return new_path

    return save(cover_file, title=title)


def saveAvatar(avatar_file, old_path: str | None = None) -> str:
    # 头像固定保存到 cover/avatar/ 并重命名为 avatar
    ext = validate_image(avatar_file)
    relative_path = f"cover/avatar/avatar{ext}"

    target = Path(settings.MEDIA_ROOT) / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    _write_upload(target, avatar_file)

    # 旧头像若不在固定路径，删除旧文件避免残留
    if old_path and old_path != relative_path:
        delete(old_path)

    return relative_path


def delete(relative_path: str) -> None:
    if not relative_path:
        return

    media_root = Path(settings.MEDIA_ROOT)
    target = _resolve_media_path(relative_path)

    if target.is_dir():
        shutil.rmtree(target)
    else:
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
    validate_image(file)
    target = _resolve_media_path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    _write_upload(target, file)


def _sanitize_filename(name: str) -> str:
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "")
    return name.strip()


def _resolve_media_path(relative_path: str) -> Path:
    """Resolve a stored media path and reject paths outside MEDIA_ROOT."""
    media_root = Path(settings.MEDIA_ROOT).resolve()
    path = Path(relative_path)
    if path.is_absolute():
        raise ValueError("非法媒体文件路径")

    target = (media_root / path).resolve()
    try:
        target.relative_to(media_root)
    except ValueError as exc:
        raise ValueError("非法媒体文件路径") from exc

    return target


def saveImgs(imgs: list, slug: str):
    if len(imgs) > MAX_IMAGE_COUNT:
        raise ImageValidationError(
            f"最多上传 {MAX_IMAGE_COUNT} 张图片"
        )

    # 先完成全部校验，避免中途失败时只保存部分图片。
    validated_imgs = [
        (img, validate_image(img))
        for img in imgs
    ]

    safe_title = _sanitize_filename(slug) or "imgs"
    now = datetime.now()
    i = 1
    for img, ext in validated_imgs:
        imgName = str(i) + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        relative_path = f"imgs/{now:%Y}/{now:%m}/{safe_title}/{imgName}{ext}"

        target = Path(settings.MEDIA_ROOT) / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)

        _write_upload(target, img)
        i += 1

    return f"imgs/{now:%Y}/{now:%m}/{safe_title}"


def validate_image(upload_file) -> str:
    """
    校验上传文件大小、扩展名和真实图片格式。

    返回基于真实格式确定的规范扩展名，调用方不应信任用户提交的扩展名。
    """
    filename = upload_file.filename or ""
    filename_ext = os.path.splitext(filename)[1].lower()

    if filename_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ImageValidationError("只支持 .jpg、.png 图片")

    file_obj = upload_file.file

    try:
        file_obj.seek(0, os.SEEK_END)
        file_size = file_obj.tell()
        if file_size == 0:
            raise ImageValidationError("图片文件不能为空")
        if file_size > MAX_IMAGE_SIZE:
            raise ImageValidationError("单张图片大小不能超过 5MB")

        file_obj.seek(0)
        with Image.open(file_obj) as image:
            actual_format = image.format
            image.verify()
    except ImageValidationError:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError):
        raise ImageValidationError("上传文件不是有效的 JPG 或 PNG 图片")
    finally:
        file_obj.seek(0)

    if actual_format not in ALLOWED_IMAGE_FORMATS:
        raise ImageValidationError("只支持 JPG、PNG 图片")

    expected_ext = ALLOWED_IMAGE_FORMATS[actual_format]
    if filename_ext != expected_ext:
        raise ImageValidationError("图片扩展名与真实文件类型不匹配")

    return expected_ext


def _write_upload(target: Path, upload_file) -> None:
    upload_file.file.seek(0)
    with target.open("wb") as destination:
        shutil.copyfileobj(
            upload_file.file,
            destination,
            length=1024 * 1024,
        )


def getImgs(imgs_Path: str):
    print(imgs_Path)
    image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.tif', '.tiff'}
    result = []

    try:
        target = _resolve_media_path(imgs_Path)
    except ValueError:
        return result

    if not os.path.isdir(target):
        return result

    # 规范化传入路径：统一为正斜杠，去除尾部斜杠
    base_path = imgs_Path.replace('\\', '/').rstrip('/')

    try:
        for entry in os.listdir(target):
            full_path = os.path.join(target, entry)
            if os.path.isfile(full_path):
                ext = os.path.splitext(entry)[1].lower()
                if ext in image_exts:
                    # 使用相对路径构建返回值
                    path = f"{base_path}/{entry}"
                    result.append(path)
                    print(path)
    except PermissionError:
        pass

    result.sort()
    return result
