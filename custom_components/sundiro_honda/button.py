"""Button platform for Sundiro Honda."""
from homeassistant.components.button import ButtonEntity
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
    """Set up Sundiro Honda buttons."""
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
            SundiroHondaFindButton(coordinator, vehicle)
        )

    async_add_entities(entities)

class SundiroHondaFindButton(CoordinatorEntity, ButtonEntity):
    """Find vehicle button (flash lights and honk)."""

    def __init__(
        self,
        coordinator: SundiroHondaCoordinator,
        vehicle: dict,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.vehicle = vehicle
        self.vehicle_code = vehicle["vehicleCode"]
        self._attr_unique_id = f"{self.vehicle_code}_find"
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} Find"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.vehicle_code)},
            name=vehicle.get("vehicleNick", "Sundiro Vehicle"),
            manufacturer="Sundiro Honda",
            model=vehicle.get("vehicleModelSeries", "Unknown"),
        )

    async def async_press(self) -> None:
        """Press the button to find the vehicle."""
        api = self.coordinator.api
        await api.find_vehicle(self.vehicle_code)
