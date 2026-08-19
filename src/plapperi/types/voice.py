from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from plapperi.types.dialect import Dialect


class VoiceGender(str, Enum):
    """Public gender label associated with a Plapperi voice."""

    FEMALE = "female"
    MALE = "male"


class Voice(BaseModel):
    """A voice available for Plapperi speech synthesis."""

    id: str
    name: str
    gender: VoiceGender
    supported_dialects: list[Dialect] = Field(alias="supportedDialects")

    model_config = ConfigDict(populate_by_name=True, use_enum_values=False)


class VoicesResponse(BaseModel):
    """Response returned by the voice catalogue endpoint."""

    voices: list[Voice]
