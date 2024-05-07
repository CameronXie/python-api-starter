import uuid
from typing import Self

from pydantic import BaseModel, model_validator


class TaskBase(BaseModel):

    """Represents a base class for tasks."""

    description: str
    is_completed: bool = False


class TaskRead(TaskBase):

    """Define and validate the structure of a Task object for read operations."""

    id: uuid.UUID


class TaskCreate(TaskBase):

    """Define and validate the input data for Task creation operations."""


class TaskUpdate(TaskBase):

    """Define and validate the input data for Task update operations."""

    description: str | None = None  # type: ignore[assignment]
    is_completed: bool | None = None  # type: ignore[assignment]

    @model_validator(mode="after")
    def validate_task(self) -> Self:
        """Validate method is used to check if the required fields are provided in the model instance."""
        if self.description is None and self.is_completed is None:
            raise ValueError("at least one field must be provided")
        return self
