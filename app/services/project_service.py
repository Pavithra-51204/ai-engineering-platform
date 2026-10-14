from uuid import UUID

from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse


class ProjectService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def create_project(self, project_data: ProjectCreate) -> ProjectResponse:
        return self._repository.create(project_data)

    def list_projects(self) -> list[ProjectResponse]:
        return self._repository.list_all()

    def get_project(self, project_id: UUID) -> ProjectResponse | None:
        return self._repository.get_by_id(project_id)
