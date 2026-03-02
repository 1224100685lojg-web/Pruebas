from app import db
from datetime import datetime

class Calificacion(db.Model):
    __tablename__ = "calificaciones"

    id = db.Column(db.Integer, primary_key=True)

    estudiante_id = db.Column(db.Integer, db.ForeignKey("estudiantes.id"), nullable=False)
    materia_id = db.Column(db.Integer, db.ForeignKey("materias.id"), nullable=False)

    calificacion = db.Column(db.Float, nullable=False)  # 0-10
    periodo = db.Column(db.String(20), nullable=False, default="2026-1")  # ej. 2026-1
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Evita duplicar misma materia en mismo periodo para mismo estudiante
    __table_args__ = (
        db.UniqueConstraint("estudiante_id", "materia_id", "periodo", name="uq_est_mat_periodo"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "estudiante_id": self.estudiante_id,
            "materia_id": self.materia_id,
            "calificacion": self.calificacion,
            "periodo": self.periodo,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None
        }