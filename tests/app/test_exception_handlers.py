import pytest
from fastapi.exceptions import RequestValidationError
from src.app.exception_handlers import validation_exception_handler
from starlette import status
from starlette.responses import JSONResponse

_validation_exception_handler_test_cases = {
    "should convert RequestValidationError to JSONResponse": (
        RequestValidationError(
            errors=[
                {"loc": ("body", "description"), "msg": "required field"},
                {"loc": ("body", "is_completed"), "msg": "required field"},
            ]
        ),
        None,
        '{"detail":[{"message":"error location: body description, required field"},{"message":"error location: body is_completed, required field"}]}',
    ),
    "should raise TypeError if exception type is not RequestValidationError": (
        Exception("test exception"),
        (TypeError, "expected RequestValidationError, got Exception"),
        None,
    ),
}


@pytest.mark.parametrize(
    "exc,expected_exc,expected_response",
    _validation_exception_handler_test_cases.values(),
    ids=_validation_exception_handler_test_cases.keys(),
)
def test_validation_exception_handler(exc: Exception, expected_exc, expected_response: JSONResponse):
    """Test validation exception handler."""
    if expected_exc is None:
        resp = validation_exception_handler(None, exc)
        assert resp.body.decode("utf-8") == expected_response
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        return

    with pytest.raises(expected_exc[0]) as exc_info:
        validation_exception_handler(None, exc)
    assert str(exc_info.value) == expected_exc[1]
