from __future__ import annotations

from typing import Final, Self, Optional

import attrs
import self
import tcod.ecs.callbacks
from tcod.ecs import Entity


@attrs.define(frozen=True)
class Attribute:
    base: int
    modifier: int
    total: int


@attrs.define(frozen=True)
class Attributes:
    grit: Attribute
    speed: Attribute
    technique: Attribute
    ego: Attribute
