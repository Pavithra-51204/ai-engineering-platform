from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


def get_project_service(
    db: Annotated[Session, Depends(get_db)],
) -> ProjectService:
    return ProjectService(
        repository=ProjectRepository(db),
        session=db,
    )


ProjectServiceDependency = Annotated[
    ProjectService,
    Depends(get_project_service),
]


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    service: ProjectServiceDependency,
) -> ProjectResponse:
    return service.create_project(project_data)


@router.get("", response_model=list[ProjectResponse])
@router.get("", response_model=list[ProjectResponse])
def list_projects(
    service: ProjectServiceDependency,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ProjectResponse]:
    return service.list_projects(
        limit=limit,
        offset=offset,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    service: ProjectServiceDependency,
) -> ProjectResponse:
    project = service.get_project(project_id)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project
