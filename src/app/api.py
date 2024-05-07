from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from .tasks.router import tasks_router


class ErrorDetail(BaseModel):

    """Error detail."""

    message: str


class ErrorResponse(BaseModel):

    """Error response.

    :param detail: A list of ErrorDetail objects representing additional error details. It can be None.
    """

    detail: list[ErrorDetail] | None = None


api_router = APIRouter(
    default_response_class=JSONResponse,
)

api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
