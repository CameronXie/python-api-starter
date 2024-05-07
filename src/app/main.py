import logging

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from mangum import Mangum

from .api import api_router
from .config import settings
from .exception_handlers import validation_exception_handler

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)

app = FastAPI(title=settings.project_name, version=settings.version, redoc_url=None, root_path=settings.api_prefix)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(api_router)

handler = Mangum(app, lifespan="off")
