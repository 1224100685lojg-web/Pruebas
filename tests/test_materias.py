import uuid

class TestMaterias:

    def _materia_payload(self):
        code = uuid.uuid4().hex[:6].upper()
        return {
            "clave": f"MAT{code}",
            "nombre": f"Materia {code}",
            "creditos": 5
        }

    def test_crear_materia(self, client, auth_headers):
        payload = self._materia_payload()
        resp = client.post("/api/materias/", json=payload, headers=auth_headers)
        assert resp.status_code in (200, 201), resp.get_json()

    def test_listar_materias(self, client, auth_headers):
        client.post("/api/materias/", json=self._materia_payload(), headers=auth_headers)

        resp = client.get("/api/materias/", headers=auth_headers)
        assert resp.status_code == 200, resp.get_json()

        data = resp.get_json()
        assert "materias" in data
        assert isinstance(data["materias"], list)