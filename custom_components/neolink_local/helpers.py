"""Add entities for cameras that appear later in the add-on configuration."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NeolinkCoordinator


def track_cameras(
    coordinator: NeolinkCoordinator,
    add_entities: AddConfigEntryEntitiesCallback,
    build: Callable[[str], Iterable[Entity]],
    when: Callable[[dict[str, Any]], bool] = lambda cam: True,
) -> Callable[[], None]:
    """Create entities for every camera now and for each new one later.

    With `when`, a camera gets its entities only once its state matches (for
    example the battery entities after the first battery reading).
    """
    known: set[str] = set()

    @callback
    def _check() -> None:
        new = [
            n
            for n, cam in coordinator.data.get("by_name", {}).items()
            if n not in known and when(cam)
        ]
        if not new:
            return
        known.update(new)
        add_entities([e for name in new for e in build(name)])

    _check()
    return coordinator.async_add_listener(_check)
