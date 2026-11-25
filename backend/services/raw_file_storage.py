import asyncio
from pathlib import Path
import re
from typing import Optional

# Raw uploads are stored as `<file_id><ext>`, where file_id is the content hash
# used as the primary key of file_metadata. This makes lookup by id trivial.
RAW_DIR = Path("uploaded_excels")

_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]+$")


def _safe_ext(original_filename: Optional[str]) -> str:
    ext = Path(original_filename or "").suffix.lower()
    return ext if re.fullmatch(r"\.[a-z0-9]{1,5}", ext) else ".xlsx"


def _check_id(file_id: str) -> None:
    if not _SAFE_ID.match(file_id):
        raise ValueError("Invalid file id")


def _write_sync(path: Path, data: bytes) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def find_raw_file(file_id: str) -> Optional[Path]:
    _check_id(file_id)
    if not RAW_DIR.exists():
        return None
    return next((p for p in RAW_DIR.glob(f"{file_id}.*") if p.is_file()), None)


async def save_raw_file(file_id: str, file_bytes: bytes, original_filename: Optional[str]) -> Path:
    _check_id(file_id)
    # Re-uploading identical content replaces the previous copy.
    delete_raw_file(file_id)
    path = RAW_DIR / f"{file_id}{_safe_ext(original_filename)}"
    await asyncio.to_thread(_write_sync, path, file_bytes)
    return path


def delete_raw_file(file_id: str) -> bool:
    path = find_raw_file(file_id)
    if path is None:
        return False
    path.unlink(missing_ok=True)
    return True
