from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from functools import partial

from flet import (
	Page,
	Container,
	Column,
	Row,
	colors,
	TextField,
	Text,
	MainAxisAlignment,
)

import constants

from plugins.plugin import APlugin


class Line(Row):
	def __init__(self, name: str, read_only: bool = False, callback: Callable = lambda x: None, *args, **kwargs) -> None:
		self.name_field = Text(name)
		self.value_field = TextField(width=100, on_change=self.__on_change, read_only=read_only)
		self.callback = callback
		super().__init__(controls=[self.name_field, self.value_field], alignment=MainAxisAlignment.SPACE_BETWEEN, *args, **kwargs)

	def __on_change(self, event):
		try:
			self.value_field.border_color = colors.BLACK
			self.callback(event.data)
		except Exception as e:
			self.value_field.border_color = colors.RED
			print(e.__class__.__name__, e)

		self.update()

	def set_value(self, value: float) -> None:
		self.value_field.value = value
		self.update()


class WxCalculator:
	def __init__(self) -> None:
		self.__momentum = 0.0
		self.__material_sigma = 0.0

	def calculate(self) -> float:
		result = (self.__momentum * 10 ** 3) / (self.__material_sigma * 10 ** 6)
		return result * 10 ** 6

	def set_momentum(self, momentum: float) -> None:
		self.__momentum = momentum

	def set_material_sigma(self, material_sigma: float) -> None:
		self.__material_sigma = material_sigma


# @register_plugin
class BeamPlugin(APlugin):
	name = "Beam"
	order = 1

	def __init__(self, page: Page):
		self.page = page
		self.m_field = None
		self.sigma_field = None
		self.wx_field = None
		self.calculator = WxCalculator()
		self.container = self.build_container()

	def build_container(self) -> Container:
		self.m_field = Line('Момент, кH/м:', callback=partial(self.__calc, self.calculator.set_momentum))
		self.sigma_field = Line('σ (материала), МПа:', callback=partial(self.__calc, self.calculator.set_material_sigma))
		self.wx_field = Line('Wx, см^3:', read_only=True)

		return Container(
			content=Column(
				controls=[
					self.m_field,
					self.sigma_field,
					self.wx_field,
				],
			),
			width=constants.PLUGIN_CONTAINER_WIDTH,
			height=constants.PLUGIN_CONTAINER_HEIGHT,
		)

	def __calc(self, callback: Callable[[float], None], value: str):
		try:
			callback(float(value) if value else 0.0)
			result = self.calculator.calculate()
			self.wx_field.set_value(result)
		except ZeroDivisionError:
			self.wx_field.set_value('Деление на ноль')
		except Exception as e:
			self.wx_field.set_value(f'{self.__class__.__name__}: {e}')
		self.container.update()
