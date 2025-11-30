# Prometheus Dynamic Targets Generator

A Python project that dynamically generates Prometheus targets from the Remna API for service discovery.

## Overview

This project provides a Python script that continuously fetches targets from the Remna API and generates a Prometheus-compatible targets file. The script runs as a daemon, automatically updating targets at a configurable interval.

## Project Structure

```
.
├── src/                      # Main package
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point (with logging setup)
│   ├── config.py            # Configuration management
│   ├── api.py               # API client
│   ├── runner.py            # Main runner loop
│   └── generators/          # Target generators package
│       ├── __init__.py      # Generators package init
│       ├── base.py          # Abstract base class
│       └── prometheus_generator.py  # Prometheus generator implementation
├── prometheus.yml            # Example Prometheus config with file import
├── .env                      # Environment configuration (create from .env.example)
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
└── generated/               # Output directory (created automatically)
    └── targets.yml          # Generated targets file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Or using the virtual environment:
```bash
.venv/bin/pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
REMNA_API_URL=https://api.example.com/targets
REMNA_API_TOKEN=your_api_token_here
UPDATE_INTERVAL=30
```

### Environment Variables

- `REMNA_API_URL` - The Remna API endpoint to fetch targets from (required)
- `REMNA_API_TOKEN` - API authentication token (required)
- `UPDATE_INTERVAL` - Interval in seconds between target updates (default: 30)

## Usage

### Basic Usage

Run continuously and update targets every `UPDATE_INTERVAL` seconds:
```bash
python -m src
```

The script will:
- Load configuration from `.env`
- Fetch targets from the API every `UPDATE_INTERVAL` seconds
- Automatically regenerate `generated/targets.yml`
- Run until stopped with Ctrl+C

**Output:**
```
[2025-11-29 16:30:00] INFO - Configuration loaded:
[2025-11-29 16:30:00] INFO -   API URL: https://api.example.com/targets
[2025-11-29 16:30:00] INFO -   Update Interval: 30s
[2025-11-29 16:30:00] INFO - Starting continuous update mode
[2025-11-29 16:30:00] INFO - Press Ctrl+C to stop
[2025-11-29 16:30:00] INFO - Successfully fetched 3 targets from API
[2025-11-29 16:30:00] INFO - Generated targets file: generated/targets.yml
[2025-11-29 16:30:00] INFO - Successfully generated 3 target(s)
[2025-11-29 16:30:00] INFO - Next update in 30s...
```

### Custom Output Path

Specify a custom output path:
```bash
python -m src --output custom/path/targets.yml
```

### Multiple Output Files

Generate multiple target files simultaneously (useful for different Prometheus instances or configurations):
```bash
python -m src --output "generated/prod-targets.yml,generated/dev-targets.yml"
```

This will:
- Fetch targets from API once
- Generate both files with the same data
- Show progress for all files

## API Response Format

The Remna API should return JSON in this format:

```json
{
  "targets": [
    {
      "host": "localhost:9090",
      "labels": {
        "env": "production",
        "service": "prometheus"
      }
    },
    {
      "host": "localhost:9100",
      "labels": {
        "env": "production",
        "service": "node_exporter"
      }
    }
  ]
}
```

Alternatively, you can use `"target"` instead of `"host"`:
```json
{
  "targets": [
    {
      "target": "localhost:9090",
      "labels": {
        "env": "production"
      }
    }
  ]
}
```

## Generated Output

The script generates a file in Prometheus `file_sd_configs` format:

```yaml
- targets:
  - localhost:9090
  labels:
    env: production
    service: prometheus
- targets:
  - localhost:9100
  labels:
    env: production
    service: node_exporter
```

## Integration with Prometheus

The `prometheus.yml` file shows how to import the generated targets:

```yaml
scrape_configs:
  # Dynamic targets fetched from Remna API
  # Update refresh_interval to match UPDATE_INTERVAL from .env
  - job_name: 'dynamic_targets'
    file_sd_configs:
      - files:
          - 'generated/targets.yml'
        refresh_interval: 30s
```

Prometheus will automatically reload the targets file at the specified interval. Make sure `refresh_interval` matches or is less than your `UPDATE_INTERVAL`.

## Running as a Service

### Systemd Service (Recommended)

Create a systemd service for continuous updates:

**`/etc/systemd/system/prometheus-targets.service`**
```ini
[Unit]
Description=Prometheus Targets Generator
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/project
ExecStart=/path/to/python -m src
User=prometheus
Group=prometheus
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable prometheus-targets.service
sudo systemctl start prometheus-targets.service

# Check status
sudo systemctl status prometheus-targets.service

# View logs
sudo journalctl -u prometheus-targets.service -f
```

### Docker Container

Create a `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY .env .

CMD ["python", "-m", "src"]
```

Build and run:
```bash
docker build -t prometheus-targets .

docker run -d \
  --name prometheus-targets \
  --restart unless-stopped \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/generated:/app/generated \
  prometheus-targets
```

## Error Handling

The script handles errors gracefully:
- **API failures**: Logged with timestamp, script continues and retries at next interval
- **Invalid JSON**: Error logged, update skipped, retries at next interval
- **Network timeouts**: 30-second timeout with error logging
- **Graceful shutdown**: Handles SIGINT (Ctrl+C) and SIGTERM cleanly

If an update fails, the script will retry at the next interval without crashing.

## Command-Line Arguments

```
--output PATH    Output file path (default: generated/targets.yml)
```

## Security

- Never commit your `.env` file to version control
- Store `REMNA_API_TOKEN` securely (use secrets manager in production)
- Use HTTPS for `REMNA_API_URL`
- Limit API token permissions to read-only
- Run as non-privileged user (not root)

## Monitoring

Watch the logs to ensure targets are updating:
```bash
# Systemd
sudo journalctl -u prometheus-targets.service -f

# Docker
docker logs -f prometheus-targets

# Direct execution
python -m src
```

Look for:
- Successful API fetches
- Target count
- Update timestamps
- Any error messages

## Troubleshooting

**Script exits immediately:**
- Check `.env` file exists and has required variables
- Verify `REMNA_API_URL` and `REMNA_API_TOKEN` are set

**API connection failures:**
- Verify network connectivity
- Check API URL is correct and accessible
- Ensure API token is valid
- Check firewall rules

**Prometheus not picking up targets:**
- Verify `generated/targets.yml` exists and has content
- Check Prometheus `file_sd_configs` path matches output path
- Ensure Prometheus has read permissions on the file
- Check Prometheus logs for file_sd errors

## License

MIT
