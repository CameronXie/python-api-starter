from importlib.metadata import version

from pydantic_settings import BaseSettings

MODULE_NAME = "python_api_starter"


class Settings(BaseSettings):

    """project settings Class."""

    project_name: str = "Todo List"
    api_prefix: str = "/v1"
    debug: bool = False
    db_host: str | None = None
    db_tasks_table: str

    @property
    def version(self) -> str:
        """Returns the version of the module."""
        try:
            return version(MODULE_NAME)
        except (ImportError, AttributeError):
            return "0.0.0"


settings = Settings()  # type: ignore[call-arg]
