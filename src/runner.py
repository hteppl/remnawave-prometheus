import asyncio
import logging
import aiohttp
import signal
from typing import Dict, Any, List

from .api import fetch_nodes
from .generators import TargetGenerator

logger = logging.getLogger(__name__)


async def update_targets(
    session: aiohttp.ClientSession, generators: List[TargetGenerator], env_config: Dict[str, Any]
) -> bool:
    try:
        nodes = await fetch_nodes(session, env_config["api_url"], env_config["api_token"])

        if not nodes:
            logger.warning("No nodes fetched from API")

        if not env_config["scrape_disabled_nodes"]:
            nodes = [node for node in nodes if not node.get("isDisabled", False)]

        for generator in generators:
            count = generator.process(nodes)
            logger.info(f"Successfully generated {count} targets")

        return True

    except Exception as e:
        logger.error(f"Error during update: {e}")
        return False


async def run_continuous_updates(generators: List[TargetGenerator], env_config: Dict[str, Any]):
    logger.info("Configuration loaded:")
    logger.info(f"  API URL: {env_config['api_url']}")
    logger.info(f"  Update Interval: {env_config['update_interval']}s")
    logger.info(f"  Scrape Disabled Nodes: {env_config['scrape_disabled_nodes']}")
    logger.info(f"  Output Files: {len(generators)}")
    for i, gen in enumerate(generators, 1):
        logger.info(f"    {i}. {gen.output_path}")

    async with aiohttp.ClientSession() as session:
        try:
            while True:
                await update_targets(session, generators, env_config)
                logger.info(f"Next update in {env_config['update_interval']}s...")
                await asyncio.sleep(env_config["update_interval"])
        except asyncio.CancelledError:
            logger.info("Stopped")
            raise


async def shutdown(signal_name: str, task):
    logger.info(f"Received {signal_name}, stopping...")
    task.cancel()
    await task


async def run(generators: List[TargetGenerator], env_config: Dict[str, Any]):
    loop = asyncio.get_running_loop()
    task = asyncio.create_task(run_continuous_updates(generators, env_config))

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s.name, task)))

    try:
        await task
    except asyncio.CancelledError:
        pass
