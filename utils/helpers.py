import os
from datetime import datetime, timedelta

from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if file extension is allowed"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def save_uploaded_file(file, folder):
    """
    Save uploaded image as 8-bit RGB JPEG.

    Returns a tuple: (static_relative_path, absolute_filepath)
      - static_relative_path: e.g. 'uploads/faces/xyz.jpg' — relative to the
        'static' folder, for use with url_for('static', filename=...) and
        for storing on the Employee model (photo_path / face_encoding_path).
      - absolute_filepath: the real path on disk, for anything that opens
        the file directly (e.g. Image.open(), face_recognition).
    Returns (None, None) if the file is missing/not an allowed type.
    """

    if not file or not allowed_file(file.filename):
        return None, None

    os.makedirs(
        os.path.join(current_app.config["UPLOAD_FOLDER"], folder),
        exist_ok=True
    )

    filename = secure_filename(file.filename)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    name, _ = os.path.splitext(filename)

    filename = f"{name}_{timestamp}.jpg"

    filepath = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        folder,
        filename
    )

    image = Image.open(file.stream)

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(filepath, "JPEG", quality=95)

    relative_path = os.path.join("uploads", folder, filename).replace("\\", "/")

    return relative_path, filepath


def get_date_range(period="month"):
    end_date = datetime.now().date()

    if period == "week":
        start_date = end_date - timedelta(days=7)

    elif period == "month":
        start_date = end_date.replace(day=1)

    elif period == "year":
        start_date = end_date.replace(month=1, day=1)

    else:
        start_date = end_date

    return start_date, end_date


def format_currency(amount):
    return f"Rs. {amount:,.2f}"


def calculate_age(birth_date):
    today = datetime.now().date()

    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )