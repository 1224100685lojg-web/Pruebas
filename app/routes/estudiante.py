from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, DataError
from app import db
from app.models.estudiante import Estudiante
from app.models.calificacion import Calificacion
from app.models.materia import Materia

estudiantes_bp = Blueprint("estudiantes", __name__, url_prefix="/api/estudiantes")


@estudiantes_bp.route("/", methods=["POST"])
def crear_estudiante():
    """
    Crear estudiante
    ---
    tags:
      - Estudiantes
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - matricula
              - nombre
              - apellido
              - email
              - carrera
            properties:
              matricula:
                type: string
                example: ITIC202401
              nombre:
                type: string
                example: Ana
              apellido:
                type: string
                example: García
              email:
                type: string
                example: ana@utng.edu.mx
              carrera:
                type: string
                example: ITIC
              semestre:
                type: integer
                example: 5
    responses:
      201:
        description: Estudiante creado
      400:
        description: Error de validación
      409:
        description: Duplicado
    """
    datos = request.get_json() or {}

    campos = ["matricula", "nombre", "apellido", "email", "carrera"]
    faltantes = [c for c in campos if c not in datos or str(datos[c]).strip() == ""]
    if faltantes:
        return jsonify({"error": f"Faltan campos: {', '.join(faltantes)}"}), 400

    # OJO: si tu BD tiene matricula VARCHAR(10)
    if len(str(datos["matricula"])) > 10:
        return jsonify({"error": "La matrícula no puede exceder 10 caracteres"}), 400

    # Validación semestre
    semestre = datos.get("semestre", 1)
    try:
        semestre = int(semestre)
        if semestre < 1 or semestre > 15:
            return jsonify({"error": "Semestre inválido (1 a 15)"}), 400
    except ValueError:
        return jsonify({"error": "Semestre debe ser numérico"}), 400

    # Duplicados
    if Estudiante.query.filter_by(matricula=str(datos["matricula"]).strip()).first():
        return jsonify({"error": "La matrícula ya existe"}), 409
    if Estudiante.query.filter_by(email=str(datos["email"]).strip()).first():
        return jsonify({"error": "El email ya existe"}), 409

    nuevo = Estudiante(
        matricula=str(datos["matricula"]).strip(),
        nombre=str(datos["nombre"]).strip(),
        apellido=str(datos["apellido"]).strip(),
        email=str(datos["email"]).strip(),
        carrera=str(datos["carrera"]).strip(),
        semestre=semestre,
    )

    try:
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Creado", "estudiante": nuevo.to_dict()}), 201
    except (IntegrityError, DataError):
        db.session.rollback()
        return jsonify({"error": "Error al guardar. Verifica datos (duplicados/longitud)."}), 400


@estudiantes_bp.route("/", methods=["GET"])
def listar_estudiantes():
    """
    Listar estudiantes (filtro + paginación)
    ---
    tags:
      - Estudiantes
    parameters:
      - in: query
        name: carrera
        schema:
          type: string
        required: false
        description: Filtrar por carrera (ej. ITIC)
      - in: query
        name: pagina
        schema:
          type: integer
        required: false
        description: Número de página
      - in: query
        name: por_pagina
        schema:
          type: integer
        required: false
        description: Registros por página
    responses:
      200:
        description: Lista paginada de estudiantes
    """
    carrera = request.args.get("carrera")
    pagina = request.args.get("pagina", default=1, type=int)
    por_pagina = request.args.get("por_pagina", default=10, type=int)

    if pagina < 1:
        pagina = 1
    if por_pagina < 1:
        por_pagina = 10
    if por_pagina > 100:
        por_pagina = 100

    query = Estudiante.query.filter_by(activo=True)
    if carrera:
        query = query.filter(Estudiante.carrera.ilike(carrera))

    pag = query.order_by(Estudiante.id.asc()).paginate(page=pagina, per_page=por_pagina, error_out=False)

    return jsonify({
        "total": pag.total,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "paginas": pag.pages,
        "estudiantes": [e.to_dict() for e in pag.items]
    }), 200


@estudiantes_bp.route("/<int:id>", methods=["GET"])
def obtener_estudiante(id):
    """
    Obtener estudiante por ID
    ---
    tags:
      - Estudiantes
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Estudiante
      404:
        description: No encontrado
    """
    estudiante = Estudiante.query.get(id)
    if not estudiante or not estudiante.activo:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    return jsonify(estudiante.to_dict()), 200


@estudiantes_bp.route("/<int:id>", methods=["PUT"])
def actualizar_estudiante(id):
    """
    Actualizar estudiante por ID
    ---
    tags:
      - Estudiantes
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              nombre: {type: string}
              apellido: {type: string}
              email: {type: string}
              carrera: {type: string}
              semestre: {type: integer}
    responses:
      200:
        description: Actualizado
      404:
        description: No encontrado
    """
    estudiante = Estudiante.query.get(id)
    if not estudiante or not estudiante.activo:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    datos = request.get_json() or {}

    for campo in ["nombre", "apellido", "email", "carrera", "semestre"]:
        if campo in datos:
            setattr(estudiante, campo, datos[campo])

    try:
        db.session.commit()
        return jsonify({"mensaje": "Actualizado", "estudiante": estudiante.to_dict()}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar (duplicados)."}), 400


@estudiantes_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_estudiante(id):
    """
    Eliminar estudiante (borrado lógico)
    ---
    tags:
      - Estudiantes
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Desactivado
      404:
        description: No encontrado
    """
    estudiante = Estudiante.query.get(id)
    if not estudiante or not estudiante.activo:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    estudiante.activo = False
    db.session.commit()
    return jsonify({"mensaje": "Estudiante desactivado"}), 200


@estudiantes_bp.route("/<int:id>/kardex", methods=["GET"])
def kardex(id):
    """
    Kardex del estudiante
    ---
    tags:
      - Kardex
    parameters:
      - in: path
        name: id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Kardex y resumen
      404:
        description: Estudiante no encontrado
    """
    estudiante = Estudiante.query.get(id)
    if not estudiante or not estudiante.activo:
        return jsonify({"error": "Estudiante no encontrado"}), 404

    rows = (
        db.session.query(Calificacion, Materia)
        .join(Materia, Calificacion.materia_id == Materia.id)
        .filter(Calificacion.estudiante_id == id)
        .order_by(Calificacion.periodo.asc())
        .all()
    )

    detalle = []
    aprobadas = 0
    reprobadas = 0
    suma = 0.0
    n = 0

    for cal, mat in rows:
        n += 1
        suma += float(cal.calificacion)
        if cal.calificacion >= 6:
            aprobadas += 1
            resultado = "Aprobada"
        else:
            reprobadas += 1
            resultado = "Reprobada"

        detalle.append({
            "periodo": cal.periodo,
            "materia": mat.nombre,
            "clave": mat.clave,
            "creditos": mat.creditos,
            "calificacion": cal.calificacion,
            "resultado": resultado
        })

    promedio = round(suma / n, 2) if n > 0 else 0.0

    return jsonify({
        "estudiante": estudiante.to_dict(),
        "resumen": {
            "total_materias": n,
            "aprobadas": aprobadas,
            "reprobadas": reprobadas,
            "promedio": promedio
        },
        "kardex": detalle
    }), 200