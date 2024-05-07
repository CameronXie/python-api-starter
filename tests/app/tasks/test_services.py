import uuid
from typing import ClassVar

import pytest
from fastapi import HTTPException
from moto import mock_aws
from pynamodb.exceptions import PutError
from src.app.tasks.models import Task
from src.app.tasks.schemas import TaskCreate, TaskRead, TaskUpdate
from src.app.tasks.services import create_task, delete_task, get_task, get_task_by_id, list_tasks, update_task

Task.Meta.table_name = "test-tasks-table"
Task.Meta.host = None


class TestServices:

    """Test tasks services."""

    @pytest.fixture(scope="function")
    def setup_test_data(self, request):
        """Create a test table."""
        with mock_aws():
            Task().create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
            if hasattr(request, "param"):
                for task in request.param:
                    task.save()
            yield
            Task().delete_table()

    get_task_by_id_test_cases: ClassVar = {
        "should retrieve task by id": (
            [
                Task(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False),
                Task(id="edd63ebf-fbc2-4691-bc0c-70a7f78cf894", description="description_2", is_completed=True),
            ],
            uuid.UUID("edd63ebf-fbc2-4691-bc0c-70a7f78cf894"),
            None,
            Task(id="edd63ebf-fbc2-4691-bc0c-70a7f78cf894", description="description_2", is_completed=True),
        ),
        "should raise HTTPException if task not found": (
            [],
            uuid.UUID("130f7f01-4e9a-468c-8daf-bdb6143331f7"),
            (HTTPException, "404: task not found"),
            None,
        ),
    }

    @mock_aws
    @pytest.mark.parametrize(
        "setup_test_data,task_id,expected_exc,expected_task",
        get_task_by_id_test_cases.values(),
        ids=get_task_by_id_test_cases.keys(),
        indirect=["setup_test_data"],
    )
    def test_get_task_by_id(self, setup_test_data, task_id: uuid.UUID, expected_exc: tuple | None, expected_task: Task):
        """Test get_task_by_id function."""
        if expected_exc is None:
            task = get_task_by_id(task_id)
            assert task.id == expected_task.id
            assert task.description == expected_task.description
            assert task.is_completed == expected_task.is_completed
            return

        with pytest.raises(expected_exc[0]) as exc_info:
            get_task_by_id(task_id)

        assert str(exc_info.value) == expected_exc[1]

    list_tasks_test_cases: ClassVar = {
        "should list first tasks when after_id is None and limit is 1": (
            [
                Task(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False),
                Task(id="edd63ebf-fbc2-4691-bc0c-70a7f78cf894", description="description_2", is_completed=True),
            ],
            (None, 1),
            None,
            [
                TaskRead(
                    id=uuid.UUID("0c977aea-c1e3-4f60-b27f-2ba7e24bcca4"),
                    description="description_1",
                    is_completed=False,
                )
            ],
        ),
        "should list second tasks when after_id is first task id and limit is 1": (
            [
                Task(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False),
                Task(id="edd63ebf-fbc2-4691-bc0c-70a7f78cf894", description="description_2", is_completed=True),
            ],
            (uuid.UUID("edd63ebf-fbc2-4691-bc0c-70a7f78cf894"), 1),
            None,
            [TaskRead(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False)],
        ),
        "should raise HTTPException if after_id is invalid": (
            [],
            (uuid.UUID("edd63ebf-fbc2-4691-bc0c-70a7f78cf894"), None),
            (HTTPException, "400: invalid task id"),
            None,
        ),
    }

    @mock_aws
    @pytest.mark.parametrize(
        "setup_test_data,opts,expected_exc,expected_tasks",
        list_tasks_test_cases.values(),
        ids=list_tasks_test_cases.keys(),
        indirect=["setup_test_data"],
    )
    def test_list_tasks(
        self,
        setup_test_data,
        opts: tuple,
        expected_exc: tuple | None,
        expected_tasks: list[TaskRead],
    ):
        """Test list_tasks function."""
        if expected_exc is None:
            tasks = list_tasks(*opts)
            for idx in range(len(tasks)):
                assert tasks[idx] == expected_tasks[idx]
            return

        with pytest.raises(expected_exc[0]) as exc_info:
            list_tasks(*opts)

        assert str(exc_info.value) == expected_exc[1]

    def test_get_task(self):
        """Test get_task function."""
        assert get_task(
            Task(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False)
        ) == TaskRead(
            id=uuid.UUID("0c977aea-c1e3-4f60-b27f-2ba7e24bcca4"), description="description_1", is_completed=False
        )

    create_task_test_cases: ClassVar = {
        "should create a new task": (
            TaskCreate(description="description_1", is_completed=True),
            ("description_1", True),
        )
    }

    @mock_aws
    @pytest.mark.parametrize(
        "new_task,expected_task",
        create_task_test_cases.values(),
        ids=create_task_test_cases.keys(),
    )
    def test_create_task(self, setup_test_data, new_task: TaskCreate, expected_task: tuple):
        """Test create_task function."""
        created_task = create_task(new_task)

        assert created_task.description == expected_task[0]
        assert created_task.is_completed == expected_task[1]
        assert created_task == get_task(get_task_by_id(created_task.id))

    update_task_cases: ClassVar = {
        "should update task by id": (
            [
                Task(
                    id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4",
                    description="description_1",
                    is_completed=False,
                    version=1,
                ),
            ],
            (
                Task(
                    id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4",
                    description="description_1",
                    is_completed=False,
                    version=1,
                ),
                TaskUpdate(description="description_2", is_completed=True),
            ),
            TaskRead(
                id=uuid.UUID("0c977aea-c1e3-4f60-b27f-2ba7e24bcca4"), description="description_2", is_completed=True
            ),
        )
    }

    @mock_aws
    @pytest.mark.parametrize(
        "setup_test_data",
        [
            [
                Task(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False),
                Task(id="edd63ebf-fbc2-4691-bc0c-70a7f78cf894", description="description_2", is_completed=True),
            ]
        ],
        indirect=True,
    )
    def test_update_task_success(self, setup_test_data):
        """Test successfully update task with update_task function."""
        description = "description_3"
        is_completed = False

        updated_task = update_task(
            get_task_by_id(uuid.UUID("edd63ebf-fbc2-4691-bc0c-70a7f78cf894")),
            TaskUpdate(description=description, is_completed=is_completed),
        )

        assert updated_task.description == description
        assert updated_task.is_completed == is_completed

    @mock_aws
    @pytest.mark.parametrize(
        "setup_test_data",
        [
            [
                Task(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False),
                Task(id="edd63ebf-fbc2-4691-bc0c-70a7f78cf894", description="description_2", is_completed=True),
            ]
        ],
        indirect=True,
        ids=["should update task"],
    )
    def test_update_task(self, setup_test_data):
        """Test successfully update task with update_task function."""
        task = get_task_by_id(uuid.UUID("edd63ebf-fbc2-4691-bc0c-70a7f78cf894"))
        task2 = get_task_by_id(uuid.UUID("edd63ebf-fbc2-4691-bc0c-70a7f78cf894"))

        description = "description_3"
        is_completed = False

        updated_task = update_task(task, TaskUpdate(description=description, is_completed=is_completed))

        assert updated_task.id == get_task(task).id
        assert updated_task.description == description
        assert updated_task.is_completed == is_completed

        # test optimistic locking
        with pytest.raises(PutError) as exc_info:
            update_task(task2, TaskUpdate(description=description, is_completed=is_completed))

        assert "ConditionalCheckFailedException" in str(exc_info.value)

    @mock_aws
    @pytest.mark.parametrize(
        "setup_test_data",
        [
            [
                Task(id="0c977aea-c1e3-4f60-b27f-2ba7e24bcca4", description="description_1", is_completed=False),
                Task(id="edd63ebf-fbc2-4691-bc0c-70a7f78cf894", description="description_2", is_completed=True),
            ]
        ],
        indirect=True,
        ids=["should delete task"],
    )
    def test_delete_task(self, setup_test_data):
        """Test delete_task function."""
        delete_task(get_task_by_id(uuid.UUID("edd63ebf-fbc2-4691-bc0c-70a7f78cf894")))
        assert list_tasks(None, 10) == [
            TaskRead(
                id=uuid.UUID("0c977aea-c1e3-4f60-b27f-2ba7e24bcca4"), description="description_1", is_completed=False
            )
        ]
