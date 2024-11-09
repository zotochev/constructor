from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING

from flet import (
	Container,
	Page,
)

# if TYPE_CHECKING:
# 	from core.event_system import EventSystem


class APlugin(ABC):
	order = 0
	container: Container = None
	page: Page = None
	name: str = None
	# event_system: EventSystem = None
