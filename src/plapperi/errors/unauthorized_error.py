import typing

from .api_error import ApiError


class PlapperiUnauthorizedError(ApiError):
    def __init__(
        self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None
    ):
        super().__init__(status_code=401, headers=headers, body=body)
