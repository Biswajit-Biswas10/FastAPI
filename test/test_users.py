from .utils import *
from routers.users import get_db, get_current_user
from fastapi import status



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == "Biswajit"
    assert response.json()['email'] == "biswajit@test.com"
    assert response.json()['first_name'] == "Biswajit"
    assert response.json()['last_name'] == "Biswas"
    assert response.json()['role'] == "admin"
    assert response.json()['phone_number'] == "(111)-111-1111"


def test_change_password_success(test_user):
    response = client.put("/user/password", json={"password": "testpassword",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_invalid_current_user(test_user):
    response = client.put("/user/password", json={"password": "wrong_password",
                                                  "new_password": "newpassword"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on Password change'}


def test_change_phone_number_success(test_user):
    response = client.put("/user/phonenumber/999999")
    assert response.status_code == status.HTTP_204_NO_CONTENT
