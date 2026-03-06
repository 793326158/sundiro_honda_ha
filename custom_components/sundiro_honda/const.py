"""Constants for the Sundiro Honda integration."""
DOMAIN = "sundiro_honda"
CONF_TOKEN = "token"
CONF_VEHICLE_CODE = "vehicle_code"

# API endpoints
API_BASE = "https://crmlot-app.honda-sundiro.com/app/api"
API_LOGIN = "/login"
API_VEHICLE_LIST = "/vehicle/v1/garage"
API_VEHICLE_STATUS = "/vehicle/v1/status/{vehicle_code}"
API_VEHICLE_CONTROL = "/vehicle/v1/control/{vehicle_code}"
API_VEHICLE_FIND = "/vehicle/v1/find/{vehicle_code}"
API_VEHICLE_LAST_GPS = "/vehicle/v1/lastGps/{vehicle_code}"
API_TIRE_PRESSURE = "/vehicle/v1/tirePressure/{vehicle_code}"
API_MESSAGE_UNREAD = "/message/unreadNumber"

# Default headers
DEFAULT_HEADERS = {
    "User-Agent": "Dart/3.5 (dart:io)",
    "language": "zh_CN",
    "apptype": "2",
    "Content-Type": "application/json"
}

# Update interval (seconds)
UPDATE_INTERVAL = 300  # 5 minutes
