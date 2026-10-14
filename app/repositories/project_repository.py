from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.project import ProjectCreate, ProjectResponse


class ProjectRepository:
    def __init__(self) -> None:
        self._projects: dict[UUID, ProjectResponse] = {}

    def create(self, project_data: ProjectCreate) -> ProjectResponse:
        project = ProjectResponse(
            id=uuid4(),
            name=project_data.name,
            description=project_data.description,
            created_at=datetime.now(UTC),
        )

        self._projects[project.id] = project
        return project

    def list_all(self) -> list[ProjectResponse]:
        return list(self._projects.values())

    def get_by_id(self, project_id: UUID) -> ProjectResponse | None:
        return self._projects.get(project_id)
