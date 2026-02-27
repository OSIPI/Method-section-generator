from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def normalize_response(data: dict) -> dict:
    """
    Remove volatile fields to ensure deterministic regression.
    """
    data.pop("nifti_slice_number", None)
    return data


def test_root_endpoint_regression(data_regression):
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    data_regression.check(data)


def test_dicom_invalid_file_returns_500(tmp_path):
    file_path = tmp_path / "invalid.txt"
    file_path.write_text("not a dicom")

    with open(file_path, "rb") as f:
        response = client.post(
            "/api/report/process/dicom",
            files={"dcm_files": ("invalid.txt", f, "text/plain")},
            data={"modality": "ASL"},
        )

    assert response.status_code == 500