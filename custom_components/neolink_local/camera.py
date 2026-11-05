"""Camera entities: live video over RTSP, still images that never wake the camera."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import NeolinkConfigEntry
from .api import NeolinkError
from .const import CONF_RTSP_HOST, CONF_STREAM, DEFAULT_STREAM
from .coordinator import NeolinkCoordinator
from .entity import NeolinkEntity
from .helpers import track_cameras


async def async_setup_entry(
    hass: HomeAssistant,
    entry: NeolinkConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    stream = entry.options.get(CONF_STREAM, DEFAULT_STREAM)
    entry.async_on_unload(
        track_cameras(
            coordinator,
            async_add_entities,
            lambda name: [NeolinkCamera(coordinator, name, stream)],
        )
    )


class NeolinkCamera(NeolinkEntity, Camera):
    """A Reolink camera served by the Neolink Local add-on."""

    _attr_name = None
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(self, coordinator: NeolinkCoordinator, camera: str, stream: str) -> None:
        NeolinkEntity.__init__(self, coordinator, camera, "camera")
        Camera.__init__(self)
        self._stream = stream

    def _stream_for_camera(self) -> str:
        """The configured stream if this camera publishes it, else the first it has."""
        streams = [s["stream"] for s in (self.cam or {}).get("streams", [])]
        if not streams or self._stream in streams:
            return self._stream
        return streams[0]

    async def stream_source(self) -> str | None:
        """RTSP address of the live stream (opening it wakes the camera)."""
        data = self.coordinator.config_entry.data
        host = data.get(CONF_RTSP_HOST) or data[CONF_HOST]
        port = self.coordinator.data.get("rtsp_port", 8558)
        auth = ""
        if data.get(CONF_USERNAME):
            auth = f"{quote(data[CONF_USERNAME], safe='')}:{quote(data.get(CONF_PASSWORD, ''), safe='')}@"
        path = f"{quote(self.camera_name, safe='')}/{self._stream_for_camera()}"
        return f"rtsp://{auth}{host}:{port}/{path}"

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Last image the add-on saw. Never contacts (or wakes) the camera."""
        try:
            return await self.coordinator.client.snapshot(
                self.camera_name, self._stream_for_camera()
            )
        except NeolinkError:
            return None

    @property
    def is_streaming(self) -> bool:
        return bool((self.cam or {}).get("viewers"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        cam = self.cam or {}
        return {
            "connected": cam.get("connected"),
            "viewers": cam.get("viewers"),
            "connect_mode": cam.get("connect_mode"),
            "stream": self._stream_for_camera(),
        }
