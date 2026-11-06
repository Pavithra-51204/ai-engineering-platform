import os
from collections.abc import Generator
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.database import Base, get_db
from app.main import app
from app.models import Project  # noqa: F401

load_dotenv()


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    database_url = os.environ["TEST_DATABASE_URL"]

    engine = create_engine(
        database_url,
        pool_pre_ping=True,
    )

    Base.metadata.create_all(bind=engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()

    test_session_local = sessionmaker(
        bind=connection,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    session = test_session_local()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
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


def test_list_projects_with_limit(client: TestClient) -> None:
    for index in range(5):
        client.post(
            "/api/v1/projects",
            json={"name": f"Project {index}"},
        )

    response = client.get("/api/v1/projects?limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_projects_with_offset(client: TestClient) -> None:
    for index in range(5):
        client.post(
            "/api/v1/projects",
            json={"name": f"Project {index}"},
        )

    response = client.get("/api/v1/projects?limit=2&offset=2")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_projects_rejects_invalid_limit(client: TestClient) -> None:
    response = client.get("/api/v1/projects?limit=0")

    assert response.status_code == 422


def test_list_projects_rejects_negative_offset(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/projects?offset=-1")

    assert response.status_code == 422


def test_list_projects_rejects_limit_above_maximum(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/projects?limit=101")

    assert response.status_code == 422
