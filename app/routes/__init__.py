from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def index():
    return jsonify({
        "mensaje": "🐍 Bienvenido a mi primera API con Flask!",
        "version": "1.0.0",
        "tecnologias": ["Python", "Flask", "PostgreSQL"]
    })