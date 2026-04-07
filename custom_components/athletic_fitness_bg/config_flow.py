"""Config flow for Athletic Fitness BG integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow as ConfigEntriesFlow,
    ConfigFlowResult,
)
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

from .athletic_api_client import (
    AthleticApiClient,
    AthleticApiClientAuthError,
    AthleticApiClientError,
)
from .const import DOMAIN, MAX_GYMS
from .models import GymDetails

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("email"): str,
        vol.Required("password"): str,
    }
)


class ConfigFlow(ConfigEntriesFlow, domain=DOMAIN):
    """Handle a config flow for Athletic Fitness BG."""

    VERSION = 1

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the config flow."""
        super().__init__(*args, **kwargs)
        self._user_data: dict[str, Any] = {}
        self._available_gyms: dict[int, GymDetails] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        # Check for existing instance
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await self._test_credentials(
                    user_input["email"], user_input["password"]
                )
            except AthleticApiClientAuthError:
                errors["base"] = "invalid_auth"
            except AthleticApiClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Store user data and proceed to location selection
                self._user_data = user_input
                return await self.async_step_location()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the location selection step."""
        if user_input is not None:
            if len(user_input["gym_ids"]) > MAX_GYMS:
                return await self._show_gym_selection_form(
                    "location",
                    user_input["gym_ids"],
                    {"base": "max_gyms_selected"},
                )

            selected_gyms = self._selected_gyms_from_input(user_input)
            config_data = {**self._user_data, "gyms": self._serialize_gyms(selected_gyms)}

            return self.async_create_entry(
                title="Athletic Fitness",
                data=config_data,
            )

        return await self._show_gym_selection_form("location")

    async def _test_credentials(self, email: str, password: str) -> None:
        """Test if the provided credentials are valid."""
        client = AthleticApiClient(self.hass)
        await client.authenticate(email, password)

    async def _show_gym_selection_form(
        self,
        step_id: str,
        default_gym_ids: list[str] | None = None,
        errors: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        """Show the gym selection form."""
        # Fetch available gyms
        client = AthleticApiClient(self.hass)
        try:
            gyms = await client.get_gyms()
        except AthleticApiClientError as err:
            _LOGGER.error("Error fetching gyms: %s", err)
            if step_id == "location":
                return self.async_show_form(
                    step_id=step_id,
                    data_schema=vol.Schema({}),
                    errors={"base": "cannot_fetch_gyms"},
                )
            return self.async_abort(reason="cannot_fetch_gyms")

        self._available_gyms = {
            gym["gymId"]: GymDetails(
                gym_id=gym["gymId"],
                gym_name=gym["gymName"],
                city=gym["city"],
            )
            for gym in gyms
        }

        # Create dynamic schema with gym options
        options: list[SelectOptionDict] = [
            SelectOptionDict(
                value=str(gym.gym_id), label=f"{gym.city} - {gym.gym_name}"
            )
            for gym in self._available_gyms.values()
        ]

        schema = vol.Schema(
            {
                vol.Required("gym_ids", default=default_gym_ids or []): SelectSelector(
                    SelectSelectorConfig(
                        options=options,
                        multiple=True,
                        translation_key="gym_ids",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id=step_id,
            data_schema=schema,
            errors=errors,
            description_placeholders={"max_gyms": str(MAX_GYMS)},
        )

    def _selected_gyms_from_input(self, user_input: dict[str, Any]) -> list[GymDetails]:
        """Return selected gym models from submitted form input."""
        selected_gym_ids = [int(gym_id) for gym_id in user_input["gym_ids"]]
        return [self._available_gyms[gym_id] for gym_id in selected_gym_ids]

    @staticmethod
    def _serialize_gyms(gyms: list[GymDetails]) -> list[dict[str, Any]]:
        """Serialize gym details for storage in config entry data."""
        return [
            {"gym_id": gym.gym_id, "gym_name": gym.gym_name, "city": gym.city}
            for gym in gyms
        ]

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a reconfigure flow to change gym selection."""
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        if not config_entry:
            return self.async_abort(reason="reconfigure_failed")

        if user_input is not None:
            if len(user_input["gym_ids"]) > MAX_GYMS:
                return await self._show_gym_selection_form(
                    "reconfigure",
                    user_input["gym_ids"],
                    {"base": "max_gyms_selected"},
                )

            selected_gyms = self._selected_gyms_from_input(user_input)
            updated_data = {
                **config_entry.data,
                "gyms": self._serialize_gyms(selected_gyms),
            }

            self.hass.config_entries.async_update_entry(config_entry, data=updated_data)
            await self.hass.config_entries.async_reload(config_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")

        # Get currently selected gyms for prepopulation
        current_gyms = config_entry.data.get("gyms", [])
        current_gym_ids = [str(gym["gym_id"]) for gym in current_gyms]

        return await self._show_gym_selection_form("reconfigure", current_gym_ids)
