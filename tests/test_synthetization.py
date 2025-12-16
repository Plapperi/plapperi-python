from plapperi.client import Plapperi
from plapperi.types.synthetization import SynthetizationStatus

from .utils import DEFAULT_TEXT, DEFAULT_VOICE


def test_synth() -> None:
    client = Plapperi()
    result = client.synthetization.synth(
        text=DEFAULT_TEXT,
        voice=DEFAULT_VOICE,
    )
    assert isinstance(result, bytes), "Audio should be returned as bytes"


def test_synth_manual_job_control() -> None:
    client = Plapperi()
    job = client.synthetization.start(
        text=DEFAULT_TEXT,
        voice=DEFAULT_VOICE,
    )
    status = client.synthetization.status(job.job_id)

    assert isinstance(
        status, SynthetizationStatus
    ), "Status should be returned as SynthetizationStatus"
