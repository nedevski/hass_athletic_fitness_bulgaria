"""Pytest configuration for the Athletic Fitness BG integration tests."""

import pytest


pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading integrations from custom_components in tests."""
    yield