"""Tests for the WLED button platform."""
from unittest.mock import MagicMock

from freezegun import freeze_time
import pytest
from wled import WLEDConnectionError, WLEDError

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_ICON,
    ENTITY_CATEGORY_CONFIG,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry


async def test_button(
    hass: HomeAssistant, init_integration: MockConfigEntry, mock_wled: MagicMock
) -> None:
    """Test the creation and values of the WLED button."""
    entity_registry = er.async_get(hass)

    state = hass.states.get("button.wled_rgb_light_restart")
    assert state
    assert state.attributes.get(ATTR_ICON) == "mdi:restart"
    assert state.state == STATE_UNKNOWN

    entry = entity_registry.async_get("button.wled_rgb_light_restart")
    assert entry
    assert entry.unique_id == "aabbccddeeff_restart"
    assert entry.entity_category == ENTITY_CATEGORY_CONFIG

    # Restart
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: "button.wled_rgb_light_restart"},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert mock_wled.reset.call_count == 1
    mock_wled.reset.assert_called_with()


@freeze_time("2021-11-04 17:37:00", tz_offset=-1)
async def test_button_error(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_wled: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test error handling of the WLED buttons."""
    mock_wled.reset.side_effect = WLEDError

    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: "button.wled_rgb_light_restart"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("button.wled_rgb_light_restart")
    assert state
    assert state.state == "2021-11-04T16:37:00+00:00"
    assert "Invalid response from API" in caplog.text


async def test_button_connection_error(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_wled: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test error handling of the WLED buttons."""
    mock_wled.reset.side_effect = WLEDConnectionError

    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: "button.wled_rgb_light_restart"},
        blocking=True,
    )
    await hass.async_block_till_done()

    state = hass.states.get("button.wled_rgb_light_restart")
    assert state
    assert state.state == STATE_UNAVAILABLE
    assert "Error communicating with API" in caplog.text
