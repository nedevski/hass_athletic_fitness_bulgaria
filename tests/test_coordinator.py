"""Tests for the Athletic Fitness BG data coordinator."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from custom_components.athletic_fitness_bg.athletic_api_client import (
    AthleticApiClientError,
)
from custom_components.athletic_fitness_bg.const import DOMAIN
from custom_components.athletic_fitness_bg.coordinator import AthleticFitnessBGCoordinator
from custom_components.athletic_fitness_bg.models import GymDetails
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry


def _create_entry(gyms: list[dict] | None = None) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            "email": "test@example.com",
            "password": "test_password",
            "gyms": gyms if gyms is not None else [],
        },
    )


async def test_async_update_data_returns_empty_list_when_no_gyms(hass) -> None:
    """The coordinator should not call the API when nothing is configured."""
    entry = _create_entry()
    coordinator = AthleticFitnessBGCoordinator(hass, entry)

    result = await coordinator._async_update_data()

    assert result == []


async def test_async_update_data_updates_people_counts(hass) -> None:
    """Successful coordinator refreshes should update each configured gym."""
    entry = _create_entry(
        [
            {"gym_id": 1, "gym_name": "Mladost", "city": "Sofia"},
            {"gym_id": 2, "gym_name": "Center", "city": "Plovdiv"},
        ]
    )
    coordinator = AthleticFitnessBGCoordinator(hass, entry)

    client = AsyncMock()
    client.authenticate = AsyncMock(return_value={})
    client.get_people_count = AsyncMock(side_effect=[7, 12])

    with patch(
        "custom_components.athletic_fitness_bg.coordinator.AthleticApiClient",
        return_value=client,
    ):
        result = await coordinator._async_update_data()

    assert result == [
        GymDetails(gym_id=1, gym_name="Mladost", city="Sofia", people_count=7),
        GymDetails(gym_id=2, gym_name="Center", city="Plovdiv", people_count=12),
    ]
    client.authenticate.assert_awaited_once_with("test@example.com", "test_password")


async def test_async_update_data_raises_when_authentication_fails(hass) -> None:
    """Authentication failures should be surfaced as coordinator update failures."""
    entry = _create_entry(
        [{"gym_id": 1, "gym_name": "Mladost", "city": "Sofia"}]
    )
    coordinator = AthleticFitnessBGCoordinator(hass, entry)

    client = AsyncMock()
    client.authenticate = AsyncMock(side_effect=AthleticApiClientError("boom"))

    with patch(
        "custom_components.athletic_fitness_bg.coordinator.AthleticApiClient",
        return_value=client,
    ):
        with pytest.raises(UpdateFailed, match="Error fetching people counts"):
            await coordinator._async_update_data()


async def test_async_update_data_raises_when_one_gym_update_fails(hass) -> None:
    """A failed gym count fetch should fail the full refresh with the gym id."""
    entry = _create_entry(
        [{"gym_id": 9, "gym_name": "Mladost", "city": "Sofia"}]
    )
    coordinator = AthleticFitnessBGCoordinator(hass, entry)

    client = AsyncMock()
    client.authenticate = AsyncMock(return_value={})
    client.get_people_count = AsyncMock(side_effect=RuntimeError("bad payload"))

    with patch(
        "custom_components.athletic_fitness_bg.coordinator.AthleticApiClient",
        return_value=client,
    ):
        with pytest.raises(UpdateFailed, match="gym 9"):
            await coordinator._async_update_data()