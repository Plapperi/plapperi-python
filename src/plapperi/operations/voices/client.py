import httpx

from plapperi.operations.base_client import BaseClient
from plapperi.types.voice import Voice, VoicesResponse


class VoicesClient(BaseClient):
    """Client for the available speech-synthesis voice catalogue."""

    def __init__(self, base_url: str, api_key: str, client: httpx.Client):
        super().__init__(base_url=base_url, api_key=api_key, client=client)

    def list(self) -> list[Voice]:
        """List the current Studio voices and their supported dialects."""
        response = self._make_request("GET", "voices")
        return VoicesResponse.model_validate(response).voices
