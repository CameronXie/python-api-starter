from src.app.main import app
from starlette import status
from starlette.testclient import TestClient


def test_list_tasks_validation_error():
    """Test app validation error."""
    resp = TestClient(app).get("/v1/tasks?limit=123")

    assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json() == {
        "detail": [{"message": "error location: query limit, input should be less than or equal to 100"}]
    }
