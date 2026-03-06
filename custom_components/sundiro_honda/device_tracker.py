"""Device tracker platform for Sundiro Honda."""
from homeassistant.components.device_tracker.config_entry import TrackerEntity
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
    """Set up Sundiro Honda device trackers."""
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
            SundiroHondaDeviceTracker(coordinator, vehicle)
        )

    async_add_entities(entities)

class SundiroHondaDeviceTracker(CoordinatorEntity, TrackerEntity):
    """Representation of a Sundiro Honda device tracker."""

    def __init__(
        self,
        coordinator: SundiroHondaCoordinator,
        vehicle: dict,
    ) -> None:
        """Initialize the tracker."""
        super().__init__(coordinator)
        self.vehicle = vehicle
        self.vehicle_code = vehicle["vehicleCode"]
        self._attr_unique_id = f"{self.vehicle_code}_tracker"
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} Location"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.vehicle_code)},
            name=vehicle.get("vehicleNick", "Sundiro Vehicle"),
            manufacturer="Sundiro Honda",
            model=vehicle.get("vehicleModelSeries", "Unknown"),
        )

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        if self.coordinator.data and "gps" in self.coordinator.data:
            return self.coordinator.data["gps"].get("latitude")
        return None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        if self.coordinator.data and "gps" in self.coordinator.data:
            return self.coordinator.data["gps"].get("longitude")
        return None

    @property
    def source_type(self) -> str:
        """Return the source type of the device."""
        return "gps"

    @property
    def icon(self) -> str:
        """Return the icon."""
        return "mdi:motorbike"
