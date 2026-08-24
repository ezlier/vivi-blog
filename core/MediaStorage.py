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


def _sanitize_filename(name: str) -> str:
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "")
    return name.strip()
