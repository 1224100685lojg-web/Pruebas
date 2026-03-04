# tests/conftest.py
import pytest
from app import create_app, db as _db
from app.config import TestingConfig
import uuid


@pytest.fixture(scope="session")
def app(tmp_path_factory):
    # ✅ BD en archivo temporal (misma para toda la sesión)
    db_file = tmp_path_factory.mktemp("data") / "test.sqlite"

    class FileTestingConfig(TestingConfig):
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_file}"
        SQLALCHEMY_ENGINE_OPTIONS = {"connect_args": {"check_same_thread": False}}

    app = create_app(FileTestingConfig)
    yield app


@pytest.fixture(scope="session")
def db(app):
    with app.app_context():
        # ✅ Importa modelos ANTES de create_all (para que registre tablas)
        from app.models.estudiante import Estudiante
        from app.models.usuario import Usuario
        from app.models.materia import Materia
        from app.models.calificacion import Calificacion

        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(scope="function")
def session(db, app):
    with app.app_context():
        yield db.session
        db.session.rollback()
        db.session.remove()


@pytest.fixture(scope="function")
def client(app, db):
    # ✅ db se ejecuta antes (create_all), luego ya puedes hacer requests
    return app.test_client()

@pytest.fixture
def estudiante_data():
    codigo = uuid.uuid4().hex[:6].upper()
    return {
        "matricula": f"TEST{codigo}",
        "nombre": "Carlos",
        "apellido": "Ramírez",
        "email": f"carlos{codigo.lower()}@test.edu.mx",
        "carrera": "ITIC",
        "semestre": 5
    }
@pytest.fixture
def auth_headers(client):
    code = uuid.uuid4().hex[:6].lower()

    # registrar
    r = client.post("/api/auth/register", json={
        "username": f"user_{code}",
        "email": f"user_{code}@test.com",
        "password": "Password123!"
    })
    assert r.status_code in (200, 201), r.get_json()

    # login
    l = client.post("/api/auth/login", json={
        "username": f"user_{code}",
        "password": "Password123!"
    })
    assert l.status_code == 200, l.get_json()

    data = l.get_json()
    token = data["access_token"]

    return {"Authorization": f"Bearer {token}"}