import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import settings
from src.utils.logger import setup_logger, get_logger


def main():
    config = settings()
    setup_logger(log_level=config.log_level)
    logger = get_logger("main")
    
    logger.info("=" * 50)
    logger.info("YouTube Shorts Pipeline Started")
    logger.info("=" * 50)
    
    try:
        # TODO: 파이프라인 단계별 실행
        logger.info("Pipeline completed successfully!")
        
    except Exception as e:
        logger.exception(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
