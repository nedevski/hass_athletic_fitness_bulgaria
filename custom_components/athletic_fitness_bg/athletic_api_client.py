"""API client for Athletic Fitness BG."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

_LOGGER = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "https://mobileapiathletic.gymrealm.com"
API_ENDPOINT_LOGIN = "/api/Login"
API_ENDPOINT_GET_GYMS = "/api/GetGyms"
API_ENDPOINT_GET_PEOPLE_COUNT = "/api/GetPeopleInTheGymCount"


class AthleticApiClientError(HomeAssistantError):
    """Base exception for Athletic API client errors."""


class AthleticApiClientAuthError(AthleticApiClientError):
    """Exception raised when authentication fails."""


class AthleticApiClient:
    """API client for Athletic Fitness BG."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the API client."""
        self.hass = hass
        self.session = aiohttp_client.async_get_clientsession(hass)
        self._access_token: str | None = None
        self._token_expiry: datetime | None = None

    def _is_token_valid(self) -> bool:
        """Check if the current token is still valid."""
        if self._access_token is None or self._token_expiry is None:
            return False
        # Add a small buffer (1 minute) to account for network delays
        return datetime.now(UTC) < (self._token_expiry - timedelta(minutes=1))

    async def authenticate(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate with the API and return the response data."""
        try:
            response = await self.session.post(
                f"{API_BASE_URL}{API_ENDPOINT_LOGIN}",
                json={"userName": email, "password": password},
            )
            if response.status == 401:
                raise AthleticApiClientAuthError("Invalid credentials")
            response.raise_for_status()
            data = await response.json()

            # Store the token and expiry date
            self._access_token = data.get("accessToken")
            if data.get("expirationDate"):
                # Parse the ISO format datetime string
                self._token_expiry = datetime.fromisoformat(data["expirationDate"])
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to Athletic Fitness BG API: %s", err)
            raise AthleticApiClientError("Connection error") from err
        else:
            return data

    def _get_auth_headers(self) -> dict[str, str]:
        """Return headers for authenticated requests."""
        if not self._is_token_valid() or self._access_token is None:
            raise AthleticApiClientAuthError(
                "Authentication token is invalid or expired"
            )
        return {"Authorization": f"Bearer {self._access_token}"}

    async def get_gyms(self) -> list[dict[str, Any]]:
        """Get list of available gyms."""
        try:
            response = await self.session.get(
                f"{API_BASE_URL}{API_ENDPOINT_GET_GYMS}",
            )
            response.raise_for_status()
            gyms = await response.json()

            # Filter out gyms with null/None/empty city and sort by name descending
            filtered_gyms = [
                gym
                for gym in gyms
                if gym.get("city") is not None and gym.get("city") != "None"
            ]
            filtered_gyms.sort(key=lambda x: x.get("name", ""), reverse=True)
        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching gyms from Athletic Fitness BG API: %s", err)
            raise AthleticApiClientError("Connection error") from err
        else:
            return filtered_gyms

    async def get_people_count(self, gym_id: int) -> int:
        """Get the current number of people in the gym."""
        try:
            response = await self.session.get(
                f"{API_BASE_URL}{API_ENDPOINT_GET_PEOPLE_COUNT}",
                params={"gymId": gym_id},
                headers=self._get_auth_headers(),
            )
            response.raise_for_status()
            data = await response.json()
            return int(data)
        except (aiohttp.ClientError, ValueError, TypeError) as err:
            _LOGGER.error("Error fetching people count for gym %s: %s", gym_id, err)
            raise AthleticApiClientError("Connection error") from err
