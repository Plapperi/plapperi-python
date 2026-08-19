import typing

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from plapperi.types.dialect import (
    SYNTHETIZATION_DIALECTS,
    normalize_synthetization_dialect,
)
from plapperi.types.job import JobStatus, JobType


MULTI_SPEAKER_IDS = ("speaker-1", "speaker-2")
MULTI_SPEAKER_DIALECTS = SYNTHETIZATION_DIALECTS


class Speaker(BaseModel):
    """Voice and dialect assigned to one side of a two-speaker dialogue."""

    id: typing.Literal["speaker-1", "speaker-2"]
    voice: str = Field(..., min_length=1)
    dialect: str

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("voice")
    @classmethod
    def normalize_voice(cls, value: str) -> str:
        value = value.strip().lower()
        if not value:
            raise ValueError("Voice cannot be empty")
        return value

    @field_validator("dialect", mode="before")
    @classmethod
    def validate_dialect(cls, value: typing.Any) -> str:
        normalized = getattr(value, "value", value)
        if not isinstance(normalized, str):
            raise ValueError("Dialect must be a string or Dialect value")
        try:
            return normalize_synthetization_dialect(normalized.strip())
        except ValueError as exc:
            raise ValueError(
                f"Multi-speaker dialect must be one of {MULTI_SPEAKER_DIALECTS}"
            ) from exc


class DialogueTurn(BaseModel):
    """One ordered spoken turn in a two-speaker dialogue."""

    speaker_id: typing.Literal["speaker-1", "speaker-2"] = Field(
        ..., alias="speakerId"
    )
    text: str = Field(..., min_length=1, max_length=1000)

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Dialogue text cannot be empty")
        return value


class MultiSpeakerRequest(BaseModel):
    speakers: list[Speaker]
    turns: list[DialogueTurn] = Field(..., min_length=1, max_length=100)

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_dialogue(self):
        if len(self.speakers) != 2:
            raise ValueError("Exactly two speaker profiles are required")
        if {speaker.id for speaker in self.speakers} != set(MULTI_SPEAKER_IDS):
            raise ValueError("Speaker IDs must be speaker-1 and speaker-2")
        if len({speaker.voice for speaker in self.speakers}) != 2:
            raise ValueError("The two speakers must use distinct voices")
        if {turn.speaker_id for turn in self.turns} != set(MULTI_SPEAKER_IDS):
            raise ValueError("Both speakers must have at least one dialogue turn")
        if sum(len(turn.text) for turn in self.turns) > 5000:
            raise ValueError("Dialogue cannot exceed 5000 spoken characters")
        return self


class MultiSpeakerAudio(BaseModel):
    content_type: str = Field(default="audio/wav", alias="contentType")
    playback_url: str = Field(..., alias="playbackUrl")
    download_url: str = Field(..., alias="downloadUrl")
    url_expires_at: str = Field(..., alias="urlExpiresAt")
    duration_seconds: typing.Optional[float] = Field(None, alias="durationSeconds")
    size_bytes: typing.Optional[int] = Field(None, alias="sizeBytes")

    model_config = ConfigDict(populate_by_name=True)


class MultiSpeakerResult(BaseModel):
    audio: MultiSpeakerAudio

    model_config = ConfigDict(populate_by_name=True)


class MultiSpeakerStatus(BaseModel):
    job_id: str = Field(default="", alias="jobId")
    job_type: JobType = Field(default=JobType.MULTI_SPEAKER, alias="jobType")
    status: JobStatus
    result: typing.Optional[MultiSpeakerResult] = None
    error: typing.Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, use_enum_values=False)

    @field_validator("result", mode="before")
    @classmethod
    def normalize_empty_result(cls, value: typing.Any):
        """Treat the backend's in-progress result placeholder as no result."""
        if isinstance(value, dict) and not value:
            return None
        return value

    @property
    def is_completed(self) -> bool:
        return self.status == JobStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.status == JobStatus.FAILED

    @property
    def is_pending(self) -> bool:
        return self.status == JobStatus.PENDING

    @property
    def is_processing(self) -> bool:
        return self.status == JobStatus.PROCESSING
