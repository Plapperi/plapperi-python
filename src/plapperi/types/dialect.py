from enum import Enum
from typing import Union


class Dialect(str, Enum):
    """Swiss German dialects"""

    VALAIS = "vs"  # Valais / Wallis
    BASEL = "bs"  # Basel-Stadt
    AARGAU = "ag"  # Aargau
    BERN = "be"  # Bern
    ZURICH = "zh"  # Zürich
    LUCERNE = "lu"  # Luzern
    GRAUBUNDEN = "gr"  # Graubünden
    ST_GALLEN = "sg"  # St. Gallen


DialectLike = Union[str, Dialect]


def normalize_dialect(dialect: DialectLike) -> str:
    if isinstance(dialect, Dialect):
        return dialect.value

    try:
        return Dialect(dialect.lower()).value
    except ValueError as e:
        raise ValueError(
            f"Invalid dialect {dialect!r}. Allowed: {[d.value for d in Dialect]}"
        ) from e
