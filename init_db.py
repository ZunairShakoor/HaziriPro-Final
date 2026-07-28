import os
import sys

# Create all required directories
directories = [
    'instance',
    'static/uploads/employees',
    'static/uploads/faces',
    'static/css',
    'static/js',
    'static/images',
    'exports/pdf',
    'exports/excel',
    'exports/csv',
    'ai'
]

print("Creating directories...")
for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"✓ Created: {directory}")

print("\nInitializing database...")

# Now import and create the database
from app import create_app
from extensions import db

app = create_app()

with app.app_context():
    # Drop all tables (if they exist)
    db.drop_all()
    print("Dropped existing tables (if any)")
    
    # Create all tables
    db.create_all()
    print("Created all database tables")
    
    # Create default admin
    from models.user import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@haziripro.com',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("\n✓ Default admin created!")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("\n✓ Admin already exists")

print("\n" + "="*50)
print("Database initialization complete!")
print("="*50)
print("\nYou can now run: python app.py")