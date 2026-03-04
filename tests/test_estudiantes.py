class TestEstudiantes:

    def _get_id_from_post(self, resp):
        # Si algo sale raro, esto te lo muestra
        assert resp.is_json, resp.data

        data = resp.get_json()

        # ✅ Tu API a veces devuelve {"estudiante": {...}} y a veces devuelve {...} directo
        est = data.get("estudiante", data)
        est_id = est.get("id")

        assert est_id is not None, data
        return est_id, data

    def test_crear_estudiante(self, client, estudiante_data):
        resp = client.post("/api/estudiantes/", json=estudiante_data)
        assert resp.status_code == 201, resp.get_json()
        data = resp.get_json()

        # Acepta ambas respuestas
        est = data.get("estudiante", data)
        assert est["matricula"] == estudiante_data["matricula"]

    def test_listar_estudiantes(self, client):
        resp = client.get("/api/estudiantes/")
        assert resp.status_code == 200, resp.get_json()
        data = resp.get_json()
        assert "estudiantes" in data
        assert isinstance(data["estudiantes"], list)

    def test_obtener_estudiante(self, client, estudiante_data):
        resp = client.post("/api/estudiantes/", json=estudiante_data)
        assert resp.status_code == 201, resp.get_json()

        est_id, _ = self._get_id_from_post(resp)

        resp_get = client.get(f"/api/estudiantes/{est_id}")
        assert resp_get.status_code == 200, resp_get.get_json()

        data_get = resp_get.get_json()
        # puede venir {"id":...} o {"estudiante":{"id":...}}
        est_get = data_get.get("estudiante", data_get)
        assert est_get["id"] == est_id

    def test_actualizar_estudiante(self, client, estudiante_data):
        resp = client.post("/api/estudiantes/", json=estudiante_data)
        assert resp.status_code == 201, resp.get_json()

        est_id, _ = self._get_id_from_post(resp)

        resp_put = client.put(f"/api/estudiantes/{est_id}", json={"semestre": 8})
        assert resp_put.status_code == 200, resp_put.get_json()

        data_put = resp_put.get_json()
        est_put = data_put.get("estudiante", data_put)
        assert est_put["semestre"] == 8

    def test_eliminar_estudiante(self, client, estudiante_data):
        resp = client.post("/api/estudiantes/", json=estudiante_data)
        assert resp.status_code == 201, resp.get_json()

        est_id, _ = self._get_id_from_post(resp)

        resp_del = client.delete(f"/api/estudiantes/{est_id}")
        assert resp_del.status_code == 200, resp_del.get_json()

        # Verifica que ya no aparece en lista (si tu API hace borrado lógico)
        lista = client.get("/api/estudiantes/").get_json()["estudiantes"]
        ids = [e["id"] for e in lista]
        assert est_id not in ids
        
    def test_kardex(self, client, estudiante_data):
        resp = client.post("/api/estudiantes/", json=estudiante_data)
        assert resp.status_code == 201, resp.get_json()

        data = resp.get_json()
        est = data.get("estudiante", data)
        est_id = est["id"]

        resp_k = client.get(f"/api/estudiantes/{est_id}/kardex")
        assert resp_k.status_code == 200, resp_k.get_json()