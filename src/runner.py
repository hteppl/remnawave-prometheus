import asyncio
import logging
import aiohttp
import signal
from typing import Dict, Any

from .api import fetch_nodes
from .targets import generate_prometheus_targets, save_targets

logger = logging.getLogger(__name__)


async def update_targets(session: aiohttp.ClientSession, output_path: str, env_config: Dict[str, Any]) -> bool:
    """Fetch targets from API and update the targets file."""
    try:
        nodes = await fetch_nodes(session, env_config['api_url'], env_config['api_token'])
        targets = generate_prometheus_targets(nodes)

        if not targets:
            logger.warning("No valid targets found")

        save_targets(targets, output_path)
        logger.info(f"Successfully generated {len(targets)} target(s)")

        return True

    except Exception as e:
        logger.error(f"Error during update: {e}")
        return False


async def run_continuous_updates(output_path: str, env_config: Dict[str, Any]):
    """Run continuous update loop."""
    logger.info("Configuration loaded:")
    logger.info(f"  API URL: {env_config['api_url']}")
    logger.info(f"  Update Interval: {env_config['update_interval']}s")
    logger.info("Starting continuous update mode")
    logger.info("Press Ctrl+C to stop")

    async with aiohttp.ClientSession() as session:
        try:
            while True:
                await update_targets(session, output_path, env_config)
                logger.info(f"Next update in {env_config['update_interval']}s...")
                await asyncio.sleep(env_config['update_interval'])
        except asyncio.CancelledError:
            logger.info("Stopped")
            raise


async def shutdown(signal_name: str, task):
    """Handle shutdown signal."""
    logger.info(f"Received {signal_name}, stopping...")
    task.cancel()
    await task


async def run(output_path: str, env_config: Dict[str, Any]):
    """Setup signal handlers and run continuous updates."""
    loop = asyncio.get_running_loop()
    task = asyncio.create_task(run_continuous_updates(output_path, env_config))

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(shutdown(s.name, task))
        )

    try:
        await task
    except asyncio.CancelledError:
        pass
