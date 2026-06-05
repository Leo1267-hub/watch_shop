def test_main_page_loads(client):
    response = client.get("/main")
    assert response.status_code == 200


def test_login_page_loads(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_register_page_loads(client):
    response = client.get("/register")
    assert response.status_code == 200


def test_compare_page_loads(client):
    response = client.get("/compare")
    assert response.status_code == 200


def test_seller_page_requires_login(client):
    response = client.get("/seller")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_page_requires_login(client):
    response = client.get("/admin")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_page_requires_buyer_login(client):
    response = client.get("/profile")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
