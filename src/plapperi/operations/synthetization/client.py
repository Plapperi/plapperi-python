import httpx

from plapperi.operations.base_client import BaseClient
from plapperi.types.job import Job
from plapperi.types.translation import TranslationStatus


class SynthetizationClient(BaseClient):
    """Client for synthetization operations"""

    def __init__(self, base_url: str, api_key: str, client: httpx.Client):
        super().__init__(base_url=base_url, api_key=api_key, client=client)

    def start(self, text: str, voice: str) -> Job:
        raise NotImplementedError()

    def status(self, job_id: str) -> TranslationStatus:
        raise NotImplementedError()

    def synth(
        self,
        text: str,
        voice: str,
        poll_interval: float = 1.0,
        timeout: float = 60.0,
    ) -> bytes:
        raise NotImplementedError()
