import logging
import re
import yaml
from typing import List, Dict, Any

from .base import TargetGenerator

logger = logging.getLogger(__name__)


def _is_ipv4(address: str) -> bool:
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}(:\d+)?$"
    return bool(re.match(ipv4_pattern, address))


class BlackboxTargetGenerator(TargetGenerator):
    def generate(self, targets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        domains = []
        ipv4_addresses = []

        for target in targets:
            name = target.get("name")
            if name.startswith("-"):
                continue

            address = target.get("address")

            if _is_ipv4(address):
                ipv4_addresses.append(address)
            else:
                domains.append(address)

        all_targets = domains + ipv4_addresses
        return [{"targets": all_targets}] if all_targets else []

    def save(self, transformed_targets: List[Dict[str, Any]]) -> None:
        self._ensure_output_dir()

        with open(self.output_path, "w") as f:
            yaml.dump(transformed_targets, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Generated Prometheus targets file: {self.output_path}")
