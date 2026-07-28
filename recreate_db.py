import os
import shutil
from pathlib import Path

print("=" * 60)
print("Recreating Database")
print("=" * 60)

# Get database path
db_path = Path(__file__).parent / 'instance' / 'haziripro.db'

# Delete existing database
if db_path.exists():
    print(f"\nRemoving existing database: {db_path}")
    os.remove(db_path)
    print("✓ Database removed")
else:
    print("\nNo existing database found")

# Import and create new database
print("\nCreating new database...")

from app import create_app
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Create all tables
    print("Creating tables...")
    db.create_all()
    print("✓ All tables created")
    
    # Create default admin
    admin = User(
        username='admin',
        email='admin@haziripro.com',
        password_hash=generate_password_hash('admin123'),
        role='admin',
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
    
    print("\n" + "=" * 60)
    print("✓ Database created successfully!")
    print("=" * 60)
    print("\nDefault credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("=" * 60)
    print("\nYou can now run: python app.py")
    print("=" * 60)