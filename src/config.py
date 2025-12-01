import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_env_config() -> Dict[str, Any]:
    load_dotenv()

    api_url = os.getenv("REMNA_API_URL")
    api_token = os.getenv("REMNA_API_TOKEN")

    if not api_url:
        logger.error("REMNA_API_URL is not set in .env file")
        sys.exit(1)

    if not api_token:
        logger.error("REMNA_API_TOKEN is not set in .env file")
        sys.exit(1)

    node_exporter_ports_str = os.getenv("NODE_EXPORTER_PORTS", "9100")
    node_exporter_ports = [int(port.strip()) for port in node_exporter_ports_str.split(",") if port.strip() != ""]

    config = {
        "api_url": api_url.rstrip("/"),
        "api_token": api_token,
        "update_interval": int(os.getenv("UPDATE_INTERVAL", "600")),
        "enable_blackbox": os.getenv("ENABLE_BLACKBOX_EXPORTER", "true").lower() == "true",
        "enable_node_exporter": os.getenv("ENABLE_NODE_EXPORTER", "true").lower() == "true",
        "node_exporter_ports": node_exporter_ports,
        "scrape_disabled_nodes": os.getenv("SCRAPE_DISABLED_NODES", "true").lower() == "true",
    }

    return config
