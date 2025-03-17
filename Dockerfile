FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY prometheus_youtube_exporter.py .

# Expose the metrics port
EXPOSE 8001

# Run the exporter
CMD ["python", "prometheus_youtube_exporter.py"]
