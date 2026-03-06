"""API client for Sundiro Honda."""
import logging
import async_timeout
from typing import Any, Dict, List, Optional

import aiohttp

from .const import (
    API_BASE, API_VEHICLE_LIST, API_VEHICLE_STATUS,
    API_VEHICLE_CONTROL, API_VEHICLE_FIND, API_VEHICLE_LAST_GPS,
    API_TIRE_PRESSURE, API_MESSAGE_UNREAD, DEFAULT_HEADERS
)

_LOGGER = logging.getLogger(__name__)

class SundiroHondaApi:
    """API client for Sundiro Honda."""

    def __init__(self, token: str, session: aiohttp.ClientSession):
        self.token = token
        self.session = session
        self.headers = {**DEFAULT_HEADERS, "authorization": f"Bearer {token}"}

    async def _request(
        self, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Make a request to the API."""
        kwargs.setdefault("headers", self.headers)
        try:
            async with async_timeout.timeout(10):
                resp = await self.session.request(method, url, **kwargs)
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientResponseError as err:
            _LOGGER.error(
                "HTTP error %s from %s: %s", err.status, url, err.message
            )
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Request error for %s: %s", url, err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error for %s: %s", url, err)
            raise

    async def get_vehicles(self) -> List[Dict[str, Any]]:
        """Get list of vehicles."""
        url = f"{API_BASE}{API_VEHICLE_LIST}"
        data = await self._request("GET", url)
        return data.get("data", [])

    async def get_vehicle_status(self, vehicle_code: str) -> Dict[str, Any]:
        """Get real-time status of a vehicle."""
        url = f"{API_BASE}{API_VEHICLE_STATUS.format(vehicle_code=vehicle_code)}"
        data = await self._request("GET", url)
        return data.get("data", {})

    async def lock_vehicle(self, vehicle_code: str) -> bool:
        """Lock the vehicle."""
        url = f"{API_BASE}{API_VEHICLE_CONTROL.format(vehicle_code=vehicle_code)}"
        data = await self._request("POST", url, json={"action": "lock"})
        return data.get("code") == 200

    async def unlock_vehicle(self, vehicle_code: str) -> bool:
        """Unlock the vehicle."""
        url = f"{API_BASE}{API_VEHICLE_CONTROL.format(vehicle_code=vehicle_code)}"
        data = await self._request("POST", url, json={"action": "unlock"})
        return data.get("code") == 200

    async def find_vehicle(self, vehicle_code: str) -> bool:
        """Flash lights and honk to find vehicle."""
        url = f"{API_BASE}{API_VEHICLE_FIND.format(vehicle_code=vehicle_code)}"
        data = await self._request("POST", url)
        return data.get("code") == 200

    async def get_last_gps(self, vehicle_code: str) -> Dict[str, Any]:
        """Get last known GPS location."""
        url = f"{API_BASE}{API_VEHICLE_LAST_GPS.format(vehicle_code=vehicle_code)}"
        data = await self._request("GET", url)
        return data.get("data", {})

    async def get_tire_pressure(self, vehicle_code: str) -> Dict[str, Any]:
        """Get tire pressure data."""
        url = f"{API_BASE}{API_TIRE_PRESSURE.format(vehicle_code=vehicle_code)}"
        data = await self._request("GET", url)
        return data.get("data", {})

    async def get_unread_messages(self) -> int:
        """Get number of unread messages."""
        url = f"{API_BASE}{API_MESSAGE_UNREAD}"
        data = await self._request("GET", url)
        return data.get("data", 0)
