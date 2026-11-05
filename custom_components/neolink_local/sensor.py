"""Viewer count, time of the last image and battery level, per camera."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from homeassistant.const import EntityCategory
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE
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
            lambda name: [
                NeolinkViewers(coordinator, name, "viewers"),
                NeolinkLastImage(coordinator, name, "last_image"),
            ],
        )
    )
    entry.async_on_unload(
        track_cameras(
            coordinator,
            async_add_entities,
            lambda name: [NeolinkBattery(coordinator, name, "battery")],
            when=lambda cam: bool(cam.get("battery")),
        )
    )


class NeolinkViewers(NeolinkEntity, SensorEntity):
    """How many players are watching the camera right now."""

    _attr_translation_key = "viewers"
    _attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        cam = self.cam
        return None if cam is None else int(cam.get("viewers", 0))


class NeolinkLastImage(NeolinkEntity, SensorEntity):
    """When the camera last sent a full frame (the image shown as thumbnail)."""

    _attr_translation_key = "last_image"
    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> datetime | None:
        times = [
            s["last_frame_at"]
            for s in (self.cam or {}).get("streams", [])
            if s.get("last_frame_at")
        ]
        return datetime.fromtimestamp(max(times), UTC) if times else None


class NeolinkBattery(NeolinkEntity, SensorEntity):
    """Battery level from the last reading, taken only while the camera was awake."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def _battery(self) -> dict[str, Any]:
        return (self.cam or {}).get("battery") or {}

    @property
    def native_value(self) -> int | None:
        value = self._battery.get("percent")
        return None if value is None else int(value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        bat = self._battery
        updated = bat.get("updated_at")
        return {
            "updated_at": (
                datetime.fromtimestamp(updated, UTC).isoformat() if updated else None
            ),
            "charge_status": bat.get("charge_status"),
            "adapter": bat.get("adapter"),
            "temperature": bat.get("temperature"),
            "low_battery": bat.get("low"),
        }
