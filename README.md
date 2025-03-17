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
