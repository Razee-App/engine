import sys
import os
import tempfile
import pytest

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload():
    # Create a temporary file to upload
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"Test content")
        temp_file.seek(0)  # Move cursor to the start of the file

        # Open the file in read-binary mode for the upload
        with open(temp_file.name, 'rb') as file:
            response = client.post(
                "/api/test-upload",
                files={"file": (temp_file.name, file, "text/plain")}
            )
    
    # Clean up the temporary file
    os.remove(temp_file.name)

    assert response.status_code == 200
    assert "message" in response.json()
    print(response.json())

if __name__ == "__main__":
    pytest.main()
