"""Integration constants."""

from .lib.protocol import ZS800J, ZS821J

DOMAIN = "jomoo_ble"
DEFAULT_PREFIX = "JOMOO_SMART_"
MANUFACTURER = "JOMOO"

CONF_MODEL = "model"
MODELS = {"237369": ZS800J, "294180": ZS821J}

CONF_NAME_PREFIX = "name_prefix"
CONF_ENABLE_STATUS_STREAM = "enable_status_stream"
CONF_ENABLE_CONTROLS = "enable_controls"
CONF_ENABLE_EXPERIMENTAL = "enable_experimental"
CONF_POLL_INTERVAL = "poll_interval"
DEFAULT_POLL_INTERVAL = 0  # 0 = never poll; every connection makes the toilet beep
MIN_POLL_INTERVAL = 300
MAX_POLL_INTERVAL = 86400

SERVICE_REFRESH = "refresh"

STORAGE_VERSION = 1
