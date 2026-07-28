print("Testing installations...")

# Test Flask
try:
    import flask
    print("✓ Flask installed")
except ImportError:
    print("✗ Flask not installed")

# Test SQLAlchemy
try:
    import flask_sqlalchemy
    print("✓ Flask-SQLAlchemy installed")
except ImportError:
    print("✗ Flask-SQLAlchemy not installed")

# Test Face Recognition (optional)
try:
    import face_recognition
    print("✓ Face Recognition installed")
except ImportError:
    print("✗ Face Recognition not installed (optional)")

# Test OpenCV (optional)
try:
    import cv2
    print("✓ OpenCV installed")
except ImportError:
    print("✗ OpenCV not installed (optional)")

# Test TensorFlow (optional)
try:
    import tensorflow
    print("✓ TensorFlow installed")
except ImportError:
    print("✗ TensorFlow not installed (optional)")

print("\nCore packages check complete!")