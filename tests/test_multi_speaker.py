from unittest.mock import patch

import httpx
import pytest

from plapperi.errors.api_error import ApiError
from plapperi.errors.timeout_error import PlapperiTimeoutError
from plapperi.operations.multi_speaker.client import MultiSpeakerClient
from plapperi.types.dialect import Dialect
from plapperi.types.job import JobType
from plapperi.types.multi_speaker import (
    DialogueTurn,
    MultiSpeakerRequest,
    MultiSpeakerStatus,
    Speaker,
)


SPEAKERS = [
    Speaker(id="speaker-1", voice="tavin", dialect="zh"),
    Speaker(id="speaker-2", voice="brisa", dialect="gr"),
]
TURNS = [
    DialogueTurn(speaker_id="speaker-1", text="Hoi mitenand."),
    DialogueTurn(speaker_id="speaker-2", text="Sali, wie geits?"),
]


def test_request_validates_distinct_active_speakers() -> None:
    with pytest.raises(ValueError, match="distinct voices"):
        MultiSpeakerRequest(
            speakers=[SPEAKERS[0], Speaker(id="speaker-2", voice="tavin", dialect="be")],
            turns=TURNS,
        )

    with pytest.raises(ValueError, match="Both speakers"):
        MultiSpeakerRequest(speakers=SPEAKERS, turns=[TURNS[0]])


def test_speaker_accepts_graubuenden_and_rejects_translation_only_dialects() -> None:
    assert (
        Speaker(id="speaker-1", voice="tavin", dialect=Dialect.GRAUBUNDEN).dialect
        == "gr"
    )

    with pytest.raises(ValueError, match="Multi-speaker dialect"):
        Speaker(id="speaker-1", voice="tavin", dialect=Dialect.AARGAU)


def test_start_uses_structured_public_endpoint() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={"jobId": "job-1", "jobType": "multi-speaker", "status": "pending"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = MultiSpeakerClient("https://api.example", "secret", http_client)
        job = client.start(SPEAKERS, TURNS)

    assert captured["path"] == "/multi-speaker/run"
    assert '"speakerId":"speaker-1"' in captured["body"].replace(" ", "")
    assert job.job_type == JobType.MULTI_SPEAKER


def test_status_normalizes_empty_processing_result() -> None:
    status = MultiSpeakerStatus.model_validate(
        {"jobId": "job-1", "status": "processing", "result": {}}
    )

    assert status.is_processing
    assert status.result is None


def test_synth_polls_and_downloads_wav_bytes() -> None:
    status_calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal status_calls
        if request.url.path == "/multi-speaker/run":
            return httpx.Response(
                200,
                json={"jobId": "job-1", "jobType": "multi-speaker", "status": "pending"},
            )
        if request.url.path == "/multi-speaker/status/job-1":
            status_calls += 1
            if status_calls == 1:
                return httpx.Response(
                    200,
                    json={
                        "jobId": "job-1",
                        "jobType": "multi-speaker",
                        "status": "processing",
                        "result": {},
                    },
                )
            return httpx.Response(
                200,
                json={
                    "jobId": "job-1",
                    "jobType": "multi-speaker",
                    "status": "completed",
                    "result": {
                        "audio": {
                            "contentType": "audio/wav",
                            "playbackUrl": "https://audio.example/play",
                            "downloadUrl": "https://audio.example/download",
                            "urlExpiresAt": "2030-01-01T00:00:00+00:00",
                        }
                    },
                },
            )
        if request.url.host == "audio.example":
            return httpx.Response(200, content=b"RIFF-test-wav")
        raise AssertionError(f"Unexpected request: {request.url}")

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = MultiSpeakerClient("https://api.example", "secret", http_client)
        with patch("plapperi.operations.multi_speaker.client.time.sleep"):
            audio = client.synth(SPEAKERS, TURNS, poll_interval=0, timeout=10)

    assert audio == b"RIFF-test-wav"
    assert status_calls == 2


def test_synth_rejects_completed_status_without_audio() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/multi-speaker/run":
            return httpx.Response(
                200,
                json={"jobId": "job-1", "jobType": "multi-speaker", "status": "pending"},
            )
        if request.url.path == "/multi-speaker/status/job-1":
            return httpx.Response(
                200,
                json={
                    "jobId": "job-1",
                    "jobType": "multi-speaker",
                    "status": "completed",
                    "result": {},
                },
            )
        raise AssertionError(f"Unexpected request: {request.url}")

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = MultiSpeakerClient("https://api.example", "secret", http_client)
        with pytest.raises(ApiError, match="completed without an audio result"):
            client.synth(SPEAKERS, TURNS, poll_interval=0, timeout=10)


def test_synth_raises_clear_timeout() -> None:
    client = MultiSpeakerClient("https://api.example", "secret", httpx.Client())
    with patch.object(
        client,
        "start",
        return_value=type("JobStub", (), {"job_id": "job-timeout"})(),
    ), patch("plapperi.operations.multi_speaker.client.time.monotonic", side_effect=[0, 2]):
        with pytest.raises(PlapperiTimeoutError, match="job-timeout"):
            client.synth(SPEAKERS, TURNS, timeout=1)
    client.client.close()
