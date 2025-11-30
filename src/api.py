import logging
import aiohttp
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


async def fetch_nodes(session: aiohttp.ClientSession, api_url: str, api_token: str) -> List[Dict[str, Any]]:
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

    async with session.get(f"{api_url}/nodes", headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
        response.raise_for_status()
        data = await response.json()

    nodes = data.get("response", [])
    logger.info(f"Successfully fetched {len(nodes)} nodes from API")

    return nodes
