"""Test config flow for Athletic Fitness BG integration."""

from unittest.mock import AsyncMock, patch

from custom_components.athletic_fitness_bg.athletic_api_client import (
    AthleticApiClient,
    AthleticApiClientAuthError,
)
from custom_components.athletic_fitness_bg.config_flow import ConfigFlow
from custom_components.athletic_fitness_bg.const import DOMAIN

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_config_flow_user_step(hass: HomeAssistant) -> None:
    """Test the user step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with (
        patch.object(ConfigFlow, "_test_credentials", AsyncMock(return_value=None)),
        patch.object(
            AthleticApiClient,
            "get_gyms",
            AsyncMock(
                return_value=[{"gymId": 1, "gymName": "Test Gym", "city": "Sofia"}]
            ),
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"email": "test", "password": "test"}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "location"


async def test_config_flow_user_step_invalid_auth(hass: HomeAssistant) -> None:
    """Test the user step with invalid credentials."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch.object(
        ConfigFlow,
        "_test_credentials",
        AsyncMock(side_effect=AthleticApiClientAuthError("Invalid credentials")),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"email": "invalid", "password": "invalid"}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "invalid_auth"}
