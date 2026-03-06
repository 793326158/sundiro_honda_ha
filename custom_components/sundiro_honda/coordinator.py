"""Data update coordinator for Sundiro Honda."""
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SundiroHondaApi
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class SundiroHondaCoordinator(DataUpdateCoordinator):
    """Class to manage fetching vehicle data."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SundiroHondaApi,
        vehicle_code: str,
    ) -> None:
        """Initialize."""
        self.api = api
        self.vehicle_code = vehicle_code

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{vehicle_code}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        try:
            # 获取车辆状态
            status = await self.api.get_vehicle_status(self.vehicle_code)
            # 获取GPS位置
            gps = await self.api.get_last_gps(self.vehicle_code)
            # 获取胎压
            tire = await self.api.get_tire_pressure(self.vehicle_code)
            # 获取未读消息数
            unread = await self.api.get_unread_messages()

            return {
                "status": status,
                "gps": gps,
                "tire": tire,
                "unread": unread,
            }
        except Exception as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
