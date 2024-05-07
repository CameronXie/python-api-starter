import os

import pytest


@pytest.fixture
def setup_env(request):
    """Set up the environment variables with the given parameters."""
    old_env = os.environ.copy()
    os.environ.clear()
    os.environ.update(request.param)
    yield
    os.environ.clear()
    os.environ.update(old_env)
