import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Get the base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this-in-production')
    
    # Database - CORRECTED PATH
    # Use absolute path for SQLite database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'sqlite:///{os.path.join(basedir, "instance", "haziripro.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Directories - Use absolute paths
    EMPLOYEE_PHOTOS_DIR = os.path.join(basedir, 'static', 'uploads', 'employees')
    FACE_ENCODINGS_DIR = os.path.join(basedir, 'static', 'uploads', 'faces')
    EXPORTS_DIR = os.path.join(basedir, 'exports')
    
    # AI Models
    FACE_RECOGNITION_MODEL = 'hog'  # or 'cnn' for better accuracy
    EMOTION_MODEL_PATH = os.path.join(basedir, 'ai', 'trained_model.pkl')
    
    # Payroll
    TAX_RATE = 0.15
    OVERTIME_MULTIPLIER = 1.5
    
    # Attendance
    GRACE_PERIOD_MINUTES = 15
    WORK_HOURS_PER_DAY = 8
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        directories = [
            os.path.join(basedir, 'instance'),
            os.path.join(basedir, 'static', 'uploads', 'employees'),
            os.path.join(basedir, 'static', 'uploads', 'faces'),
            os.path.join(basedir, 'exports', 'pdf'),
            os.path.join(basedir, 'exports', 'excel'),
            os.path.join(basedir, 'exports', 'csv'),
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)