"""Test config flow for Athletic Fitness BG integration."""

from unittest.mock import AsyncMock, patch

from custom_components.athletic_fitness_bg.athletic_api_client import (
    AthleticApiClient,
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

    # Test with valid credentials and mocked gym list
    with patch.object(ConfigFlow, "_test_credentials", AsyncMock(return_value=None)), patch.object(
        AthleticApiClient,
        "get_gyms",
        AsyncMock(
            return_value=[{"gymId": 1, "gymName": "Test Gym", "city": "Sofia"}]
        ),
    ):
        result = await flow.async_step_user({"email": "test", "password": "test"})

    assert result["type"] == "form"
    assert result["step_id"] == "location"


async def test_config_flow_user_step_invalid_auth(hass: HomeAssistant) -> None:
    """Test the user step with invalid credentials."""
    flow = ConfigFlow()
    flow.hass = hass

    with patch.object(
        ConfigFlow,
        "_test_credentials",
        AsyncMock(side_effect=AthleticApiClientAuthError("Invalid credentials")),
    ):
        result = await flow.async_step_user({"email": "invalid", "password": "invalid"})

    assert result["type"] == "form"
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "invalid_auth"}
