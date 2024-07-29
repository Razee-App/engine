import sys
import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

client = TestClient(app)


def test_upload():
    # Create a temporary file to upload
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test content")
        temp_file.seek(0)  # Move cursor to the start of the file

        # Open the file in read-binary mode for the upload
        with open(temp_file.name, 'rb') as file:
            response = client.post(
                "/api/v1/test-upload",
                files={"file": (temp_file.name, file, "text/plain")}
            )

    # Clean up the temporary file
    os.remove(temp_file.name)

    assert response.status_code == 200
    assert "message" in response.json()
    print(response.json())


if __name__ == "__main__":
    pytest.main()
