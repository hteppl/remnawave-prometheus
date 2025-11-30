import asyncio
import logging
import sys

from .config import load_env_config
from .generators import BlackboxTargetGenerator, NodeExporterTargetGenerator
from .runner import run


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )

    env_config = load_env_config()

    generators = []

    if env_config["enable_blackbox"]:
        generators.append(BlackboxTargetGenerator("generated/blackbox.yml"))

    if env_config["enable_node_exporter"]:
        generators.append(NodeExporterTargetGenerator("generated/node.yml", env_config["node_exporter_ports"]))

    if not generators:
        logging.error("No generators enabled. Please enable at least one generator in .env")
        sys.exit(1)

    asyncio.run(run(generators, env_config))


if __name__ == "__main__":
    main()
