from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError
from app import db
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registro de usuario
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username
              - password
            properties:
              username:
                type: string
                example: admin1
              password:
                type: string
                example: 12345
              rol:
                type: string
                example: admin
    responses:
      201:
        description: Usuario creado
      409:
        description: Username ya existe
      400:
        description: Datos inválidos
    """
    datos = request.get_json() or {}
    username = str(datos.get("username", "")).strip()
    password = str(datos.get("password", "")).strip()
    rol = str(datos.get("rol", "user")).strip()

    if not username or not password:
        return jsonify({"error": "username y password son requeridos"}), 400

    if rol not in ["user", "admin"]:
        rol = "user"

    u = Usuario(username=username, rol=rol)
    u.set_password(password)

    try:
        db.session.add(u)
        db.session.commit()
        return jsonify({"mensaje": "Usuario creado", "usuario": u.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Ese username ya existe"}), 409


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login
    ---
    tags:
      - Auth
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username
              - password
            properties:
              username:
                type: string
                example: admin1
              password:
                type: string
                example: 12345
    responses:
      200:
        description: Token generado
      401:
        description: Credenciales inválidas
      400:
        description: Datos inválidos
    """
    datos = request.get_json() or {}
    username = str(datos.get("username", "")).strip()
    password = str(datos.get("password", "")).strip()

    if not username or not password:
        return jsonify({"error": "username y password son requeridos"}), 400

    u = Usuario.query.filter_by(username=username, activo=True).first()
    if not u or not u.check_password(password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = create_access_token(identity={"id": u.id, "username": u.username, "rol": u.rol})
    return jsonify({"access_token": token, "usuario": u.to_dict()}), 200