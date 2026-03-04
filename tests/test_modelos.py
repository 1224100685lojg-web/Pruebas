import pytest
from app.models.estudiante import Estudiante

class TestModeloEstudiante:

    def test_crear_estudiante(self, session):

        # Arrange
        est = Estudiante(
            matricula="ITIC001",
            nombre="Maria",
            apellido="Gonzalez",
            email="maria@uni.edu.mx",
            carrera="ITIC",
            semestre=5
        )

        # Act
        session.add(est)
        session.commit()

        # Assert
        assert est.id is not None
        assert est.nombre == "Maria"
        assert est.semestre == 5