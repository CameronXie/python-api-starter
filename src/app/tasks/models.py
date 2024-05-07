from pynamodb.attributes import BooleanAttribute, UnicodeAttribute, VersionAttribute
from pynamodb.models import Model

from ..config import settings


class Task(Model):

    """Task DynamoDB model."""

    class Meta:

        """Task model configuration."""

        host = settings.db_host
        table_name = settings.db_tasks_table

    id = UnicodeAttribute(hash_key=True)
    description = UnicodeAttribute(null=True)
    is_completed = BooleanAttribute(default=False)
    version = VersionAttribute()
