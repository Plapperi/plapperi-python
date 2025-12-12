import time

import httpx

from plapperi.errors.api_error import ApiError
from plapperi.errors.timeout_error import PlapperiTimeoutError
from plapperi.operations.base_client import BaseClient
from plapperi.types.dialect import DialectLike, normalize_dialect
from plapperi.types.job import Job
from plapperi.types.translation import TranslationStatus


class TranslationClient(BaseClient):
    """Client for translation operations"""

    def __init__(self, base_url: str, api_key: str, client: httpx.Client):
        super().__init__(base_url=base_url, api_key=api_key, client=client)

    def start(self, text: str, dialect: DialectLike, beam_size: int = 4) -> Job:
        """
        Start a translation job

        Args:
            text: Text to translate to Swiss German
            dialect: Dialect code (e.g., 'vs' for Valais)
            beam_size: Beam size for translation (default: 4)

        Returns:
            Job information including jobId and status
        """
        payload = {
            "text": text,
            "dialect": normalize_dialect(dialect),
            "beam_size": beam_size,
        }
        response = self._make_request("POST", "translation/run", json=payload)
        return Job.model_validate(response)

    def status(self, job_id: str) -> TranslationStatus:
        """
        Check the status of a translation job

        Args:
            job_id: The job ID returned from start()

        Returns:
            Job status information
        """
        response = self._make_request("GET", f"translation/status/{job_id}")
        return TranslationStatus.model_validate(response)

    def translate(
        self,
        text: str,
        dialect: DialectLike,
        beam_size: int = 4,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> str:
        """
        Translate text and wait for completion

        Args:
            text: Text to translate to Swiss German
            dialect: Dialect code (e.g., 'vs' for Valais)
            beam_size: Beam size for translation (default: 4)
            poll_interval: Seconds between status checks (default: 1.0)
            timeout: Maximum seconds to wait (default: 60.0)

        Returns:
            The translated text

        Raises:
            PlapperiTimeoutError: If job doesn't complete within timeout
            PlapperiAPIError: If job fails or API error occurs
        """
        # Start the job
        job = self.start(text=text, dialect=dialect, beam_size=beam_size)

        # Poll for completion
        elapsed = 0.0
        while elapsed < timeout:
            status = self.status(job.job_id)

            if status.is_completed:
                if status.result and status.result.translation:
                    return status.result.translation
                raise ApiError(body="Job completed but no translation result found.")
            elif status.is_failed:
                raise ApiError(body=f"Translation job failed: {status.error}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        raise PlapperiTimeoutError(
            f"Translation job {job.job_id} did not complete within {timeout}s"
        )
