from __future__ import annotations
from collections.abc import Callable
from functools import partial
from typing import Any
import logging

from flet import (
	Page,
	Container,
	Column,
	Divider,
	Switch,
	ControlEvent,
)

import constants
from events import Events

from plugins.plugin import APlugin

from .calculator import Loan, NotReadyToCalculate
from .view import Line, LoanTable, LoanChart
from .utils import validate_pos_int, validate_pos_float, validate_pos_percent


class LoanPlugin(APlugin):
	name = "Loan Calculator"
	order = 0

	def __init__(self, page: Page, event_system):
		self.page = page
		self.event_system = event_system

		self.loan_amount = None
		self.interest_rate_yearly = None
		self.loan_term_years = None

		self.payments_table: LoanTable = LoanTable()
		self.payments_chart: LoanChart = LoanChart()
		self.payments_container = Container(content=self.payments_table, expand=True, visible=False)
		self.view_switch = Switch(label='Таблица', on_change=self.__on_switch)

		self.calculator = Loan()

		self.container = self.build_container()

	def build_container(self) -> Container:
		self.loan_amount = Line('Кредит, руб',
								on_change=partial(self.__on_change, self.calculator.set_loan_amount),
								validator=validate_pos_float,
								event_system=self.event_system)
		self.interest_rate_yearly = Line('Кредитная ставка, % год',
										 on_change=partial(self.__on_change, self.calculator.set_interest_rate_yearly),
										 validator=validate_pos_percent,
										 event_system=self.event_system)
		self.loan_term_years = Line('Срок кредита, лет',
									on_change=partial(self.__on_change, self.calculator.set_loan_term_years),
									validator=validate_pos_int,
									event_system=self.event_system)

		return Container(
			content=Column(
				controls=[
					self.loan_amount,
					self.interest_rate_yearly,
					self.loan_term_years,
					self.view_switch,
					Divider(),
					self.payments_container,
				],
				spacing=0,
			),
			width=constants.PLUGIN_CONTAINER_WIDTH,
			height=constants.PLUGIN_CONTAINER_HEIGHT,
		)


	def __on_change(self, setter: Callable, value: Any):
		try:
			setter(value)
			self.__render_loan()
			self.container.update()
		except NotReadyToCalculate as nr:
			self.payments_container.visible = False
			message = f"{self.__class__.__name__}.__on_change: {nr.__class__.__name__}: {nr}"
			logging.debug(message)
		except Exception as e:
			self.payments_container.visible = False
			message = f"{self.__class__.__name__}.__on_change: {e.__class__.__name__}: {e}"
			logging.warning(message)
			self.event_system.emit(Events.Main.error, message)

	def __render_loan(self):
		self.calculator.calc()

		self.__render_table(self.calculator)
		self.__render_chart(self.calculator)
		self.payments_container.visible = True
		self.container.update()

	def __render_table(self, loan: Loan):
		self.payments_table.render(loan)

	def __render_chart(self, loan):
		self.payments_chart.render(loan)

	def __on_switch(self, event: ControlEvent):
		is_chart_view = event.control.value

		if is_chart_view:
			self.view_switch.label = 'График'
			self.payments_container.content = self.payments_chart
		else:
			self.view_switch.label = 'Таблица'
			self.payments_container.content = self.payments_table

		self.view_switch.update()
		self.payments_container.update()


def foo():
	"""
		# self.initial_payment = None
		self.loan_amount = None
		self.interest_rate_yearly = None
		# self.interest_rate_monthly = None
		self.loan_term_years = None
		# self.monthly_topup_available = None
		# self.monthly_topup_extra = None
		# self.loan_payment = None
		# self.refinance_rate_yearly = None

		# self.initial_payment = Line('Первоначальный взнос, руб')
		self.loan_amount = Line('Кредит, руб')
		self.interest_rate_yearly = Line('Кредитная ставка, % год')
		# self.interest_rate_monthly = Line('Кредитная ставка, % мес')
		self.loan_term_years = Line('Срок кредита, лет')
		# self.monthly_topup_available = Line('Доступно для пополнения ежемесячно')
		# self.monthly_topup_extra = Line('Доступно для пополнения ежемесячно (сверх платежа кредита), тыр')
		# self.loan_payment = Line('Платеж по кредиту')
		# self.refinance_rate_yearly = Line('Рефинансирование. Ставка, %год')
	"""
	pass
