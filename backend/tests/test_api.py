import pytest

def test_signup_and_login(client):
    # 1. Signup Request
    signup_payload = {
        "email": "newstudent@school.com",
        "password": "strongpassword123",
        "role": "student",
        "masked_name": "성명 마스킹",
        "grade": "2학년",
        "school_type": "일반고",
        "region": "경기"
    }
    response = client.post("/api/v1/auth/signup", json=signup_payload)
    assert response.status_code == 201
    assert response.json()["email"] == "newstudent@school.com"

    # 2. Login Request
    login_payload = {
        "email": "newstudent@school.com",
        "password": "strongpassword123"
    }
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_unauthorized_access(client):
    # Call records upload without Authorization header
    response = client.get("/api/v1/records/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_FAILED"
