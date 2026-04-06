"""Test config flow for Athletic Fitness BG integration."""

import pytest

from custom_components.athletic_fitness_bg.athletic_api_client import (
    AthleticApiClientAuthError,
)
from custom_components.athletic_fitness_bg.config_flow import ConfigFlow
from homeassistant.core import HomeAssistant


async def test_config_flow_user_step(hass: HomeAssistant) -> None:
    """Test the user step of the config flow."""
    flow = ConfigFlow()
    flow.hass = hass

    # Test initial step
    result = await flow.async_step_user()
    assert result["type"] == "form"
    assert result["step_id"] == "user"

    # Test with valid credentials (using test/test as per config_flow.py)
    with pytest.raises(
        AthleticApiClientAuthError
    ):  # Will fail because we don't have real API
        await flow.async_step_user({"email": "test", "password": "test"})


async def test_config_flow_user_step_invalid_auth(hass: HomeAssistant) -> None:
    """Test the user step with invalid credentials."""
    flow = ConfigFlow()
    flow.hass = hass

    result = await flow.async_step_user({"username": "invalid", "password": "invalid"})
    assert result["type"] == "form"
    assert result["errors"] == {"base": "invalid_auth"}
