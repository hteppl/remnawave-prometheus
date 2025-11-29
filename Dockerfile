FROM python:3.12-alpine

WORKDIR /app

# Copy and install dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Run the bot
CMD ["python", "-m", "src"]