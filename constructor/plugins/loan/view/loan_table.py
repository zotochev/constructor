from __future__ import annotations
from collections.abc import Callable
from functools import partial
from itertools import chain
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

from ..calculator import PAYMENT_FIELDS_NAMES
from ..utils import render_header

if TYPE_CHECKING:
    from ..calculator import Loan


TABLE_COLUMN_WIDTH = 11
TABLE_FONT = "Courier New"


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
