import os
import uuid
from pathlib import Path

from django.conf import settings


def get_document_dir(user_id: int, notebook_id: int) -> Path:
    path = Path(settings.MEDIA_ROOT) / 'files' / str(user_id) / str(notebook_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_uploaded_file(user_id: int, notebook_id: int, uploaded_file) -> tuple[str, int]:
    original_name = uploaded_file.name
    ext = Path(original_name).suffix.lower()
    stored_name = f'{uuid.uuid4().hex}{ext}'
    target_dir = get_document_dir(user_id, notebook_id)
    target_path = target_dir / stored_name

    size = 0
    with open(target_path, 'wb') as dest:
        for chunk in uploaded_file.chunks():
            dest.write(chunk)
            size += len(chunk)

    relative_path = str(Path('files') / str(user_id) / str(notebook_id) / stored_name)
    return relative_path, size


def get_absolute_path(relative_path: str) -> Path:
    return Path(settings.MEDIA_ROOT) / relative_path


def delete_file(relative_path: str) -> None:
    path = get_absolute_path(relative_path)
    if path.exists():
        os.remove(path)
