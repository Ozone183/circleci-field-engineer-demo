from app.main import app, db

print("🔧 Initializing database tables...")
with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")
