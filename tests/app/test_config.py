import pytest
from pydantic import ValidationError
from src.app.config import Settings

_settings_test_cases = {
    "should load settings from environment variables": (
        {"DEBUG": "true", "DB_HOST": "http://dynamodb:8000", "DB_TASKS_TABLE": "test_tasks"},
        Settings(
            project_name="Todo List",
            api_prefix="/v1",
            debug=True,
            db_host="http://dynamodb:8000",
            db_tasks_table="test_tasks",
        ),
        None,
    ),
    "should raise ValidationError if environment variables missing": (
        {"DEBUG": "true", "DB_HOST": "http://dynamodb:8000"},
        Settings(debug=True, db_host="http://dynamodb:8000", db_tasks_table="test_tasks"),
        ValidationError,
    ),
}


@pytest.mark.parametrize(
    "setup_env,expected_settings,expected_exc",
    _settings_test_cases.values(),
    ids=_settings_test_cases.keys(),
    indirect=["setup_env"],
)
def test_settings(setup_env, expected_settings, expected_exc: Exception):
    """Test settings."""
    if expected_exc is None:
        assert Settings() == expected_settings
        return

    with pytest.raises(expected_exc):
        Settings()
