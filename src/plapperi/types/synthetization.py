import typing

from pydantic import BaseModel, ConfigDict, Field, field_validator

from plapperi.types.job import JobStatus, JobType


class SynthetizationRequest(BaseModel):
    """Request payload for synthetization"""

    text: str = Field(..., min_length=1)
    voice: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Text cannot be empty or whitespace only")
        return v


class SynthetizationResult(BaseModel):
    """Result of a synthetization job"""

    audio_wav_b64: typing.Optional[str] = None
    sr: typing.Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class SynthetizationStatus(BaseModel):
    """Status of a synthetization job"""

    job_id: str = Field(default="", alias="jobId")
    job_type: JobType = Field(default=JobType.SYNTHETIZATION, alias="jobType")
    status: JobStatus
    result: typing.Optional[SynthetizationResult] = None
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
