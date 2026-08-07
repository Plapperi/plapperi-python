import time
import typing

import httpx

from plapperi.errors.api_error import ApiError
from plapperi.errors.timeout_error import PlapperiTimeoutError
from plapperi.operations.base_client import BaseClient
from plapperi.types.job import Job
from plapperi.types.multi_speaker import (
    DialogueTurn,
    MultiSpeakerRequest,
    MultiSpeakerStatus,
    Speaker,
)


class MultiSpeakerClient(BaseClient):
    """Client for native two-speaker dialogue synthesis."""

    def start(
        self,
        speakers: typing.Sequence[Speaker],
        turns: typing.Sequence[DialogueTurn],
    ) -> Job:
        request = MultiSpeakerRequest(speakers=list(speakers), turns=list(turns))
        response = self._make_request(
            "POST",
            "multi-speaker/run",
            json=request.model_dump(by_alias=True),
        )
        return Job.model_validate(response)

    def status(self, job_id: str) -> MultiSpeakerStatus:
        response = self._make_request("GET", f"multi-speaker/status/{job_id}")
        return MultiSpeakerStatus.model_validate(response)

    def synth(
        self,
        speakers: typing.Sequence[Speaker],
        turns: typing.Sequence[DialogueTurn],
        poll_interval: float = 2.0,
        timeout: float = 900.0,
    ) -> bytes:
        """Generate one dialogue WAV and wait up to 15 minutes by default."""
        job = self.start(speakers=speakers, turns=turns)
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            status = self.status(job.job_id)
            if status.is_completed:
                if not status.result:
                    raise ApiError(body="Job completed without an audio result.")
                try:
                    response = self.client.get(status.result.audio.download_url)
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    raise ApiError(
                        body=(
                            "Audio download failed: "
                            f"{exc.response.status_code} - {exc.response.text}"
                        ),
                        status_code=exc.response.status_code,
                    ) from exc
                except httpx.RequestError as exc:
                    raise ApiError(body=f"Audio download failed: {exc}") from exc
                return response.content
            if status.is_failed:
                raise ApiError(body=f"Multi-speaker job failed: {status.error}")
            time.sleep(poll_interval)

        raise PlapperiTimeoutError(
            f"Multi-speaker job {job.job_id} did not complete within {timeout}s"
        )
