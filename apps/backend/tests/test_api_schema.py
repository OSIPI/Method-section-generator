from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bids_endpoint_returns_expected_schema():
    response = client.post(
        "/api/report/process/bids",
        data={"modality": "ASL"}
    )

    assert response.status_code == 200
    data = response.json()

    expected_keys = {
        "basic_report",
        "extended_report",
        "asl_parameters",
        "errors",
        "warnings",
    }

    assert expected_keys.issubset(data.keys())