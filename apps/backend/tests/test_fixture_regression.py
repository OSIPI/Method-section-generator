import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

FIXTURE_DIR = os.path.join(
    os.path.dirname(__file__),
    "fixtures",
    "real_sample"
)

def test_real_asl_fixture_regression(data_regression):
    sample_nifti_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "app",
        "utils",
        "sample_nifti.nii.gz"
    )

    with open(os.path.join(FIXTURE_DIR, "sub-Sub1_asl.json"), "rb") as f_asl, \
         open(os.path.join(FIXTURE_DIR, "sub-Sub1_m0scan.json"), "rb") as f_m0, \
         open(os.path.join(FIXTURE_DIR, "sub-Sub1_aslcontext.tsv"), "rb") as f_tsv, \
         open(sample_nifti_path, "rb") as f_nifti:

        response = client.post(
            "/api/report/process/bids",
            data={"modality": "ASL"},
            files=[
                ("files", ("sub-Sub1_asl.json", f_asl, "application/json")),
                ("files", ("sub-Sub1_m0scan.json", f_m0, "application/json")),
                ("files", ("sub-Sub1_aslcontext.tsv", f_tsv, "text/tab-separated-values")),
                ("nifti_file", ("sample_nifti.nii.gz", f_nifti, "application/octet-stream")),
            ],
        )

    assert response.status_code == 200

    data = response.json()
    data.pop("nifti_slice_number", None)

    data_regression.check(data)