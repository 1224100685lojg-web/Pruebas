from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from app import db
from app.models.materia import Materia

# Blueprint
materias_bp = Blueprint("materias", __name__, url_prefix="/api/materias")


@materias_bp.route("/", methods=["POST"])
@jwt_required()
def crear_materia():
    datos = request.get_json() or {}

    # Validaciones básicas
    clave = str(datos.get("clave", "")).strip()
    nombre = str(datos.get("nombre", "")).strip()

    if not clave or not nombre:
        return jsonify({"error": "clave y nombre son requeridos"}), 400

    try:
        creditos = int(datos.get("creditos", 0))
        semestre = int(datos.get("semestre", 1))
    except ValueError:
        return jsonify({"error": "creditos y semestre deben ser numéricos"}), 400

    nueva = Materia(
        clave=clave,
        nombre=nombre,
        creditos=creditos,
        semestre=semestre
    )

    try:
        db.session.add(nueva)
        db.session.commit()

        return jsonify({
            "mensaje": "Materia creada",
            "materia": nueva.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "La clave de materia ya existe"}), 409


@materias_bp.route("/", methods=["GET"])
@jwt_required()
def listar_materias():

    materias = Materia.query.filter_by(activo=True).order_by(Materia.id.asc()).all()

    # Devuelve lista directa (compatible con tus tests)
    return jsonify({"materias": [m.to_dict() for m in materias]}), 200