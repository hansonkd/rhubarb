import dataclasses
from typing import Any

from rhubarb.object_set import Registry


@dataclasses.dataclass
class Config:
    registry: Registry
