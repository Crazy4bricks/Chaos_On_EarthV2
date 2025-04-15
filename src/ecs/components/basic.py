"""Collection of common components"""

from __future__ import annotations

from typing import Final, Self, Optional

import attrs
import self
import tcod.ecs.callbacks
from tcod.ecs import Entity



@attrs.define(frozen=True)
class IsPlayer:
    """An entity is the player"""


@attrs.define(frozen=True)
class IsActor:
    """An entity is an actor"""


@attrs.define(frozen=True)
class IsItem:
    """An entity is an item"""


@attrs.define(frozen=True)
class BlocksMovement:
    """An entity blocks movement"""
    blocking: bool = True


@attrs.define(frozen=True)
class Name:
    """An entity's name"""
    name: str

@tcod.ecs.callbacks.register_component_changed(component=Name)
def on_name_changed(entity: Entity, old: Name | None, new: Name | None) -> None:
    """Mirror name components as a tag."""
    if old == new:
        return
    if old is not None:
        entity.tags.discard(old)
    if new is not None:
        entity.tags.add(new)


@attrs.define(frozen=True)
class Description:
    """An entity's description"""
    description: str


@attrs.define(frozen=True)
class Position:
    """An entity's position"""

    x: int
    y: int

    def __add__(self, direction: tuple[int, int]) -> Self:
        """Add a vector to this position"""
        x, y = direction
        return self.__class__(self.x + x, self.y + y)



@tcod.ecs.callbacks.register_component_changed(component=Position)
def on_position_changed(entity: Entity, old: Position | None, new: Position | None) -> None:
    """Mirror position components as a tag."""
    if old == new:
        return
    if old is not None:
        entity.tags.discard(old)
    if new is not None:
        entity.tags.add(new)


@attrs.define(frozen=True)
class Graphic:
    """An entity's icon and color."""

    char: str = "!"
    fg: tuple[int, int, int] = (255, 255, 255)


@attrs.define(frozen=True)
class LightEmitter:
    radius: int
