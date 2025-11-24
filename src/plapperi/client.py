import os

import httpx

from plapperi.operations.synthetization.client import SynthetizationClient
from plapperi.operations.translation.client import TranslationClient


class Plapperi:
    """
    Main client for the Plapperi.ch API

    Example:
        >>> from plapperi import Plapperi
        >>> client = Plapperi(api_key="your-api-key")
        >>> translated = client.translation.translate(
        ...     text="Die Bevölkerung habe genug von den vielen Touristen.",
        ...     dialect="vs"
        ... )
        >>> print(translated)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.plapperi.ch",
        timeout: float = 30.0,
    ):
        """
        Initialize the Plapperi client

        Args:
            api_key: Your Plapperi.ch API key
            base_url: Base URL for the API (default: https://api.plapperi.ch)
            timeout: Request timeout in seconds (default: 30.0)
        """
        if api_key is None:
            api_key = os.environ.get("PLAPPERI_API_KEY")

        if api_key is None:
            raise Exception(
                "The api_key client option must be set either by passing api_key to the client or by setting the PLAPPERI_API_KEY environment variable"
            )

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

        self._client = httpx.Client(timeout=timeout)

        self.translation = TranslationClient(self.base_url, self.api_key, self._client)
        self.synthetization = SynthetizationClient(
            self.base_url, self.api_key, self._client
        )

    def close(self):
        """Close the HTTP client"""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
