"""Data coordinator for Athletic Fitness BG integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import cast

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .athletic_api_client import AthleticApiClient, AthleticApiClientError
from .const import DOMAIN
from .models import GymDetails

_LOGGER = logging.getLogger(__name__)

type AthleticFitnessBGConfigEntry = config_entries.ConfigEntry[
    "AthleticFitnessBGCoordinator"
]


class AthleticFitnessBGCoordinator(DataUpdateCoordinator[list[GymDetails]]):
    """Data coordinator for Athletic Fitness BG."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: AthleticFitnessBGConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=5),
        )
        self.email = config_entry.data["email"]
        self.password = config_entry.data["password"]
        self.gyms = self._build_gym_details(config_entry)

    def _build_gym_details(
        self, config_entry: config_entries.ConfigEntry
    ) -> list[GymDetails]:
        """Build gym detail objects from config entry data."""
        gyms_data = config_entry.data["gyms"]
        return [
            GymDetails(gym_id=gym["gym_id"], gym_name=gym["gym_name"], city=gym["city"])
            for gym in gyms_data
        ]

    async def _async_update_data(self) -> list[GymDetails]:
        """Fetch data from the API."""
        if not self.gyms:
            return []

        client = AthleticApiClient(self.hass)
        try:
            await client.authenticate(self.email, self.password)
            results = await asyncio.gather(
                *(client.get_people_count(gym.gym_id) for gym in self.gyms),
                return_exceptions=True,
            )
        except AthleticApiClientError as err:
            raise UpdateFailed(f"Error fetching people counts: {err}") from err

        for gym, result in zip(self.gyms, results, strict=False):
            if isinstance(result, Exception):
                raise UpdateFailed(
                    f"Error fetching people count for gym {gym.gym_id}: {result}"
                ) from result
            gym.people_count = cast(int, result)

        return self.gyms
