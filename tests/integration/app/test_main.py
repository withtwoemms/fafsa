import httpx
import pytest
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs


@pytest.fixture(scope="session")
def fafsa_container():
    """Start FastAPI vault container for integration tests (no context manager)."""
    image_name = "eobi-app:latest"

    container = (
        DockerContainer(image_name)
        .with_exposed_ports(8888)
        .with_env("APP_ENV", "testing")
    )

    # --- Start the container ---
    container.start()
    wait_for_logs(container, "Application startup complete.", timeout=30)
    host = container.get_container_host_ip()
    port = container.get_exposed_port(8888)
    base_url = f"http://{host}:{port}"
    print(f"Started {image_name} on {base_url}")

    yield base_url

    print(f"Stopping container {image_name}")
    container.stop()


def test_health_endpoint(fafsa_container):
    """Test the /health endpoint of the FAFSA application."""
    base_url = fafsa_container
    r = httpx.get(f"{base_url}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_validate_endpoint(fafsa_container):
    """Test the "/validate" endpoint with a sample FAFSA application."""
    base_url = fafsa_container
    sample_application = {
        "studentInfo": {
            "firstName": "John",
            "lastName": "Doe",
            "ssn": "123456789",
            "dateOfBirth": "2000-01-01",
        },
        "household": {
            "numberInHousehold": 4,
            "numberInCollege": 2
        },
        "income": {
            "studentIncome": 15000,
            "parentIncome": 60000
        },
        "spouseInfo": None,
        "stateOfResidence": "CA",
        "dependencyStatus": "dependent",
        "maritalStatus": "single"
    }

    r = httpx.post(f"{base_url}/validate", json=sample_application)
    assert r.status_code == 200
    response_data = r.json()
    assert response_data["valid"] is True
    assert response_data["errors"] == []
    assert response_data["warnings"] == []
    assert response_data["passed"] != []
