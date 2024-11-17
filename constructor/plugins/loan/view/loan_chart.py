from __future__ import annotations
from typing import Any, TYPE_CHECKING

from flet import (
    Container,
    colors,
    Text,
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
)

from ..utils import payment_field_name_by

if TYPE_CHECKING:
    from ..calculator import Loan


TABLE_COLUMN_WIDTH = 11
TABLE_FONT = "Courier New"


class LoanChart(LineChart):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.border = Border(
            bottom=BorderSide(4, colors.with_opacity(0.5, colors.ON_SURFACE))
        )
        self.tooltip_bgcolor = colors.with_opacity(0.8, colors.BLUE_GREY)
        self.min_y = 0
        self.min_x = 0

    def render(self, loan: Loan) -> None:
        points_percents = []
        points_debt = []
        max_payment = 0.0
        number_of_payments = loan.number_of_payments()
        tooltip_style = TextStyle(size=10)

        for n in range(loan.number_of_payments()):
            payment = loan.get_payment(n)
            max_payment = max(max_payment, payment.payment_percents, abs(payment.payment_dept))

            percents_y = round(payment.payment_percents, 2)
            tooltip_percents = "{} : {} : {}".format(
                n,
                payment_field_name_by('payment_percents'),
                percents_y,
            )
            points_percents.append(
                LineChartDataPoint(
                    x=n,
                    y=percents_y,
                    tooltip=tooltip_percents,
                    tooltip_style=tooltip_style,
                )
            )

            debt_y = round(abs(payment.payment_dept), 2)
            tooltip_debt = "{} : {} : {}".format(
                n,
                payment_field_name_by('payment_dept'),
                debt_y,
            )
            points_debt.append(
                LineChartDataPoint(
                    x=n,
                    y=debt_y,
                    tooltip=tooltip_debt,
                    tooltip_style=tooltip_style,
                )
            )

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
        self.animate=1000

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
