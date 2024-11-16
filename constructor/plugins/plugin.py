from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from flet import (
		Container,
		Page,
	)
	from event_system import EventSystem


class APlugin(ABC):
	order: int | float = float('inf')
	container: Container
	page: Page
	name: str
	event_system: EventSystem
