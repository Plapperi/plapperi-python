from plapperi.client import Plapperi
from plapperi.types.translation import TranslationStatus

from .utils import DEFAULT_DIALECT, DEFAULT_TEXT


def test_translate() -> None:
    client = Plapperi()
    result = client.translation.translate(
        text=DEFAULT_TEXT,
        dialect=DEFAULT_DIALECT,
        beam_size=4,
    )
    assert isinstance(result, str), "Translation should be returned as text"


def test_translate_manual_job_control() -> None:
    client = Plapperi()
    job = client.translation.start(
        text=DEFAULT_TEXT,
        dialect=DEFAULT_DIALECT,
    )
    status = client.translation.status(job.job_id)

    assert isinstance(
        status, TranslationStatus
    ), "Status should be returned as TranslationStatus"
