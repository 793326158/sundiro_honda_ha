"""Init for Sundiro Honda integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client  # 替换 helpers 的导入方式

from .api import SundiroHondaApi
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR, Platform.LOCK, Platform.BUTTON, Platform.DEVICE_TRACKER]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sundiro Honda from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # 正确获取 clientsession 的方式
    session = aiohttp_client.async_get_clientsession(hass)
    api = SundiroHondaApi(entry.data["token"], session)

    # 获取车辆列表
    vehicles = await api.get_vehicles()
    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "vehicles": vehicles,
    }

    # 设置平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
