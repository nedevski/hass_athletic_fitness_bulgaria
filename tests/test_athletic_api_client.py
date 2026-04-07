"""Tests for the Athletic Fitness BG API client."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest

from custom_components.athletic_fitness_bg.athletic_api_client import (
    AthleticApiClient,
    AthleticApiClientAuthError,
)


async def test_authenticate_stores_token_and_normalizes_expiration(hass) -> None:
    """Authenticate should store the token and normalize naive expirations."""
    client = AthleticApiClient(hass)

    # Create dynamic expiration (naive datetime)
    mock_expiration = datetime.now() + timedelta(minutes=5)
    mock_expiration_str = mock_expiration.isoformat()

    response = Mock(status=200)
    response.raise_for_status = Mock()
    response.json = AsyncMock(
        return_value={
            "accessToken": "token-123",
            "expirationDate": mock_expiration_str,
        }
    )
    client.session = Mock(post=AsyncMock(return_value=response))

    result = await client.authenticate("user@example.com", "secret")

    # Expected normalized expiration (UTC-aware)
    expected_expiration = mock_expiration.replace(tzinfo=UTC)

    assert result["accessToken"] == "token-123"
    assert client._access_token == "token-123"
    assert client._token_expiry == expected_expiration
    assert client._get_auth_headers() == {"Authorization": "Bearer token-123"}


async def test_get_auth_headers_rejects_missing_or_expired_token(hass) -> None:
    """Authenticated headers should require a currently valid token."""
    client = AthleticApiClient(hass)

    with pytest.raises(AthleticApiClientAuthError):
        client._get_auth_headers()

    client._access_token = "expired-token"
    client._token_expiry = datetime.now(UTC) + timedelta(seconds=30)

    with pytest.raises(AthleticApiClientAuthError):
        client._get_auth_headers()


async def test_get_gyms_filters_out_entries_without_city_and_sorts_descending(
    hass,
) -> None:
    """Gym results should exclude incomplete entries and sort by display name."""
    client = AthleticApiClient(hass)
    response = Mock()
    response.raise_for_status = Mock()
    response.json = AsyncMock(
        return_value=[
            {"gymId": 1, "gymName": "Mladost", "city": "Sofia"},
            {"gymId": 2, "gymName": "Arena", "city": None},
            {"gymId": 3, "gymName": "West", "city": "Plovdiv"},
        ]
    )
    client.session = Mock(get=AsyncMock(return_value=response))

    gyms = await client.get_gyms()

    assert gyms == [
        {"gymId": 3, "gymName": "West", "city": "Plovdiv"},
        {"gymId": 1, "gymName": "Mladost", "city": "Sofia"},
    ]


async def test_get_people_count_wraps_invalid_payload_errors(hass) -> None:
    """People count fetch should convert non-numeric payload failures into client errors."""
    client = AthleticApiClient(hass)
    client._access_token = "valid-token"
    client._token_expiry = datetime.now(UTC) + timedelta(minutes=5)

    response = Mock()
    response.raise_for_status = Mock()
    response.json = AsyncMock(return_value="not-a-number")
    client.session = Mock(get=AsyncMock(return_value=response))

    with pytest.raises(Exception) as err:
        await client.get_people_count(42)

    assert err.type.__name__ == "AthleticApiClientError"


async def test_authenticate_raises_auth_error_on_unauthorized(hass) -> None:
    """Unauthorized login responses should raise the auth-specific exception."""
    client = AthleticApiClient(hass)
    response = Mock(status=401)
    client.session = Mock(post=AsyncMock(return_value=response))

    with pytest.raises(AthleticApiClientAuthError):
        await client.authenticate("user@example.com", "bad-secret")


async def test_get_gyms_wraps_client_errors(hass) -> None:
    """Network failures while fetching gyms should be wrapped consistently."""
    client = AthleticApiClient(hass)
    client.session = Mock(get=AsyncMock(side_effect=aiohttp.ClientError("boom")))

    with pytest.raises(Exception) as err:
        await client.get_gyms()

    assert err.type.__name__ == "AthleticApiClientError"