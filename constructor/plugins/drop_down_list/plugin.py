from __future__ import annotations

from flet import (
	Page,
	Container,
	Row,
	Text,
	ControlEvent,
	Dropdown,
	dropdown,
)

import constants

from plugins.plugin import APlugin


bd = {
	"1": 10,
	"2": 20,
	"3": 30,
}


class DropDownListPlugin(APlugin):
	name = "Drop Down List"

	def __init__(self, page: Page, event_system):
		self.page = page
		self.dd = None
		self.result: Text | None = None
		self.container = self.build_container()
		self.event_system = event_system

	def build_container(self) -> Container:
		self.dd = Dropdown(
			width=100,
			options=[
				dropdown.Option(k) for k in bd.keys()
			],
			on_change=self.__on_change_dd,
		)
		self.result = Text()

		return Container(
			content=Row(
				controls=[
					self.dd,
					self.result,
				],
			),
			width=constants.PLUGIN_CONTAINER_WIDTH,
			height=constants.PLUGIN_CONTAINER_HEIGHT,
		)

	def __on_change_dd(self, event: ControlEvent) -> None:
		print(f'__on_change_dd: {event}')
		self.result.value = bd[event.data]
		self.result.update()
