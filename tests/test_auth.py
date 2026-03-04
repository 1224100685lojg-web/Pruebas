class TestAuth:

   class TestAuth:

    def test_register(self, client):
        resp = client.post("/api/auth/register", json={
            "username": "testuser1",
            "email": "testuser1@test.com",
            "password": "Password123!"
        })

        # Si tu API retorna 201 al registrar:
        assert resp.status_code in [200, 201], resp.get_json()


    def test_login(self, client):
        # Primero registra
        client.post("/api/auth/register", json={
            "username": "loginuser1",
            "email": "loginuser1@test.com",
            "password": "Password123!"
        })

        # Luego login
        resp = client.post("/api/auth/login", json={
            "username": "loginuser1",
            "password": "Password123!"
        })

        assert resp.status_code == 200, resp.get_json()

        data = resp.get_json()

        # ✅ Tu API usa access_token
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 10

        # opcional: validar que venga el usuario
        assert "usuario" in data
        assert data["usuario"]["username"] == "loginuser1"