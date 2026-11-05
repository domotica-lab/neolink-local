"""Neolink Local: Reolink cameras (battery and P2P too) from the Neolink Local add-on."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NeolinkClient
from .const import CONF_API_PORT
from .coordinator import NeolinkCoordinator

PLATFORMS = [Platform.CAMERA, Platform.BINARY_SENSOR, Platform.SENSOR]

type NeolinkConfigEntry = ConfigEntry[NeolinkCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: NeolinkConfigEntry) -> bool:
    """Connect to the add-on and create the camera devices."""
    client = NeolinkClient(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data[CONF_API_PORT]
    )
    coordinator = NeolinkCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NeolinkConfigEntry) -> bool:
    """Remove the devices' entities."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: NeolinkConfigEntry) -> None:
    """Options changed (for example the stream quality): reload."""
    await hass.config_entries.async_reload(entry.entry_id)
