"""Sensor platform for Athletic Fitness BG integration."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import AthleticFitnessBGCoordinator
from .models import GymDetails


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    assert entry.runtime_data is not None
    coordinator: AthleticFitnessBGCoordinator = entry.runtime_data

    async_add_entities(PeopleInGymSensor(coordinator, gym) for gym in coordinator.gyms)


class PeopleInGymSensor(CoordinatorEntity[AthleticFitnessBGCoordinator], SensorEntity):
    """Representation of a people-count sensor for a selected gym."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "people"

    def __init__(
        self, coordinator: AthleticFitnessBGCoordinator, gym: GymDetails
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._gym = gym
        config_entry = coordinator.config_entry
        assert config_entry is not None
        self._attr_name = f"{gym.city} - {gym.gym_name}"
        self._attr_unique_id = f"{config_entry.entry_id}_gym_{gym.gym_id}"

    @property
    def available(self) -> bool:
        """Return if the entity is available."""
        if not super().available or self.coordinator.data is None:
            return False
        return any(gym.gym_id == self._gym.gym_id for gym in self.coordinator.data)

    @property
    def native_value(self) -> int | None:
        """Return the current people count for this gym."""
        if self.coordinator.data is None:
            return None
        matching_gyms = [
            gym for gym in self.coordinator.data if gym.gym_id == self._gym.gym_id
        ]
        return matching_gyms[0].people_count if matching_gyms else None
