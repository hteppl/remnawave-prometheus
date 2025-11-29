import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_env_config() -> Dict[str, Any]:
    """Load configuration from .env file."""
    load_dotenv()

    api_url = os.getenv('REMNA_API_URL')
    api_token = os.getenv('REMNA_API_TOKEN')

    if not api_url:
        logger.error("REMNA_API_URL is not set in .env file")
        sys.exit(1)

    if not api_token:
        logger.error("REMNA_API_TOKEN is not set in .env file")
        sys.exit(1)

    config = {
        'api_url': api_url.rstrip('/'),
        'api_token': api_token,
        'update_interval': int(os.getenv('UPDATE_INTERVAL', '600'))
    }

    return config
