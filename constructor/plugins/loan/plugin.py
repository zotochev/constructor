from __future__ import annotations
from collections.abc import Callable
from functools import partial
from itertools import chain
from msilib import Control
from typing import Any, TYPE_CHECKING
import logging
import textwrap

from flet import (
	Page,
	Container,
	Column,
	Row,
	colors,
	TextField,
	Text,
	MainAxisAlignment,
	ListView,
	Divider,
	LineChart,
	LineChartData,
	LineChartDataPoint,
	Border,
	BorderSide,
	ChartAxisLabel,
	ChartAxis,
	FontWeight,
	margin,
	TextSpan,
	TextStyle,
	Switch,
	ControlEvent,
)

import constants
from events import Events

from .calculator import Loan, NotReadyToCalculate, PAYMENT_FIELDS_NAMES, payment_field_name_by

from plugins.plugin import APlugin

if TYPE_CHECKING:
	from event_system import EventSystem


TABLE_COLUMN_WIDTH = 11
TABLE_FONT = "Courier New"


def _validate_numeric(value: Any) -> float:
	try:
		return float(value)
	except ValueError:
		assert False, f"Ожидается числовое значение, получено: {value}"


def _validate_positive(value: Any) -> float:
	value = _validate_numeric(value)
	assert value >= 0.0, "Ожидается значение большее и равное 0.0, получено: {value}"
	return value


def _validate_int(value: Any) -> int:
	value = _validate_numeric(value)
	assert abs(value) % 1.0 == 0.0, f"Ожидается целочисленное значение, получено: {value}"
	return int(value)


def _validate_pos_int(value: Any) -> int:
	value = _validate_positive(value)
	return _validate_int(value)


def _validate_pos_float(value: Any):
	return _validate_positive(value)


def _validate_pos_percent(value: Any) -> float:
	return _validate_pos_float(value) / 100.0


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


class LoanChart(LineChart):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.border = Border(
			bottom=BorderSide(4, colors.with_opacity(0.5, colors.ON_SURFACE))
		)
		self.tooltip_bgcolor = colors.with_opacity(0.8, colors.BLUE_GREY)
		self.min_y = 0
		self.min_x = 0
		# self.expand = True

	def render(self, loan: Loan) -> None:
		points_percents = []
		points_debt = []
		max_payment = 0.0
		number_of_payments = loan.number_of_payments()

		for n in range(loan.number_of_payments()):
			payment = loan.get_payment(n)
			max_payment = max(max_payment, payment.payment_percents, abs(payment.payment_dept))
			points_percents.append(LineChartDataPoint(x=n, y=round(payment.payment_percents, 2)))
			points_debt.append(LineChartDataPoint(x=n, y=round(abs(payment.payment_dept), 2)))

		self.data_series = [
			LineChartData(
				points_percents,
				stroke_width=8,
				color=colors.LIGHT_GREEN,
				curved=True,
				stroke_cap_round=True,
			),
			LineChartData(
				points_debt,
				stroke_width=8,
				color=colors.PINK,
				curved=True,
				stroke_cap_round=True,
			),
		]
		self.__render_left_axis(max_payment)
		self.__render_bottom_axis(number_of_payments)
		self.animate=5000

	def __render_left_axis(self, max_payment: float):
		step = 1000
		self.left_axis = ChartAxis(
			labels=[
				ChartAxisLabel(
					value=x * step,
					label=Text(f"{x}k", size=14, weight=FontWeight.BOLD),
				)
				for x in range(int(max_payment // step) + 1)
			],
			labels_size=40,
			title=Text(spans=[
				TextSpan(payment_field_name_by('payment_percents'), TextStyle(color=colors.LIGHT_GREEN)),
				TextSpan('\n'),
				TextSpan(payment_field_name_by('payment_dept'), TextStyle(color=colors.PINK)),
			]),
			title_size=40,
		)
		self.min_y = 0
		self.max_y = max_payment


	def __render_bottom_axis(self, number_of_payments: int) -> None:
		self.bottom_axis = ChartAxis(
			labels=[
				ChartAxisLabel(
					value=n,
					label=Container(
						Text(
							f"{n}",
							size=16,
							weight=FontWeight.BOLD,
							color=colors.with_opacity(0.5, colors.ON_SURFACE),
						),
						margin=margin.only(top=10),
					),
				)
				for n in range(number_of_payments + 1)
			],
			labels_size=32,
			show_labels=True,
			title=Text('Платежи, мес'),
			title_size=40,
		)
		self.min_x = 0
		self.max_x = number_of_payments + 1


class LoanTable(Column):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.table_header: ListView | None = None
		self.table: ListView | None = None
		self.build_table()

	def render(self, loan: Loan) -> None:
		self.table.controls.clear()
		rows = []

		for n in range(loan.number_of_payments()):
			payment = loan.get_payment(n)
			rows.append(
				Text(
					render_header([f'{x:.2f}' for x in chain([n + 1], payment)], TABLE_COLUMN_WIDTH),
					font_family=TABLE_FONT,
					selectable=True,
				)
			)

		self.table.controls.extend(rows)

	def build_table(self) -> None:
		self.table_header = ListView(
			controls=[
				Text(
					render_header([n for _, n in chain([(None, '#')], PAYMENT_FIELDS_NAMES)], TABLE_COLUMN_WIDTH),
					font_family=TABLE_FONT
				),
			],
		)
		self.table = ListView(
			expand=True,
		)
		self.controls=[
			self.table_header,
			Divider(),
			self.table,
		]


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
								validator=_validate_pos_float,
								event_system=self.event_system)
		self.interest_rate_yearly = Line('Кредитная ставка, % год',
										 on_change=partial(self.__on_change, self.calculator.set_interest_rate_yearly),
										 validator=_validate_pos_percent,
										 event_system=self.event_system)
		self.loan_term_years = Line('Срок кредита, лет',
									on_change=partial(self.__on_change, self.calculator.set_loan_term_years),
									validator=_validate_pos_int,
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


def render_header(columns, column_width: int, column_padding=2) -> str:
	columns = [textwrap.wrap(c, width=column_width) for c in columns]
	max_lines = max(len(c) for c in columns)
	result = []

	for line_number in range(max_lines):
		line = ''
		for column in columns:
			header_line = ''
			if line_number < len(column):
				header_line = column[line_number]
			line += header_line.ljust(column_width + column_padding)
		result.append(line)

	return "\n".join(result)


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
