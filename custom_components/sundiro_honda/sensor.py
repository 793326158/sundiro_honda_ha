"""Sensor platform for Sundiro Honda."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfLength,
    UnitOfPressure,
    UnitOfTime,
)
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
    """Set up Sundiro Honda sensors."""
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

        # 为每辆车创建传感器
        entities.extend([
            SundiroHondaFuelSensor(coordinator, vehicle),
            SundiroHondaMileageSensor(coordinator, vehicle),
            SundiroHondaTirePressureSensor(coordinator, vehicle, "front"),
            SundiroHondaTirePressureSensor(coordinator, vehicle, "rear"),
            SundiroHondaUnreadSensor(coordinator, vehicle),
            SundiroHondaServiceDaysSensor(coordinator, vehicle),
        ])

    async_add_entities(entities)

class SundiroHondaBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor for Sundiro Honda."""

    def __init__(
        self,
        coordinator: SundiroHondaCoordinator,
        vehicle: dict,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.vehicle = vehicle
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{vehicle['vehicleCode']}_{sensor_type}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vehicle["vehicleCode"])},
            name=vehicle.get("vehicleNick", "Sundiro Vehicle"),
            manufacturer="Sundiro Honda",
            model=vehicle.get("vehicleModelSeries", "Unknown"),
            sw_version=vehicle.get("deviceBlueName", "Unknown"),
        )

class SundiroHondaFuelSensor(SundiroHondaBaseSensor):
    """Fuel level sensor."""

    def __init__(self, coordinator, vehicle):
        """Initialize fuel sensor."""
        super().__init__(coordinator, vehicle, "fuel")
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} Fuel"
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the native value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            # 假设从status中获取油量百分比
            return self.coordinator.data["status"].get("fuelPercent")
        return None

class SundiroHondaMileageSensor(SundiroHondaBaseSensor):
    """Total mileage sensor."""

    def __init__(self, coordinator, vehicle):
        """Initialize mileage sensor."""
        super().__init__(coordinator, vehicle, "mileage")
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} Mileage"
        self._attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        """Return the native value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            return self.coordinator.data["status"].get("totalMileage")
        return None

class SundiroHondaTirePressureSensor(SundiroHondaBaseSensor):
    """Tire pressure sensor."""

    def __init__(self, coordinator, vehicle, position):
        """Initialize tire pressure sensor."""
        super().__init__(coordinator, vehicle, f"tire_{position}")
        self.position = position
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} {position.title()} Tire Pressure"
        self._attr_native_unit_of_measurement = UnitOfPressure.KPA
        self._attr_device_class = SensorDeviceClass.PRESSURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the native value."""
        if self.coordinator.data and "tire" in self.coordinator.data:
            tire_data = self.coordinator.data["tire"]
            if self.position == "front":
                return tire_data.get("frontTirePressure")
            else:
                return tire_data.get("rearTirePressure")
        return None

class SundiroHondaUnreadSensor(SundiroHondaBaseSensor):
    """Unread messages sensor."""

    def __init__(self, coordinator, vehicle):
        """Initialize unread sensor."""
        super().__init__(coordinator, vehicle, "unread")
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} Unread Messages"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the native value."""
        if self.coordinator.data:
            return self.coordinator.data.get("unread", 0)
        return 0

class SundiroHondaServiceDaysSensor(SundiroHondaBaseSensor):
    """Service days remaining sensor."""

    def __init__(self, coordinator, vehicle):
        """Initialize service days sensor."""
        super().__init__(coordinator, vehicle, "service_days")
        self._attr_name = f"{vehicle.get('vehicleNick', 'Vehicle')} Service Days"
        self._attr_native_unit_of_measurement = UnitOfTime.DAYS
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the native value."""
        if self.coordinator.data and "status" in self.coordinator.data:
            return self.coordinator.data["status"].get("expirationServerDays")
        return None
