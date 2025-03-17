#!/usr/bin/env python3

import requests
import time
import json
import threading
from prometheus_client import start_http_server, Gauge, Counter, Info, REGISTRY

class YouTubeMetrics:
    """Central class for YouTube metrics"""

    def __init__(self):
        # Metrics for live stream status
        self.stream_status = Gauge(
            'youtube_stream_status',
            'YouTube stream status (1=LIVE, 0=OFFLINE)',
            ['channel_id', 'stream', 'video_id', 'channel_name', 'environment']
        )

        self.stream_viewers = Gauge(
            'youtube_stream_viewers',
            'YouTube stream viewer count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        # Video engagement metrics
        self.video_views = Gauge(
            'youtube_video_views',
            'Total view count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        self.video_likes = Gauge(
            'youtube_video_likes',
            'Like count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        self.video_comments = Gauge(
            'youtube_video_comments',
            'Comment count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        self.video_favorites = Gauge(
            'youtube_video_favorites',
            'Favorites count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        self.engagement_rate = Gauge(
            'youtube_engagement_rate',
            'Engagement rate (likes/views %)',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        # Channel metrics
        self.channel_subscribers = Gauge(
            'youtube_channel_subscribers',
            'Channel subscriber count',
            ['channel_id', 'stream', 'channel_name']
        )

        # Statistical counters - Same labels will be used for all channels
        self.check_count = Counter(
            'youtube_stream_check_count',
            'Total check count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        self.error_count = Counter(
            'youtube_stream_error_count',
            'Total error count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        self.api_errors = Counter(
            'youtube_api_errors',
            'YouTube API error count',
            ['channel_id', 'stream', 'video_id', 'channel_name']
        )

        # Channel information (metadata)
        self.channel_info = Info(
            'youtube_channel',
            'YouTube channel information',
            ['channel_id', 'channel_name']
        )

        # Video information (metadata)
        self.video_info = Info(
            'youtube_video',
            'YouTube video information',
            ['video_id', 'channel_id', 'stream']
        )

        # List of monitored streams
        self.registered_streams = set()

    def register_stream(self, channel_id, video_id, stream_name, channel_name, environment="Production"):
        """Register a new stream and initialize its basic metrics"""
        stream_key = f"{channel_id}_{video_id}_{stream_name}"

        if stream_key in self.registered_streams:
            return

        # Basic labels
        base_labels = {
            'channel_id': channel_id,
            'stream': stream_name,
            'video_id': video_id,
            'channel_name': channel_name
        }

        status_labels = {
            'channel_id': channel_id,
            'stream': stream_name,
            'video_id': video_id,
            'channel_name': channel_name,
            'environment': environment
        }

        # Initialize all gauge metrics as 0
        self.stream_status.labels(**status_labels).set(0)
        self.stream_viewers.labels(**base_labels).set(0)
        self.video_views.labels(**base_labels).set(0)
        self.video_likes.labels(**base_labels).set(0)
        self.video_comments.labels(**base_labels).set(0)
        self.video_favorites.labels(**base_labels).set(0)
        self.engagement_rate.labels(**base_labels).set(0)

        # Channel metrics
        channel_labels = {
            'channel_id': channel_id,
            'stream': stream_name,
            'channel_name': channel_name
        }
        self.channel_subscribers.labels(**channel_labels).set(0)

        # Initialize counters (these counters will be increased with Inc() first, but we're registering them now to see the metrics)
        # Set initial values to 0
        self.initialize_counters(base_labels)

        # Mark the stream as registered
        self.registered_streams.add(stream_key)

    def initialize_counters(self, labels):
        """Initialize basic counters - Prometheus won't show counters without calling this function"""

        # Initialize API errors
        try:
            # If we try to increase an unregistered counter, Prometheus creates a metric for it
            # Here we added 0, so the metric will be shown but its value won't change
            self.api_errors.labels(**labels).inc(0)
            self.check_count.labels(**labels).inc(0)
            self.error_count.labels(**labels).inc(0)
        except Exception as e:
            print(f"Error initializing counters: {str(e)}")

class YouTubeMonitor:
    """Class for monitoring a YouTube stream"""

    def __init__(self, channel_id, video_id, api_key, stream_name, channel_name, environment="Production", metrics=None):
        """
        Initialize YouTube monitor class

        Args:
            channel_id (str): YouTube channel ID
            video_id (str): Video/stream ID to monitor
            api_key (str): YouTube API key
            stream_name (str): Identifier name for the stream
            channel_name (str): Channel name
            environment (str): Environment info (Production, Test, etc.)
            metrics (YouTubeMetrics): Metrics class instance
        """
        self.channel_id = channel_id
        self.video_id = video_id
        self.api_key = api_key
        self.stream_name = stream_name
        self.channel_name = channel_name
        self.environment = environment

        # Labels for metrics
        self.base_labels = {
            'stream': stream_name,
            'video_id': video_id,
            'channel_id': channel_id,
            'channel_name': channel_name
        }

        self.status_labels = {
            'stream': stream_name,
            'video_id': video_id,
            'channel_id': channel_id,
            'channel_name': channel_name,
            'environment': environment
        }

        self.channel_labels = {
            'stream': stream_name,
            'channel_id': channel_id,
            'channel_name': channel_name
        }

        # Metrics class instance
        self.metrics = metrics if metrics else YouTubeMetrics()

        # Register stream and initialize metrics
        self.metrics.register_stream(channel_id, video_id, stream_name, channel_name, environment)

        # Record channel information (metadata)
        self.metrics.channel_info.labels(channel_id=channel_id, channel_name=channel_name).info({
            'stream_name': stream_name,
            'environment': environment
        })

    def check_stream_status(self):
        """Check live stream status using YouTube API"""
        try:
            # Increase check counter for each check - WHETHER THERE IS AN ERROR OR NOT
            self.metrics.check_count.labels(**self.base_labels).inc()

            # Get video details using API
            url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,liveStreamingDetails&id={self.video_id}&key={self.api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()

            is_live = False
            viewer_count = 0
            video_title = ""

            if 'items' in data and data['items']:
                item = data['items'][0]
                # Check stream status
                if 'snippet' in item:
                    if item['snippet'].get('liveBroadcastContent') == 'live':
                        is_live = True

                    # Get video title
                    video_title = item['snippet'].get('title', 'No title')

                # Get viewer count
                if 'liveStreamingDetails' in item and 'concurrentViewers' in item['liveStreamingDetails']:
                    viewer_count = int(item['liveStreamingDetails']['concurrentViewers'])

            # Record video information (metadata)
            self.metrics.video_info.labels(
                video_id=self.video_id,
                channel_id=self.channel_id,
                stream=self.stream_name
            ).info({
                'title': video_title,
                'is_live': str(is_live),
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            })

            # Update metrics
            self.metrics.stream_status.labels(**self.status_labels).set(1 if is_live else 0)

            # Update viewer count always (even if it's 0)
            self.metrics.stream_viewers.labels(**self.base_labels).set(viewer_count)

            status_text = "LIVE" if is_live else "OFFLINE"
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} - {self.stream_name} ({self.channel_name}) YouTube Stream {status_text}, Viewers: {viewer_count}")

            # If stream is offline, increase error counter
            if not is_live:
                self.metrics.error_count.labels(**self.base_labels).inc()

            return is_live, viewer_count, video_title

        except Exception as e:
            # In case of API error
            self.metrics.stream_status.labels(**self.status_labels).set(0)
            self.metrics.error_count.labels(**self.base_labels).inc()
            self.metrics.api_errors.labels(**self.base_labels).inc()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} - {self.stream_name} ({self.channel_name}) API ERROR: {str(e)}")
            return False, 0, ""

    def get_video_engagement(self):
        """Get video engagement metrics (likes, comments, views)"""
        try:
            # Get video statistics
            url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics&id={self.video_id}&key={self.api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if 'items' in data and data['items']:
                stats = data['items'][0]['statistics']

                # Get metrics (use 0 if not available)
                views = int(stats.get('viewCount', 0))
                likes = int(stats.get('likeCount', 0))
                comments = int(stats.get('commentCount', 0))
                favorites = int(stats.get('favoriteCount', 0))

                # Update Prometheus metrics
                self.metrics.video_views.labels(**self.base_labels).set(views)
                self.metrics.video_likes.labels(**self.base_labels).set(likes)
                self.metrics.video_comments.labels(**self.base_labels).set(comments)
                self.metrics.video_favorites.labels(**self.base_labels).set(favorites)

                # Calculate engagement rate (likes per view)
                if views > 0:
                    engagement_rate = (likes / views) * 100
                    self.metrics.engagement_rate.labels(**self.base_labels).set(engagement_rate)

                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{timestamp} - {self.stream_name} ({self.channel_name}) Views: {views}, Likes: {likes}, Comments: {comments}")
                return views, likes, comments

        except Exception as e:
            # Increase api_errors counter for each API error
            self.metrics.api_errors.labels(**self.base_labels).inc()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} - {self.stream_name} ({self.channel_name}) Failed to get engagement data: {str(e)}")
            return 0, 0, 0

    def get_channel_info(self):
        """Get channel information (subscriber count, etc.)"""
        try:
            # Get channel statistics
            url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics,snippet&id={self.channel_id}&key={self.api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()

            if 'items' in data and data['items']:
                item = data['items'][0]
                stats = item['statistics']
                snippet = item.get('snippet', {})

                # Get subscriber count
                subscriber_count = int(stats.get('subscriberCount', 0))

                # Update channel metrics
                self.metrics.channel_subscribers.labels(**self.channel_labels).set(subscriber_count)

                # Update channel information
                self.metrics.channel_info.labels(
                    channel_id=self.channel_id,
                    channel_name=self.channel_name
                ).info({
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', '')[:100] + '...',
                    'subscriber_count': str(subscriber_count),
                    'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
                })

                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{timestamp} - {self.stream_name} ({self.channel_name}) Channel subscriber count: {subscriber_count}")
                return subscriber_count

        except Exception as e:
            # In case of API error
            self.metrics.api_errors.labels(**self.base_labels).inc()
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{timestamp} - {self.stream_name} ({self.channel_name}) Failed to get channel information: {str(e)}")
            return 0

    def monitor_loop(self, interval=30):
        """Continuous monitoring loop"""
        engagement_interval = 5  # update engagement data every 5 check cycles
        channel_interval = 10    # update channel information every 10 check cycles

        count = 0
        while True:
            # Check stream status
            self.check_stream_status()

            # Check engagement metrics at specific intervals
            if count % engagement_interval == 0:
                self.get_video_engagement()

            # Update channel information at specific intervals
            if count % channel_interval == 0:
                self.get_channel_info()

            count += 1

            # Check at specified intervals
            time.sleep(interval)

def run_monitor(stream_config, metrics, interval=30):
    """Run a monitor"""
    monitor = YouTubeMonitor(
        stream_config['channel_id'],
        stream_config['video_id'],
        stream_config['api_key'],
        stream_config['name'],
        stream_config['channel_name'],
        stream_config.get('environment', 'Production'),
        metrics
    )

    print(f"Monitoring started: {stream_config['name']} - {stream_config['channel_name']} - Video ID: {stream_config['video_id']}")
    monitor.monitor_loop(interval)

def main():
    # Start Prometheus HTTP server
    prometheus_port = 8001
    start_http_server(prometheus_port)
    print(f"Prometheus metrics server started: http://localhost:{prometheus_port}")

    # Create central metrics class
    metrics = YouTubeMetrics()

    # Stream settings to monitor
    streams = [
        {
            'name': 'CHANNEL-1',
            'channel_name': 'TEST_Master',
            'channel_id': 'XXXXXXXXXXXXXXXXXXXXXXXXXXX',
            'video_id': 'XXXXXXXXXXX',
            'api_key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_O-U',
            'environment': 'Production'
        },
        {
            'name': 'CHANNEL-2',
            'channel_name': 'TEST_Backup',
            'channel_id': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX',
            'video_id': 'XXXXXXXXXXXX',
            'api_key': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX_O-U',
            'environment': 'Production'
        }
    ]

    print(f"Monitoring a total of {len(streams)} streams...")

    # Start separate thread for each stream
    threads = []
    try:
        for stream in streams:
            thread = threading.Thread(target=run_monitor, args=(stream, metrics, 30))
            thread.daemon = True
            thread.start()
            threads.append(thread)

            # Wait 1 second between threads to distribute API calls
            time.sleep(1)

        # For the main thread to wait for other threads
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    main()
