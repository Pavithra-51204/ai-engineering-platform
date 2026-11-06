from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project
from app.schemas.project import ProjectCreate


class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, project_data: ProjectCreate) -> Project:
        project = Project(
            name=project_data.name,
            description=project_data.description,
        )

        self._session.add(project)
        self._session.flush()
        self._session.refresh(project)

        return project

    def list_all(
        self,
        limit: int = 10,
        offset: int = 0,
    ) -> list[Project]:
        statement = (
            select(Project)
            .order_by(Project.created_at.desc(), Project.id.desc())
            .limit(limit)
            .offset(offset)
        )

        return list(self._session.scalars(statement).all())

    def get_by_id(self, project_id: UUID) -> Project | None:
        return self._session.get(Project, project_id)
