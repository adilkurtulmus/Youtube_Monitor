YouTube Stream Monitoring Dashboard

![Screenshot_01](https://github.com/user-attachments/assets/02bdf72f-eb87-48e8-9160-b1f878544a6d)

![Screenshot_02](https://github.com/user-attachments/assets/b985a0cf-8193-4c8a-9216-5b543b64510f)

A comprehensive Grafana dashboard for real-time monitoring of YouTube live streams using Prometheus metrics.

Features

- Live Stream Status Monitoring: Real-time tracking of stream status (LIVE/OFFLINE)
- Viewer Count Tracking: Monitor concurrent viewers for live streams
- Outage Detection: Track and visualize stream outages over time
- API Health Monitoring: Monitor YouTube API errors and response rates
- Engagement Metrics: Track views, likes, comments, and engagement rates
- Channel Stats: Monitor subscriber counts and other channel metrics
- Multi-Stream Support: Monitor multiple streams/channels simultaneously
- Historical Data: View historical performance with customizable time ranges

Requirements

- Grafana 11.x or later
- Prometheus data source
- Python 3.6+
- YouTube Data API v3 key
- prometheus_client and requests Python libraries


Installation
Step 1: Set Up the Prometheus YouTube Exporter

1. Clone this repository:

git clone https://github.com/yourusername/youtube-stream-monitoring.git
cd youtube-stream-monitoring

2. Install required Python dependencies:
pip install prometheus_client requests

3. Configure your YouTube API key and channels:

    - Obtain a YouTube Data API v3 key from Google Cloud Console
    - Edit prometheus_youtube_exporter.py and update the streams list with your channels
  
4. Run the exporter:

python prometheus_youtube_exporter.py

The exporter runs on port 8001 by default. You can access metrics at http://localhost:8001

Step 2: Configure Prometheus

Option 1: Using prometheus.yml
Add the following to your prometheus.yml configuration:

scrape_configs:
  - job_name: 'youtube'
    static_configs:
      - targets: ['localhost:8001']
    scrape_interval: 30s
    
Option 2: Using File-Based Service Discovery
Create a JSON file (e.g., youtube_monitor.json):

[
  {
    "targets": [
      "10.20.48.126:8001"
    ],
    "labels": {
      "job": "youtube_monitor",
      "service": "streaming"
    }
  }
]





