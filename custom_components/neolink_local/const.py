"""Constants for the Neolink Local integration."""

from datetime import timedelta

DOMAIN = "neolink_local"

CONF_API_PORT = "api_port"
CONF_RTSP_HOST = "rtsp_host"
CONF_STREAM = "stream"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_API_PORT = 8559
DEFAULT_STREAM = "main"
STREAMS = ["main", "sub", "extern"]

SCAN_INTERVAL = timedelta(seconds=10)
REQUEST_TIMEOUT = 10
