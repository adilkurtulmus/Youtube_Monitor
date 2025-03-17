YouTube Stream Monitoring Dashboard
A comprehensive Grafana dashboard for real-time monitoring of YouTube live streams using Prometheus metrics. Track stream status, viewer counts, engagement metrics, and detect outages across multiple YouTube channels simultaneously.
🌟 Features

Live Stream Status Monitoring: Real-time tracking of stream status (LIVE/OFFLINE)
Viewer Count Tracking: Monitor concurrent viewers for live streams
Outage Detection: Track and visualize stream outages over time
API Health Monitoring: Monitor YouTube API errors and response rates
Engagement Metrics: Track views, likes, comments, and engagement rates
Channel Stats: Monitor subscriber counts and other channel metrics
Multi-Stream Support: Monitor multiple streams/channels simultaneously
Historical Data: View historical performance with customizable time ranges

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

Then reference it in your Prometheus configuration:

scrape_configs:
  - job_name: 'youtube'
    file_sd_configs:
      - files:
        - 'youtube_monitor.json'
    scrape_interval: 30s

Restart Prometheus to apply the changes.

Step 3: Import the Grafana Dashboard
There are two ways to import the dashboard:

Option 1: Import via Grafana.com

1. In Grafana, go to "Create" > "Import"
2. Enter dashboard ID: 23108
3. Select your Prometheus data source
4. Click "Import"

Option 2: Import JSON Directly

1. In Grafana, go to "Create" > "Import"
2. Click "Upload JSON file" and select youtube_stream_monitoring_dashboard.json from this repository
Select your Prometheus data source
Click "Import"

Configuration
Exporter Configuration
The exporter is configured through the streams list in prometheus_youtube_exporter.py:

streams = [
    {
        'name': 'Main_Channel',        # A unique name for the stream
        'channel_name': 'Channel Name', # Display name
        'channel_id': 'UCxxxxxxxx',    # YouTube channel ID
        'video_id': 'xxxxxxxxxxx',     # YouTube video/stream ID
        'api_key': 'YOUR_API_KEY',     # YouTube API key
        'environment': 'Production'    # Environment tag
    },
    # Add more streams as needed
]

Metrics Check Frequency
You can adjust how often metrics are checked by modifying the interval parameter:

# Change the interval from 30 seconds to your preferred value (in seconds)
thread = threading.Thread(target=run_monitor, args=(stream, metrics, 30))

API Usage Optimization
The exporter is designed to minimize API usage:

- Stream status is checked every cycle (default: 30 seconds)
- Engagement metrics (views, likes) are checked every 5 cycles
- Channel information (subscribers) is checked every 10 cycles

Available Metrics

- youtube_stream_status: Stream status (1=LIVE, 0=OFFLINE)
- youtube_stream_viewers: Current live viewer count
- youtube_video_views: Total video view count
- youtube_video_likes: Like count
- youtube_video_comments: Comment count
- youtube_channel_subscribers: Channel subscriber count
- youtube_engagement_rate: Engagement rate (likes/views %)
- youtube_stream_check_count_total: Total number of checks performed
- youtube_stream_error_count_total: Total number of stream errors detected
- youtube_api_errors_total: Total number of YouTube API errors

Dashboard Panels
Main Metrics

- YouTube Stream Status: Current stream status (LIVE/OFFLINE)
- Outages in Last 24 Hours: Count of stream outages in the last 24 hours
- API Errors: Count of YouTube API errors in the last 24 hours
- Total Check Count: Number of checks performed
- API Error Rate: Percentage of API errors compared to total checks
- YouTube Stream Uptime: 24-hour stream uptime percentage

Viewership and Engagement

_ YouTube Viewer Count: Real-time and historical viewer count graph
_ YouTube Stream Status Timeline: Timeline of stream status changes
_ Engagement Metrics: Views, likes, comments counts
_ Subscriber Count: Real-time channel subscriber count
_ Engagement Rate: Percentage of viewers who engaged with the stream

Troubleshooting
Common Issues
No Metrics Showing

- Verify the exporter is running (curl http://localhost:8001)
- Check Prometheus target status in Prometheus UI
- Verify your YouTube API key is valid

API Errors

- Your API key might have exceeded its quota
- Reduce check frequency to stay within API limits
- Create a new API key with higher quotas

Dashboard Shows "No Data"

Verify Prometheus is scraping the exporter correctly
Check for label matching issues in dashboard queries
Restart the exporter and verify metrics are being generated

Missing Stream Status

Verify the video ID is correct and is a live stream
Make sure the channel has public statistics enabled

Installation as a System Service
For production environments, you may want to run the exporter as a system service:
Linux (systemd)
Create a service file at /etc/systemd/system/youtube-exporter.service:

[Unit]
Description=YouTube Stream Monitoring Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/download/youtube_yayin
ExecStart=/home/download/youtube_yayin/venv/bin/python3 /home/download/youtube_yayin/youtube_monitor.py
Restart=always
RestartSec=30
StandardOutput=append:/var/log/youtube-monitor.log
StandardError=append:/var/log/youtube-monitor-error.log
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target

Then enable and start the service:

sudo systemctl enable youtube-exporter
sudo systemctl start youtube-exporter

Docker Installation
You can also run the exporter in Docker:

docker build -t youtube-exporter .
docker run -d -p 8001:8001 --name youtube-exporter youtube-exporter


Customizing the Dashboard
You can customize the dashboard to fit your needs:

Add or remove panels
Adjust thresholds for status indicators
Create additional alerts
Modify time ranges
Add custom annotations for important events
