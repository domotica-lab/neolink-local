"""Keeps the camera list and states fresh."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NeolinkClient, NeolinkError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class NeolinkCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls the add-on's status API; reading it never wakes a camera."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: NeolinkClient
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            data = await self.client.status()
        except NeolinkError as err:
            raise UpdateFailed(f"Neolink Local add-on not reachable: {err}") from err
        # Index cameras by name for the entities.
        data["by_name"] = {cam["name"]: cam for cam in data["cameras"]}
        return data
