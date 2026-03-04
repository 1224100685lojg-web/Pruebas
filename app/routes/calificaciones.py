from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from app import db
from app.models.estudiante import Estudiante
from app.models.materia import Materia
from app.models.calificacion import Calificacion

calificaciones_bp = Blueprint("calificaciones", __name__, url_prefix="/api/calificaciones")


@calificaciones_bp.route("/", methods=["POST"])
@jwt_required()
def registrar_calificacion():
    datos = request.get_json() or {}

    requeridos = ["estudiante_id", "materia_id", "calificacion", "periodo"]
    faltan = [r for r in requeridos if r not in datos or str(datos[r]).strip() == ""]
    if faltan:
        return jsonify({"error": f"Faltan campos: {', '.join(faltan)}"}), 400

    # Validar existencia estudiante
    try:
        estudiante_id = int(datos["estudiante_id"])
    except ValueError:
        return jsonify({"error": "estudiante_id debe ser numérico"}), 400

    estudiante = Estudiante.query.get(estudiante_id)
    if not estudiante or not getattr(estudiante, "activo", True):
        return jsonify({"error": "Estudiante no encontrado"}), 404

    # Validar existencia materia
    try:
        materia_id = int(datos["materia_id"])
    except ValueError:
        return jsonify({"error": "materia_id debe ser numérico"}), 400

    materia = Materia.query.get(materia_id)
    if not materia or not getattr(materia, "activo", True):
        return jsonify({"error": "Materia no encontrada"}), 404

    # Validar rango calificación (tu API usa 0 a 10)
    try:
        cal = float(datos["calificacion"])
        if cal < 0 or cal > 10:
            return jsonify({"error": "Calificación inválida (0 a 10)"}), 400
    except ValueError:
        return jsonify({"error": "Calificación debe ser numérica"}), 400

    periodo = str(datos["periodo"]).strip()

    reg = Calificacion(
        estudiante_id=estudiante.id,
        materia_id=materia.id,
        calificacion=cal,
        periodo=periodo
    )

    try:
        db.session.add(reg)
        db.session.commit()
        return jsonify({"mensaje": "Calificación registrada", "calificacion": reg.to_dict()}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Ya existe calificación para esa materia en ese periodo"}), 409