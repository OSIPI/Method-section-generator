from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bids_endpoint_requires_files():
    response = client.post(
        "/api/report/process/bids",
        data={"modality": "ASL"}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "No files provided for ASL processing."