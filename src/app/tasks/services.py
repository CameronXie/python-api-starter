from typing import Annotated, Any
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, Query
from pynamodb.exceptions import DoesNotExist
from starlette import status

from .models import Task
from .schemas import TaskCreate, TaskRead, TaskUpdate


def get_task_by_id(task_id: UUID) -> Task:
    """Retrieve a task by its ID.

    :param task_id: The ID of the task.
    :type task_id: UUID
    :return: The task with the given ID.
    :rtype: Task
    :raises HTTPException: If the task does not exist.
    :raises Exception: If there is an error retrieving the task.
    """
    try:
        return Task.get(str(task_id))
    except DoesNotExist as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found") from exc


def list_tasks(after_id: UUID | None = None, limit: int = Query(default=50, ge=1, le=100)) -> list[TaskRead]:
    """List tasks.

    :param after_id: UUID of the task to start listing from (optional)
    :param limit: Maximum number of tasks to list (default: 50, min: 1, max: 100)
    :return: List of TaskRead objects representing the tasks
    :raises HTTPException: If the provided after_id is invalid
    """
    scan_opt: dict[str, Any] = {"limit": limit}
    if after_id is not None:
        try:
            scan_opt["last_evaluated_key"] = {"id": {"S": get_task_by_id(after_id).id}}
        except HTTPException as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid task id") from exc

    return [TaskRead(**task.attribute_values) for task in Task.scan(**scan_opt)]


def get_task(task: Annotated[Task, Depends(get_task_by_id)]) -> TaskRead:
    """Retrieve single task by task id.

    :param task: The task object to retrieve.
    :return: The read-only representation of the task.
    """
    return TaskRead(**task.attribute_values)


def create_task(task: TaskCreate) -> TaskRead:
    """Create a new task.

    :param task: A TaskCreate object representing the task to be created.
    :return: A TaskRead object representing the created task.
    """
    db_task = Task(
        id=str(uuid4()),
        description=task.description,
        is_completed=task.is_completed,
    )
    db_task.save()
    return TaskRead(**db_task.attribute_values)


def update_task(current_task: Annotated[Task, Depends(get_task_by_id)], task: TaskUpdate) -> TaskRead:
    """Update a task with the provided information.

    :param current_task: The current task to be updated.
    :type current_task: Task
    :param task: The updated task.
    :type task: TaskUpdate
    :return: The updated task.
    :rtype: TaskRead
    """
    if task.description is not None:
        current_task.description = task.description
    if task.is_completed is not None:
        current_task.is_completed = task.is_completed
    current_task.save()
    return TaskRead(**current_task.attribute_values)


def delete_task(current_task: Annotated[Task, Depends(get_task_by_id)]) -> None:
    """Delete a task.

    :param current_task: The task to be deleted.
    :return: None
    """
    current_task.delete()
