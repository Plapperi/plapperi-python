import typing

import httpx

from plapperi.errors.api_error import ApiError


class BaseClient:
    def __init__(self, base_url: str, api_key: str, client: httpx.Client):
        self.base_url = base_url
        self.api_key = api_key
        self.client = client

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict[str, typing.Any]:
        """Make an API request with error handling"""
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"ApiKey {self.api_key}"

        try:
            response = self.client.request(
                method=method,
                url=f"{self.base_url}/{endpoint}",
                headers=headers,
                **kwargs,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ApiError(
                body=f"API request failed: {e.response.status_code} - {e.response.text}",
                status_code=e.response.status_code,
            )
        except httpx.RequestError as e:
            raise ApiError(body=f"Request error: {str(e)}")
