from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from .schemas import TaskRead
from .services import create_task, delete_task, get_task, list_tasks, update_task

tasks_router = APIRouter()


@tasks_router.get("")  # type: ignore[no-redef]
def list_tasks(tasks: Annotated[list[TaskRead], Depends(list_tasks)]) -> list[TaskRead]:
    """Retrieve a list of tasks."""
    return tasks


@tasks_router.get("/{task_id}")  # type: ignore[no-redef]
def get_task(task: Annotated[TaskRead, Depends(get_task)]) -> TaskRead:
    """Retrieve a task by its ID."""
    return task


@tasks_router.post("", status_code=status.HTTP_201_CREATED)  # type: ignore[no-redef]
def create_task(created_task: Annotated[TaskRead, Depends(create_task)]) -> TaskRead:
    """Create a new task."""
    return created_task


@tasks_router.patch("/{task_id}")  # type: ignore[no-redef]
def update_task(updated_task: Annotated[TaskRead, Depends(update_task)]) -> TaskRead:
    """Update an existing task and return updated task."""
    return updated_task


@tasks_router.delete(  # type: ignore[no-redef]
    "/{task_id}", dependencies=[Depends(delete_task)], status_code=status.HTTP_204_NO_CONTENT
)
def delete_task() -> None:
    """Delete a task by the task_id."""
