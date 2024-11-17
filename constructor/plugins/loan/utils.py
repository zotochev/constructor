from typing import Any
import textwrap
from .calculator import PAYMENT_FIELDS_NAMES


def validate_numeric(value: Any) -> float:
    try:
        return float(value)
    except ValueError:
        assert False, f"Ожидается числовое значение, получено: {value}"


def validate_positive(value: Any) -> float:
    value = validate_numeric(value)
    assert value >= 0.0, "Ожидается значение большее и равное 0.0, получено: {value}"
    return value


def validate_int(value: Any) -> int:
    value = validate_numeric(value)
    assert abs(value) % 1.0 == 0.0, f"Ожидается целочисленное значение, получено: {value}"
    return int(value)


def validate_pos_int(value: Any) -> int:
    value = validate_positive(value)
    return validate_int(value)


def validate_pos_float(value: Any):
    return validate_positive(value)


def validate_pos_percent(value: Any) -> float:
    return validate_pos_float(value) / 100.0

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


def payment_field_name_by(field_id: str) -> str:
    for id_, name in PAYMENT_FIELDS_NAMES:
        if field_id == id_:
            return name
    return '-'
