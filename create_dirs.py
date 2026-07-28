import os

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

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"✓ Created: {directory}")

print("\nAll directories created successfully!")