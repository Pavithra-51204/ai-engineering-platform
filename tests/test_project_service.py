from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.project import ProjectCreate
from app.services.project_service import ProjectService


def test_create_project_rolls_back_when_database_fails() -> None:
    repository = MagicMock()
    session = MagicMock()

    repository.create.side_effect = SQLAlchemyError("Database error")

    service = ProjectService(
        repository=repository,
        session=session,
    )

    project_data = ProjectCreate(
        name="Test Project",
        description="Testing rollback",
    )

    with pytest.raises(SQLAlchemyError):
        service.create_project(project_data)

    session.rollback.assert_called_once()
    session.commit.assert_not_called()
