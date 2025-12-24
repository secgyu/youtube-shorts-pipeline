import os
import shutil
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Generator

from config.settings import settings
from .logger import get_logger

logger = get_logger("file_manager")


def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_date_folder() -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder = settings().videos_path / date_str
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def generate_output_path(prefix: str, extension: str) -> Path:
    folder = get_date_folder()
    filename = f"{prefix}_{get_timestamp()}.{extension}"
    return folder / filename


def generate_temp_path(prefix: str, extension: str) -> Path:
    temp_dir = settings().temp_path
    filename = f"{prefix}_{get_timestamp()}_{os.getpid()}.{extension}"
    return temp_dir / filename


@contextmanager
def temp_file(prefix: str, extension: str) -> Generator[Path, None, None]:
    path = generate_temp_path(prefix, extension)
    try:
        yield path
    finally:
        if path.exists():
            try:
                path.unlink()
                logger.debug(f"Deleted temp file: {path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {path}: {e}")


@contextmanager
def temp_directory(prefix: str = "shorts") -> Generator[Path, None, None]:
    temp_dir = settings().temp_path / f"{prefix}_{get_timestamp()}"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Deleted temp directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to delete temp directory {temp_dir}: {e}")


def cleanup_old_temp_files(max_age_hours: int = 24) -> int:
    temp_dir = settings().temp_path
    if not temp_dir.exists():
        return 0
    
    deleted_count = 0
    cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
    
    for item in temp_dir.iterdir():
        try:
            if item.stat().st_mtime < cutoff_time:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
                deleted_count += 1
                logger.debug(f"Cleaned up old temp item: {item}")
        except Exception as e:
            logger.warning(f"Failed to clean up {item}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} old temp items")
    
    return deleted_count


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(name: str, max_length: int = 100) -> str:
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    
    name = ' '.join(name.split())
    
    if len(name) > max_length:
        name = name[:max_length].rsplit(' ', 1)[0]
    
    return name.strip()
