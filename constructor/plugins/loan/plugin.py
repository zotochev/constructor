from __future__ import annotations
from collections.abc import Callable

from flet import (
	Page,
	Container,
	Column,
	Row,
	colors,
	TextField,
	Text,
	MainAxisAlignment,
	ControlEvent,
	Dropdown,
	dropdown,
)

import constants

from plugins.plugin import APlugin


class Line(Row):
	def __init__(self, name: str, read_only: bool = False, callback: Callable = lambda x: None, *args, **kwargs) -> None:
		self.name_field = Text(name)
		self.value_field = TextField(width=100, height=30, text_size=12, on_change=self.__on_change, read_only=read_only)
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


class LoanPlugin(APlugin):
	name = "Loan Calculator"
	order = 1

	def __init__(self, page: Page):
		self.page = page
		self.container = self.build_container()
		self.initial_payment = None
		self.loan_amount = None
		self.interest_rate_yearly = None
		self.interest_rate_monthly = None
		self.loan_term_years = None
		self.monthly_topup_available = None
		self.monthly_topup_extra = None
		self.loan_payment = None
		self.refinance_rate_yearly = None

	def build_container(self) -> Container:
		self.initial_payment = Line('Первоначальный взнос, руб')
		self.loan_amount = Line('Кредит, руб')
		self.interest_rate_yearly = Line('Кредитная ставка, % год')
		self.interest_rate_monthly = Line('Кредитная ставка, % мес')
		self.loan_term_years = Line('Срок кредита, лет')
		self.monthly_topup_available = Line('Доступно для пополнения ежемесячно')
		self.monthly_topup_extra = Line('Доступно для пополнения ежемесячно (сверх платежа кредита), тыр')
		self.loan_payment = Line('Платеж по кредиту')
		self.refinance_rate_yearly = Line('Рефинансирование. Ставка, %год')

		return Container(
			content=Column(
				controls=[
					self.initial_payment,
					self.loan_amount,
					self.interest_rate_yearly,
					self.interest_rate_monthly,
					self.loan_term_years,
					self.monthly_topup_available,
					self.monthly_topup_extra,
					self.loan_payment,
					self.refinance_rate_yearly,
				],
				spacing=0,
			),
			width=constants.PLUGIN_CONTAINER_WIDTH,
			height=constants.PLUGIN_CONTAINER_HEIGHT,
		)
