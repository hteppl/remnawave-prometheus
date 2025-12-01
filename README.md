<p align="center">
  <img src="https://raw.githubusercontent.com/hteppl/remnawave-prometheus/master/.github/images/logo.png" alt="remnawave-prometheus" width="800px">
</p>

## remnawave-prometheus

<p align="left">
  <a href="https://github.com/hteppl/remnawave-prometheus/releases/"><img src="https://img.shields.io/github/v/release/hteppl/remnawave-prometheus.svg" alt="Release"></a>
  <a href="https://hub.docker.com/r/hteppl/remnawave-prometheus/"><img src="https://img.shields.io/badge/DockerHub-remnawave--prometheus-blue" alt="DockerHub"></a>
  <a href="https://github.com/hteppl/remnawave-prometheus/actions"><img src="https://img.shields.io/github/actions/workflow/status/hteppl/remnawave-prometheus/dockerhub-publish.yaml" alt="Build"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12-blue.svg" alt="Python 3.12"></a>
  <a href="https://opensource.org/licenses/GPL-3.0"><img src="https://img.shields.io/badge/license-GPLv3-green.svg" alt="License: GPL v3"></a>
</p>

Just a simple way to autogenerate prometheus targets, based on Remnawave panel (https://docs.rw).

## Features

- **Auto-discovery** - Automatically fetches nodes from Remnawave API and generates Prometheus targets
- **Multiple Exporters** - Supports both Node Exporter and Blackbox Exporter targets
- **Configurable Ports** - Define custom ports for Node Exporter targets
- **Periodic Updates** - Continuously updates targets at configurable intervals
- **Lightweight** - Minimal dependencies and simple configuration
- **Docker Ready** - Easy deployment with Docker and Docker Compose

## Prerequisites

Before you begin, ensure you have the following:

- **Remnawave Panel** with nodes configured
- **Remnawave API Token** - Generate from your Remnawave panel settings
- **Prometheus** - Running instance to consume the generated targets

## Configuration

Copy [`.env.example`](.env.example) to `.env` and fill in your values:

```env
# Remnawave API Configuration
REMNA_API_URL=https://remna.docs.rw/api
REMNA_API_TOKEN=your_api_token_here

# Update interval in seconds (how often to regenerate targets)
UPDATE_INTERVAL=600

# Enable/disable generators
ENABLE_NODE_EXPORTER=true
ENABLE_BLACKBOX_EXPORTER=true

# Node exporter ports (comma-separated)
NODE_EXPORTER_PORTS=9100
```

### Configuration Reference

| Variable                   | Description                                        | Default | Required |
|----------------------------|----------------------------------------------------|---------|----------|
| `REMNA_API_URL`            | Remnawave API endpoint to fetch targets from       | -       | Yes      |
| `REMNA_API_TOKEN`          | API authentication token                           | -       | Yes      |
| `UPDATE_INTERVAL`          | Interval in seconds between target updates         | 600     | No       |
| `ENABLE_NODE_EXPORTER`     | Enable/disable Node Exporter target generation     | true    | No       |
| `ENABLE_BLACKBOX_EXPORTER` | Enable/disable Blackbox Exporter target generation | true    | No       |
| `NODE_EXPORTER_PORTS`      | Comma-separated list of ports for Node Exporter    | 9100    | No       |

## Installation

### Docker (recommended)

1. Create the docker-compose.yml:

```yaml
services:
  remnawave-prometheus:
    image: hteppl/remnawave-prometheus:latest
    container_name: remnawave-prometheus
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./generated:/app/generated
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

2. Create and configure your environment file:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

3. Start the container:

```bash
docker compose up -d && docker compose logs -f
```

### Manual Installation

1. Clone the repository:

```bash
git clone https://github.com/hteppl/remnawave-prometheus.git
cd remnawave-prometheus
```

2. Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create and configure your environment file:

```bash
cp .env.example .env
```

5. Run the application:

```bash
python -m src
```

## How It Works

1. **Initial Fetch** - On startup, the service fetches all nodes from the Remnawave API

2. **Target Generation** - Based on configuration, it generates target files for Node Exporter and/or Blackbox Exporter

3. **Continuous Updates** - The service polls the Remnawave API at the configured interval (`UPDATE_INTERVAL`) and
   regenerates targets

4. **Prometheus Integration** - Prometheus reads the generated target files and automatically discovers new nodes

The service generates two target files:

- `generated/blackbox.yml` - Targets for Blackbox Exporter
- `generated/node.yml` - Targets for Node Exporter

Example `prometheus.yml` configuration:

```yaml
scrape_configs:
  - job_name: "node_servers"
    file_sd_configs:
      - files:
          - /etc/generated/node.yml
        refresh_interval: 10m

  - job_name: "blackbox_https_probes"
    metrics_path: /probe
    params:
      module: [ http_2xx ]
    file_sd_configs:
      - files:
          - /etc/generated/blackbox.yml
        refresh_interval: 10m
    relabel_configs:
      - source_labels: [ __address__ ]
        target_label: __param_target
      - source_labels: [ __param_target ]
        target_label: instance
      - target_label: __address__
        replacement: blackbox_exporter:9115
```

Prometheus will automatically reload the targets files at the specified interval. Make sure `refresh_interval` matches
or is less than or equal to your `UPDATE_INTERVAL`.

### Logs

Monitor logs to diagnose issues:

```bash
# Docker
docker compose logs -f

# Manual
# Logs are output to stdout with timestamps
```

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
