"""Tests for the Athletic Fitness BG sensor platform."""

from __future__ import annotations

from unittest.mock import Mock

from custom_components.athletic_fitness_bg.const import DOMAIN
from custom_components.athletic_fitness_bg.coordinator import AthleticFitnessBGCoordinator
from custom_components.athletic_fitness_bg.models import GymDetails
from custom_components.athletic_fitness_bg.sensor import PeopleInGymSensor, async_setup_entry
from pytest_homeassistant_custom_component.common import MockConfigEntry


def _create_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "email": "test@example.com",
            "password": "test_password",
            "gyms": [
                {"gym_id": 1, "gym_name": "Mladost", "city": "Sofia"},
                {"gym_id": 2, "gym_name": "Center", "city": "Plovdiv"},
            ],
        },
    )


async def test_async_setup_entry_adds_one_sensor_per_configured_gym(hass) -> None:
    """Sensor setup should create an entity for each configured gym."""
    entry = _create_entry()
    coordinator = AthleticFitnessBGCoordinator(hass, entry)
    entry.runtime_data = coordinator
    added_entities = []

    def _add_entities(entities) -> None:
        added_entities.extend(list(entities))

    await async_setup_entry(hass, entry, _add_entities)

    assert len(added_entities) == 2
    assert all(isinstance(entity, PeopleInGymSensor) for entity in added_entities)


async def test_sensor_uses_latest_coordinator_data_for_value_and_availability(hass) -> None:
    """The entity should resolve its state from the coordinator's latest data."""
    entry = _create_entry()
    coordinator = AthleticFitnessBGCoordinator(hass, entry)
    coordinator.data = [
        GymDetails(gym_id=1, gym_name="Mladost", city="Sofia", people_count=19)
    ]
    sensor = PeopleInGymSensor(coordinator, coordinator.gyms[0])

    assert sensor.available is True
    assert sensor.native_value == 19
    assert sensor.name == "Sofia - Mladost"
    assert sensor.unique_id == f"{entry.entry_id}_gym_1"
    assert sensor.device_info["identifiers"] == {(DOMAIN, entry.entry_id)}


async def test_sensor_is_unavailable_when_gym_missing_from_latest_data(hass) -> None:
    """The entity should become unavailable if its gym is not present in coordinator data."""
    entry = _create_entry()
    coordinator = AthleticFitnessBGCoordinator(hass, entry)
    coordinator.data = [
        GymDetails(gym_id=999, gym_name="Other", city="Varna", people_count=3)
    ]
    sensor = PeopleInGymSensor(coordinator, coordinator.gyms[0])

    assert sensor.available is False
    assert sensor.native_value is None