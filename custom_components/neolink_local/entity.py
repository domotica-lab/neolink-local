"""Base entity: one device per camera."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NeolinkCoordinator


class NeolinkEntity(CoordinatorEntity[NeolinkCoordinator]):
    """An entity that belongs to one Neolink camera."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: NeolinkCoordinator, camera: str, key: str) -> None:
        super().__init__(coordinator)
        self.camera_name = camera
        entry_id = coordinator.config_entry.entry_id
        self._attr_unique_id = f"{entry_id}_{camera}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{camera}")},
            name=camera,
            manufacturer="Reolink",
            model="Neolink Local",
            # Clears the "Firmware" that 1.0.0 wrongly showed (it was the add-on version).
            sw_version=None,
        )

    @property
    def cam(self) -> dict[str, Any] | None:
        """This camera's latest state, or None if it left the configuration."""
        return self.coordinator.data.get("by_name", {}).get(self.camera_name)

    @property
    def available(self) -> bool:
        cam = self.cam
        return super().available and cam is not None and cam.get("enabled", True)
