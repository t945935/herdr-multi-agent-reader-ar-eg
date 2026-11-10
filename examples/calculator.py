"""الفصل الأول: عقد صغير عمدًا لتمرين التطوير والمراجعة."""

from math import isfinite


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("تُتوقع قيمة رقمية، باستثناء النوع bool")
    if not isfinite(value):
        raise ValueError("تُتوقع قيمة رقمية منتهية")
    return value


def add(a, b):
    return _number(a) + _number(b)


def subtract(a, b):
    return _number(a) - _number(b)


def multiply(a, b):
    return _number(a) * _number(b)


def divide(a, b):
    a, b = _number(a), _number(b)
    if b == 0:
        raise ZeroDivisionError("لا تجوز القسمة على صفر")
    return a / b
