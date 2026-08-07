from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest

from plapperi.client import Plapperi
from plapperi.operations.synthetization.client import SynthetizationClient
from plapperi.types.dialect import Dialect
from plapperi.types.synthetization import (
    SynthetizationRequest,
    SynthetizationStatus,
)

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


@pytest.mark.parametrize(
    ("dialect", "expected"),
    [(Dialect.GRAUBUNDEN, "gr"), ("GR", "gr"), (None, "zh")],
)
def test_start_sends_normalized_synthetization_dialect(
    dialect, expected: str
) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={
                "jobId": "job-1",
                "jobType": "synthetization",
                "status": "pending",
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = SynthetizationClient("https://api.example", "secret", http_client)
        if dialect is None:
            client.start(DEFAULT_TEXT, DEFAULT_VOICE)
        else:
            client.start(DEFAULT_TEXT, DEFAULT_VOICE, dialect=dialect)

    assert captured["path"] == "/synthetization/run"
    assert f'"dialect":"{expected}"' in captured["body"].replace(" ", "")


def test_synth_forwards_keyword_dialect_without_changing_positional_timing() -> None:
    completed = SynthetizationStatus(
        jobId="job-1",
        status="completed",
        result={"audio_wav_b64": "UklGRg=="},
    )

    with httpx.Client() as http_client:
        client = SynthetizationClient("https://api.example", "secret", http_client)
        with patch.object(
            client, "start", return_value=SimpleNamespace(job_id="job-1")
        ) as start, patch.object(client, "status", return_value=completed):
            audio = client.synth(
                DEFAULT_TEXT,
                DEFAULT_VOICE,
                0.25,
                30.0,
                dialect="GR",
            )

    assert audio == b"UklGRg=="
    start.assert_called_once_with(
        text=DEFAULT_TEXT,
        voice=DEFAULT_VOICE,
        dialect="GR",
    )


def test_synthetization_request_defaults_to_zurich_and_accepts_tts_dialects() -> None:
    request = SynthetizationRequest(text=DEFAULT_TEXT, voice=DEFAULT_VOICE)
    assert request.dialect == Dialect.ZURICH

    for dialect in (Dialect.BERN, "GR", Dialect.LUCERNE, "zh"):
        request = SynthetizationRequest(
            text=DEFAULT_TEXT,
            voice=DEFAULT_VOICE,
            dialect=dialect,
        )
        assert request.dialect.value in {"be", "gr", "lu", "zh"}


def test_unsupported_synthetization_dialect_fails_before_http_request() -> None:
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(500)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = SynthetizationClient("https://api.example", "secret", http_client)
        with pytest.raises(ValueError, match="Invalid synthetization dialect"):
            client.start(DEFAULT_TEXT, DEFAULT_VOICE, dialect=Dialect.AARGAU)

    assert not called
