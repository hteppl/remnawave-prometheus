import asyncio
import argparse
import logging
import sys

from .config import load_env_config
from .runner import run


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        stream=sys.stdout
    )

    parser = argparse.ArgumentParser(
        description='Generate Prometheus targets file from Remna API (runs continuously)'
    )
    parser.add_argument(
        '--output',
        default='generated/targets.yml',
        help='Path to the output targets file (default: generated/targets.yml)'
    )
    args = parser.parse_args()

    env_config = load_env_config()

    asyncio.run(run(args.output, env_config))


if __name__ == '__main__':
    main()
