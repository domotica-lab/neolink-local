"""Whether each camera is connected (awake) and whether its battery is charging."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NeolinkConfigEntry
from .entity import NeolinkEntity
from .helpers import track_cameras


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NeolinkConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entry.async_on_unload(
        track_cameras(
            coordinator,
            async_add_entities,
            lambda name: [NeolinkConnected(coordinator, name, "connected")],
        )
    )
    entry.async_on_unload(
        track_cameras(
            coordinator,
            async_add_entities,
            lambda name: [NeolinkCharging(coordinator, name, "battery_charging")],
            when=lambda cam: bool(cam.get("battery")),
        )
    )


class NeolinkConnected(NeolinkEntity, BinarySensorEntity):
    """On while neolink holds a connection to the camera."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_translation_key = "connected"

    @property
    def is_on(self) -> bool | None:
        cam = self.cam
        return None if cam is None else bool(cam.get("connected"))


class NeolinkCharging(NeolinkEntity, BinarySensorEntity):
    """On while the battery is charging (solar panel or cable), as last read."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    @property
    def is_on(self) -> bool | None:
        bat = (self.cam or {}).get("battery")
        return None if not bat else bool(bat.get("charging"))
