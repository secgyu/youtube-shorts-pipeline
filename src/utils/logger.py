import sys
from pathlib import Path
from loguru import logger

from config.settings import PROJECT_ROOT


def setup_logger(
    log_level: str = "INFO",
    log_dir: Path | None = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    logger.remove()
    
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
    )
    
    if log_dir is None:
        log_dir = PROJECT_ROOT / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_dir / "pipeline_{time:YYYY-MM-DD}.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
    )
    
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}\n{exception}",
        rotation=rotation,
        retention=retention,
        encoding="utf-8",
    )
    
    logger.info(f"Logger initialized with level: {log_level}")


def get_logger(name: str = "pipeline"):
    return logger.bind(name=name)
