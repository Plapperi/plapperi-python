import time

import httpx

from plapperi.errors.api_error import ApiError
from plapperi.errors.timeout_error import PlapperiTimeoutError
from plapperi.operations.base_client import BaseClient
from plapperi.types.job import Job
from plapperi.types.synthetization import SynthetizationStatus


class SynthetizationClient(BaseClient):
    """Client for synthetization operations"""

    def __init__(self, base_url: str, api_key: str, client: httpx.Client):
        super().__init__(base_url=base_url, api_key=api_key, client=client)

    def start(self, text: str, voice: str) -> Job:
        """
        Start a synthetization job

        Args:
            text: Text to translate to Swiss German
            voice: Voice code (e.g., 'aragon')

        Returns:
            Job information including jobId and status
        """
        payload = {"text": text, "voice": voice}
        response = self._make_request("POST", "synthetization/run", json=payload)
        return Job.model_validate(response)

    def status(self, job_id: str) -> SynthetizationStatus:
        """
        Check the status of a synthetization job

        Args:
            job_id: The job ID returned from start()

        Returns:
            Job status information
        """
        response = self._make_request("GET", f"synthetization/status/{job_id}")
        return SynthetizationStatus.model_validate(response)

    def synth(
        self,
        text: str,
        voice: str,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> bytes:
        """
        Synthetize text and wait for completion

        Args:
            text: Text to synthetize
            voice: Voice code (e.g., 'aragon')
            poll_interval: Seconds between status checks (default: 1.0)
            timeout: Maximum seconds to wait (default: 60.0)

        Returns:
            The synthetized audio

        Raises:
            PlapperiTimeoutError: If job doesn't complete within timeout
            PlapperiAPIError: If job fails or API error occurs
        """
        # Start the job
        job = self.start(text=text, voice=voice)

        # Poll for completion
        elapsed = 0.0
        while elapsed < timeout:
            status = self.status(job.job_id)

            if status.is_completed:
                if status.result and status.result.audio_wav_b64:
                    return status.result.audio_wav_b64.encode("ascii")
                raise ApiError(body="Job completed but no translation result found.")
            elif status.is_failed:
                raise ApiError(body=f"Translation job failed: {status.error}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise PlapperiTimeoutError(
            f"Translation job {job.job_id} did not complete within {timeout}s"
        )
