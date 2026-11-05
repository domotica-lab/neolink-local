"""Client for the Neolink Local status API (served by the add-on)."""

from __future__ import annotations

import asyncio
from typing import Any
from urllib.parse import quote

import aiohttp

from .const import REQUEST_TIMEOUT


class NeolinkError(Exception):
    """The add-on could not be reached or answered badly."""


class NeolinkClient:
    """Talks to `http://<host>:<port>/api/...`."""

    def __init__(self, session: aiohttp.ClientSession, host: str, port: int) -> None:
        self._session = session
        self._base = f"http://{host}:{port}/api"

    async def status(self) -> dict[str, Any]:
        """Return every camera with its state and streams."""
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                resp = await self._session.get(f"{self._base}/status")
                resp.raise_for_status()
                data = await resp.json()
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise NeolinkError(str(err)) from err
        if not isinstance(data, dict) or not isinstance(data.get("cameras"), list):
            raise NeolinkError("unexpected answer from the status API")
        return data

    async def snapshot(self, camera: str, stream: str) -> bytes | None:
        """Last image of a camera. Never wakes the camera; None if there is none yet."""
        url = f"{self._base}/cameras/{quote(camera, safe='')}/snapshot.jpg"
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                resp = await self._session.get(url, params={"stream": stream})
                if resp.status == 404:
                    return None
                resp.raise_for_status()
                return await resp.read()
        except (aiohttp.ClientError, TimeoutError) as err:
            raise NeolinkError(str(err)) from err
