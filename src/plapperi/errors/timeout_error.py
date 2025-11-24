import typing

from .api_error import ApiError


class PlapperiTimeoutError(ApiError):
    def __init__(
        self, body: typing.Any, headers: typing.Optional[typing.Dict[str, str]] = None
    ):
        super().__init__(status_code=408, headers=headers, body=body)
