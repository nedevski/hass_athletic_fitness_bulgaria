"""The Athletic Fitness BG integration."""

from __future__ import annotations

import logging

from homeassistant import config_entries
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from . import coordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Set up Athletic Fitness BG from a config entry."""
    try:
        coord = coordinator.AthleticFitnessBGCoordinator(hass, entry)
        await coord.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Failed to initialize coordinator: {err}") from err

    entry.runtime_data = coord
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
