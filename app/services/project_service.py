from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepository,
        session: Session,
    ) -> None:
        self._repository = repository
        self._session = session

    def create_project(self, project_data: ProjectCreate) -> Project:
        try:
            project = self._repository.create(project_data)
            self._session.commit()
            return project

        except SQLAlchemyError:
            self._session.rollback()
            raise

    def list_projects(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Project]:
        return self._repository.list_all(
            limit=limit,
            offset=offset,
        )

    def get_project(self, project_id: UUID) -> Project | None:
        return self._repository.get_by_id(project_id)
