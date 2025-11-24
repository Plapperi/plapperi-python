from enum import Enum


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
