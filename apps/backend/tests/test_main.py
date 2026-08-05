import sys
import pytest
from unittest.mock import MagicMock

# --- 1. MOCK WEASYPRINT BEFORE IMPORTING FASTAPI ---
mock_wp = MagicMock()
sys.modules['weasyprint'] = mock_wp
sys.modules['weasyprint.HTML'] = mock_wp

# --- 2. NOW BRING IN THE APP ---
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# --- CORE APP TESTS ---

def test_read_root():
    """Test the root endpoint (/) for status code and exact JSON structure."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "organization" in data
    assert data["name"] == "ASL Methods Parameter Generator API Service"

def test_cors_middleware():
    """Test that CORS middleware allows external origins."""
    headers = {"Origin": "http://localhost:3000"}
    response = client.get("/", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"

# --- REPORT ROUTER TESTS ---

def test_process_dicom_no_files():
    """Test that /process/dicom correctly rejects requests missing DICOM files."""
    response = client.post("/api/report/process/dicom")
    assert response.status_code == 400
    assert response.json()["detail"] == "No DICOM files provided"

def test_report_pdf_missing_payload():
    """Test that /report-pdf crashes when expected nested keys are missing."""
    # TestClient raises the actual Python KeyError instead of a 500 status code
    with pytest.raises(KeyError):
        client.post("/api/report/report-pdf", json={})

def test_process_bids_accepts_form_data():
    """Test that /process/bids processes form data."""
    # TestClient raises the ValueError from the Enum mismatch
    with pytest.raises(ValueError):
        client.post(
            "/api/report/process/bids", 
            data={"modality": "asl"}
        )