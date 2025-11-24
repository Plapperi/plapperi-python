from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class JobType(str, Enum):
    """Type of job"""

    TRANSLATION = "translation"
    SYNTHETIZATION = "synthetization"


class JobStatus(str, Enum):
    """Status of a job"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """Represents a job in the Plapperi API"""

    job_id: str = Field(..., alias="jobId")
    job_type: JobType = Field(..., alias="jobType")
    status: JobStatus

    model_config = ConfigDict(populate_by_name=True, use_enum_values=False)
