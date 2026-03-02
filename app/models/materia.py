from app import db

class Materia(db.Model):
    __tablename__ = "materias"

    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(10), unique=True, nullable=False)
    nombre = db.Column(db.String(120), nullable=False)
    creditos = db.Column(db.Integer, nullable=False, default=0)
    semestre = db.Column(db.Integer, nullable=False, default=1)
    activo = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "clave": self.clave,
            "nombre": self.nombre,
            "creditos": self.creditos,
            "semestre": self.semestre,
            "activo": self.activo
        }