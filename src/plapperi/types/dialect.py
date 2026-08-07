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
SYNTHETIZATION_DIALECTS = (
    Dialect.BERN.value,
    Dialect.GRAUBUNDEN.value,
    Dialect.LUCERNE.value,
    Dialect.ZURICH.value,
)


def normalize_dialect(dialect: DialectLike) -> str:
    if isinstance(dialect, Dialect):
        return dialect.value

    try:
        return Dialect(dialect.lower()).value
    except ValueError as e:
        raise ValueError(
            f"Invalid dialect {dialect!r}. Allowed: {[d.value for d in Dialect]}"
        ) from e


def normalize_synthetization_dialect(dialect: DialectLike) -> str:
    if not isinstance(dialect, (str, Dialect)):
        raise ValueError(
            f"Invalid synthetization dialect {dialect!r}. "
            f"Allowed: {list(SYNTHETIZATION_DIALECTS)}"
        )
    normalized = normalize_dialect(dialect)
    if normalized not in SYNTHETIZATION_DIALECTS:
        raise ValueError(
            f"Invalid synthetization dialect {dialect!r}. "
            f"Allowed: {list(SYNTHETIZATION_DIALECTS)}"
        )
    return normalized
