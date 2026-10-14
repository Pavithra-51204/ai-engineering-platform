from collections.abc import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.projects import get_project_service
from app.main import app
from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    repository = ProjectRepository()

    def override_project_service() -> ProjectService:
        return ProjectService(repository)

    app.dependency_overrides[get_project_service] = override_project_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_project(client: TestClient) -> None:
    response = client.post(
        "/api/v1/projects",
        json={
            "name": "Document Intelligence",
            "description": "Analyse engineering documents",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Document Intelligence"
    assert data["description"] == "Analyse engineering documents"
    assert "id" in data
    assert "created_at" in data


def test_create_project_without_description(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/projects",
        json={"name": "Document Intelligence"},
    )

    assert response.status_code == 201
    assert response.json()["description"] is None


def test_reject_project_name_that_is_too_short(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/projects",
        json={"name": "AI"},
    )

    assert response.status_code == 422


def test_reject_project_with_missing_name(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/projects",
        json={"description": "A project without a name"},
    )

    assert response.status_code == 422


def test_list_projects(client: TestClient) -> None:
    client.post(
        "/api/v1/projects",
        json={"name": "Project Alpha"},
    )
    client.post(
        "/api/v1/projects",
        json={"name": "Project Bravo"},
    )

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_existing_project(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/projects",
        json={"name": "Project Alpha"},
    )
    project_id = create_response.json()["id"]

    response = client.get(f"/api/v1/projects/{project_id}")

    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_get_nonexistent_project_returns_404(
    client: TestClient,
) -> None:
    nonexistent_id = uuid4()

    response = client.get(f"/api/v1/projects/{nonexistent_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_reject_invalid_project_id(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/projects/not-a-uuid")

    assert response.status_code == 422


def test_project_data_is_isolated_between_tests(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == []
