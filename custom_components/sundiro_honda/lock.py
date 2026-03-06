"""Lock platform for Sundiro Honda."""
from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SundiroHondaCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Sundiro Honda locks."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    vehicles = entry_data["vehicles"]

    entities = []
    for vehicle in vehicles:
        coordinator = SundiroHondaCoordinator(
            hass,
            entry_data["api"],
            vehicle["vehicleCode"],
        )
        await coordinator.async_config_entry_first_refresh()

        entities.append(
            SundiroHondaLock(coordinator, vehicle)
        )

    async_add_entities(entities)

class SundiroHondaLock(CoordinatorEntity, LockEntity):
    """Representation of a Sundiro Honda lock."""

    def __init__(
        self,
        coordinator: SundiroHondaCoordinator,
        vehicle: dict,
    ) -> None:
        """Initialize the lock."""
        super().__init__(coordinator)
        self.vehicle = vehicle
        self.vehicle_code = vehicle["vehicleCode"]
        self._attr_unique_id = f"{self.vehicle_code}_lock"
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} Lock"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.vehicle_code)},
            name=vehicle.get("vehicleNick", "Sundiro Vehicle"),
            manufacturer="Sundiro Honda",
            model=vehicle.get("vehicleModelSeries", "Unknown"),
        )

    @property
    def is_locked(self) -> bool | None:
        """Return true if the lock is locked."""
        if self.coordinator.data and "status" in self.coordinator.data:
            # 根据实际返回的字段判断锁状态
            return not self.coordinator.data["status"].get("isLock", True)
        return None

    async def async_lock(self, **kwargs):
        """Lock the vehicle."""
        api = self.coordinator.api
        success = await api.lock_vehicle(self.vehicle_code)
        if success:
            await self.coordinator.async_refresh()

    async def async_unlock(self, **kwargs):
        """Unlock the vehicle."""
        api = self.coordinator.api
        success = await api.unlock_vehicle(self.vehicle_code)
        if success:
            await self.coordinator.async_refresh()
