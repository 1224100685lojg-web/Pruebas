from app import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Tablas creadas correctamente")

    print("🚀 Servidor iniciado en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    # run.py

app = create_app()

# Verificar conexión a la base de datos
with app.app_context():  # Necesitamos el contexto de la app para usar db
    try:
        db.session.execute('SELECT 1')  # Ejecuta una consulta simple
        print("✅ Conexión exitosa a la base de datos!")  # Si no hay error, la conexión es exitosa
    except Exception as e:
        print("❌ Error al conectar con la base de datos:", e)

if __name__ == "__main__":
    app.run(debug=True)