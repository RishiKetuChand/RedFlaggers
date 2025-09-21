import logging
import sys
from typing import Optional

from ..config.settings import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Setup logging configuration for the service"""
    level = log_level or settings.service.log_level
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from Google Cloud libraries
    logging.getLogger('google.cloud').setLevel(logging.WARNING)
    logging.getLogger('google.auth').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('google.api_core').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)