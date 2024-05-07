from fastapi import APIRouter, FastAPI
from src.app.tasks.router import tasks_router
from starlette import status
from starlette.testclient import TestClient


def setup_test_client() -> TestClient:
    """Set up the test client for testing."""
    test_app = FastAPI()
    api_router = APIRouter()
    api_router.include_router(tasks_router, prefix="/tasks")
    test_app.include_router(api_router)

    return TestClient(test_app)


def test_list_tasks():
    """Test listing tasks."""
    resp = setup_test_client().get("/tasks?limit=101")

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json() == {
        "detail": [
            {
                "type": "less_than_equal",
                "loc": ["query", "limit"],
                "msg": "Input should be less than or equal to 100",
                "input": "101",
                "ctx": {"le": 100},
            }
        ]
    }
