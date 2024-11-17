from __future__ import annotations
from collections.abc import Callable
from typing import Any, TYPE_CHECKING
import logging

from flet import (
    Row,
    colors,
    TextField,
    Text,
    MainAxisAlignment,
)

from events import Events

if TYPE_CHECKING:
    from event_system import EventSystem


class Line(Row):
    def __init__(self,
                 name: str,
                 read_only: bool = False,
                 on_change: Callable = lambda x: None,
                 validator: Callable = lambda x: x,
                 event_system: EventSystem = None,
                 *args, **kwargs) -> None:
        self._name = name
        self.name_field = Text(name)
        self.value_field = TextField(width=100, height=30, text_size=12, on_change=self.__on_change, read_only=read_only)
        self.on_change = on_change
        self.validator = validator
        self.event_system = event_system
        super().__init__(controls=[self.name_field, self.value_field], alignment=MainAxisAlignment.SPACE_BETWEEN, *args, **kwargs)

    def __on_change(self, event):
        try:
            value = self.validator(event.data)
            self.value_field.border_color = colors.BLACK
            self.on_change(value)
        except AssertionError as ae:
            self.value_field.border_color = colors.RED
            logging.warning(f"{self.__class__.__name__}.__on_change: {ae.__class__.__name__}: {ae}")
            if self.event_system:
                self.event_system.emit(Events.Main.error, f"{self._name}: {ae}")
        except Exception as e:
            self.value_field.border_color = colors.RED
            logging.error(f"{self.__class__.__name__}.__on_change: {e.__class__.__name__}: {e}")

        self.update()

    def set_value(self, value: float) -> None:
        self.value_field.value = value
        self.update()
