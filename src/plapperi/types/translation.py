import typing

from pydantic import BaseModel, ConfigDict, Field, field_validator

from plapperi.types.dialect import Dialect
from plapperi.types.job import JobStatus, JobType


class TranslationRequest(BaseModel):
    """Request payload for translation"""

    text: str = Field(..., min_length=1)
    dialect: Dialect
    beam_size: int = Field(default=4, ge=1, le=8)

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v


class TranslationResult(BaseModel):
    """Result of a translation job"""

    translation: typing.Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class TranslationStatus(BaseModel):
    """Status of a translation job"""

    job_id: str = Field(default="", alias="jobId")
    job_type: JobType = Field(default=JobType.TRANSLATION, alias="jobType")
    status: JobStatus
    result: typing.Optional[TranslationResult] = None
    error: typing.Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, use_enum_values=False)

    @property
    def is_completed(self) -> bool:
        """Check if job is completed"""
        return self.status == JobStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if job failed"""
        return self.status == JobStatus.FAILED

    @property
    def is_pending(self) -> bool:
        """Check if job is pending"""
        return self.status == JobStatus.PENDING

    @property
    def is_processing(self) -> bool:
        """Check if job is processing"""
        return self.status == JobStatus.PROCESSING
