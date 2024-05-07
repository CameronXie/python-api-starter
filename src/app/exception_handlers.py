from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from .api import ErrorDetail, ErrorResponse


def validation_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle validation exceptions and return a JSON response.

    :param _: The request object (unused).
    :param exc: The validation exception to handle.
    :return: A JSON response with the error details.
    """
    if not isinstance(exc, RequestValidationError):
        raise TypeError(f"expected RequestValidationError, got {type(exc).__name__}")

    details = [
        ErrorDetail(message=f"error location: {' '.join(err['loc'])}, {err['msg']}".lower()) for err in exc.errors()
    ]
    return JSONResponse(
        content=jsonable_encoder(ErrorResponse(detail=details)),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
