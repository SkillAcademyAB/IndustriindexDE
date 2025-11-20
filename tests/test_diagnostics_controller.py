from fastapi.testclient import TestClient
from source.__main__ import app
from source.controllers.diagnostics import healthcheck_endpoint


client = TestClient(app)


async def test_healthcheck_endpoint_function():
    """
    Test the healthcheck_endpoint function directly.
    """
    result = await healthcheck_endpoint()
    assert result == {"message": "IndustriIndex Server online!"}
    assert "message" in result
    assert isinstance(result["message"], str)


def test_healthcheck_endpoint_via_api():
    """
    Test the /healthcheck endpoint via the FastAPI TestClient.
    """
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"message": "IndustriIndex Server online!"}


def test_healthcheck_endpoint_response_structure():
    """
    Test that the response has the expected structure.
    """
    response = client.get("/healthcheck")
    data = response.json()
    assert "message" in data
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0
