import uuid


class TestCalificaciones:
    def _estudiante_payload(self):
        code = uuid.uuid4().hex[:6].upper()
        return {
            "matricula": f"TEST{code}",
            "nombre": "Carlos",
            "apellido": "Ramírez",
            "email": f"carlos{code.lower()}@test.edu.mx",
            "carrera": "ITIC",
            "semestre": 5
        }

    def _materia_payload(self):
        code = uuid.uuid4().hex[:6].upper()
        return {
            "clave": f"MAT{code}",
            "nombre": f"Materia {code}",
            "creditos": 5,
            "semestre": 1
        }

    def test_registrar_calificacion(self, client, auth_headers):
        # 1) Crear estudiante (NO protegido)
        r_est = client.post("/api/estudiantes/", json=self._estudiante_payload())
        assert r_est.status_code in (200, 201), r_est.get_json()

        est_data = r_est.get_json()
        est = est_data.get("estudiante", est_data)
        est_id = est.get("id")
        assert est_id is not None, est_data

        # 2) Crear materia (PROTEGIDO)
        r_mat = client.post("/api/materias/", json=self._materia_payload(), headers=auth_headers)
        assert r_mat.status_code in (200, 201), r_mat.get_json()

        mat_data = r_mat.get_json()
        mat = mat_data.get("materia", mat_data)
        mat_id = mat.get("id")
        assert mat_id is not None, mat_data

        # 3) Registrar calificación (PROTEGIDO) ✅ incluye periodo
        payload_cal = {
            "estudiante_id": est_id,
            "materia_id": mat_id,
            "calificacion": 9.0,
            "periodo": "2026-1"
        }

        resp = client.post("/api/calificaciones/", json=payload_cal, headers=auth_headers)
        assert resp.status_code in (200, 201), resp.get_json()

        data = resp.get_json()
        cal = data.get("calificacion", data)
        assert cal.get("estudiante_id") == est_id
        assert cal.get("materia_id") == mat_id