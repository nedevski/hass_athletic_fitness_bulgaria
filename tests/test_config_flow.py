"""Test config flow for Athletic Fitness BG integration."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from custom_components.athletic_fitness_bg.athletic_api_client import (
    AthleticApiClient,
    AthleticApiClientAuthError,
)
from custom_components.athletic_fitness_bg.config_flow import ConfigFlow
from custom_components.athletic_fitness_bg.const import DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from tests.common import MockConfigEntry

GYM_LIST = [
    {"gymId": 1, "gymName": "Mladost", "city": "Sofia"},
    {"gymId": 2, "gymName": "Center", "city": "Plovdiv"},
]

GYM_LIST_OVER_LIMIT = [
    {"gymId": 1, "gymName": "Mladost", "city": "Sofia"},
    {"gymId": 2, "gymName": "Center", "city": "Plovdiv"},
    {"gymId": 3, "gymName": "Arena", "city": "Varna"},
    {"gymId": 4, "gymName": "Park", "city": "Burgas"},
    {"gymId": 5, "gymName": "South", "city": "Ruse"},
    {"gymId": 6, "gymName": "North", "city": "Pleven"},
]


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
            AsyncMock(return_value=GYM_LIST),
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"email": "test_email@example.com", "password": "test_password"}
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "location"


async def test_config_flow_location_creates_entry(hass: HomeAssistant) -> None:
    """Test creating an entry after selecting locations."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with (
        patch.object(ConfigFlow, "_test_credentials", AsyncMock(return_value=None)),
        patch.object(AthleticApiClient, "get_gyms", AsyncMock(return_value=GYM_LIST)),
    ):
        location_step = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"email": "test@example.com", "password": "password"}
        )
        result = await hass.config_entries.flow.async_configure(
            location_step["flow_id"], {"gym_ids": ["1", "2"]}
        )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Athletic Fitness"
    assert result["data"]["email"] == "test@example.com"
    assert result["data"]["password"] == "password"
    assert result["data"]["gyms"] == [
        {"gym_id": 1, "gym_name": "Mladost", "city": "Sofia"},
        {"gym_id": 2, "gym_name": "Center", "city": "Plovdiv"},
    ]


async def test_config_flow_reconfigure_updates_selected_gyms(
    hass: HomeAssistant,
) -> None:
    """Test reconfigure updates selected gyms and reloads the entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "email": "test@example.com",
            "password": "password",
            "gyms": [{"gym_id": 1, "gym_name": "Mladost", "city": "Sofia"}],
        },
    )
    entry.add_to_hass(hass)

    with (
        patch.object(AthleticApiClient, "get_gyms", AsyncMock(return_value=GYM_LIST)),
        patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload,
    ):
        reconfigure_step = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        result = await hass.config_entries.flow.async_configure(
            reconfigure_step["flow_id"], {"gym_ids": ["2"]}
        )

    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data["gyms"] == [
        {"gym_id": 2, "gym_name": "Center", "city": "Plovdiv"}
    ]
    mock_reload.assert_awaited_once_with(entry.entry_id)


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


async def test_config_flow_location_step_rejects_more_than_five_gyms(
    hass: HomeAssistant,
) -> None:
    """Test selecting more than 5 gyms shows an error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with (
        patch.object(ConfigFlow, "_test_credentials", AsyncMock(return_value=None)),
        patch.object(
            AthleticApiClient, "get_gyms", AsyncMock(return_value=GYM_LIST_OVER_LIMIT)
        ),
    ):
        location_step = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"email": "test@example.com", "password": "test_password"}
        )
        result = await hass.config_entries.flow.async_configure(
            location_step["flow_id"],
            {"gym_ids": ["1", "2", "3", "4", "5", "6"]},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "location"
    assert result["errors"] == {"base": "max_gyms_selected"}


async def test_config_flow_reconfigure_rejects_more_than_five_gyms(
    hass: HomeAssistant,
) -> None:
    """Test reconfigure rejects selecting more than 5 gyms."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "email": "test@example.com",
            "password": "password",
            "gyms": [{"gym_id": 1, "gym_name": "Mladost", "city": "Sofia"}],
        },
    )
    entry.add_to_hass(hass)

    with (
        patch.object(
            AthleticApiClient, "get_gyms", AsyncMock(return_value=GYM_LIST_OVER_LIMIT)
        ),
        patch.object(
            hass.config_entries,
            "async_reload",
            AsyncMock(return_value=True),
        ) as mock_reload,
    ):
        reconfigure_step = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={
                "source": config_entries.SOURCE_RECONFIGURE,
                "entry_id": entry.entry_id,
            },
        )
        result = await hass.config_entries.flow.async_configure(
            reconfigure_step["flow_id"],
            {"gym_ids": ["1", "2", "3", "4", "5", "6"]},
        )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    assert result["errors"] == {"base": "max_gyms_selected"}
    assert entry.data["gyms"] == [{"gym_id": 1, "gym_name": "Mladost", "city": "Sofia"}]
    mock_reload.assert_not_awaited()
