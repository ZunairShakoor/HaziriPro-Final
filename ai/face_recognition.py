import os
import pickle
from PIL import Image

try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except Exception:
    np = None
    NUMPY_AVAILABLE = False

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except Exception:
    face_recognition = None
    FACE_RECOGNITION_AVAILABLE = False


class FaceRecognitionSystem:
    """
    Wraps the `face_recognition` library (built on dlib) for
    registration/verification.

    IMPORTANT: dlib is the single most failure-prone dependency in this
    project on Windows (it needs a C++ build toolchain and CMake). If it
    failed to install, this class still imports fine and the rest of the
    app keeps working — only the actual face-recognition methods below
    return a clear "unavailable" message instead of throwing an
    ImportError that used to take down the whole `dashboard` blueprint
    (because AttendanceService imports this module, and
    routes/dashboard.py imports AttendanceService).
    """

    def __init__(self, encodings_path='static/uploads/faces'):
        self.encodings_path = encodings_path
        self.known_face_encodings = []
        self.known_face_names = []
        self.available = FACE_RECOGNITION_AVAILABLE and CV2_AVAILABLE and NUMPY_AVAILABLE
        self.load_encodings()

    def _unavailable_message(self):
        missing = []
        if not FACE_RECOGNITION_AVAILABLE:
            missing.append('face-recognition/dlib')
        if not CV2_AVAILABLE:
            missing.append('opencv-python')
        if not NUMPY_AVAILABLE:
            missing.append('numpy')
        return (
            "Face recognition is unavailable because these packages "
            f"failed to install: {', '.join(missing)}. "
            "See the terminal output from 'pip install -r requirements.txt' "
            "for the actual installation error."
        )

    def load_encodings(self):
        self.known_face_encodings = []
        self.known_face_names = []

        encodings_file = os.path.join(self.encodings_path, "encodings.pkl")

        if os.path.exists(encodings_file):
            with open(encodings_file, "rb") as f:
                data = pickle.load(f)
                self.known_face_encodings = data.get("encodings", [])
                self.known_face_names = data.get("names", [])

    def save_encodings(self):
        os.makedirs(self.encodings_path, exist_ok=True)
        with open(os.path.join(self.encodings_path, "encodings.pkl"), "wb") as f:
            pickle.dump(
                {
                    "encodings": self.known_face_encodings,
                    "names": self.known_face_names,
                },
                f,
            )

    def register_face(self, image_path, employee_id):
        if not self.available:
            return False, self._unavailable_message()

        img = Image.open(image_path)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(image_path, "JPEG", quality=95)

        image = np.ascontiguousarray(np.asarray(img, dtype=np.uint8))

        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            return False, "No face detected."

        if len(face_locations) > 1:
            return False, "Multiple faces detected."

        encodings = face_recognition.face_encodings(image, face_locations)

        if not encodings:
            return False, "Unable to generate encoding."

        if employee_id in self.known_face_names:
            idx = self.known_face_names.index(employee_id)
            self.known_face_encodings[idx] = encodings[0]
        else:
            self.known_face_names.append(employee_id)
            self.known_face_encodings.append(encodings[0])

        self.save_encodings()
        return True, "Face registered successfully."

    def recognize_face(self, image_path=None, image_array=None):
        if not self.available:
            return None, 0, self._unavailable_message()

        self.load_encodings()

        try:
            if image_path:
                image = face_recognition.load_image_file(image_path)
            elif image_array is not None:
                 image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                 image = np.ascontiguousarray(image, dtype=np.uint8)     
            else:
                return None, 0, "No image provided."

            if len(self.known_face_encodings) == 0:
                return None, 0, "No registered faces found."

            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                return None, 0, "No face detected."

            if len(face_locations) > 1:
                return None, 0, "Multiple faces detected."

            face_encodings = face_recognition.face_encodings(image, face_locations)

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=0.65
                )

                distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    face_encoding
                )

                if len(distances) == 0:
                    continue

                best = np.argmin(distances)

                if matches[best]:
                    confidence = max(0.0, 1 - distances[best])
                    return self.known_face_names[best], confidence, "Face recognized"

            return None, 0, "Face not recognized."

        except Exception as e:
            import traceback
            traceback.print_exc()
            return None, 0, str(e)

    def get_face_location(self, image_array):
        """
        Return the bounding box (top, right, bottom, left) of the first
        detected face in a BGR image array, or None if unavailable/no face
        found. Used to crop tightly to the face before emotion analysis —
        DeepFace is noticeably less accurate (and biases toward "neutral")
        when given a whole webcam frame with background/desk/etc. instead
        of a tight face crop.
        """
        if not self.available:
            return None

        try:
            rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            rgb_image = np.ascontiguousarray(rgb_image, dtype=np.uint8)

            face_locations = face_recognition.face_locations(rgb_image)
            if not face_locations:
                return None

            return face_locations[0]
        except Exception:
            return None

    def verify_face(self, employee_id, image_path=None, image_array=None):
        """
        Verify that the detected face belongs to the specified employee.
        """
        if not self.available:
            return False, 0, self._unavailable_message()

        self.load_encodings()

        try:
            if image_path:
                image = face_recognition.load_image_file(image_path)
            elif image_array is not None:
                image = image_array
                image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                image = np.ascontiguousarray(image, dtype=np.uint8)
            else:
                return False, 0, "No image provided."

            if employee_id not in self.known_face_names:
                return False, 0, "Employee face not registered."

            index = self.known_face_names.index(employee_id)
            stored_encoding = self.known_face_encodings[index]

            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 0:
                return False, 0, "No face detected."

            if len(face_locations) > 1:
                return False, 0, "Multiple faces detected."

            face_encoding = face_recognition.face_encodings(image, face_locations)[0]

            match = face_recognition.compare_faces(
                [stored_encoding],
                face_encoding,
                tolerance=0.65
            )[0]

            distance = face_recognition.face_distance(
                [stored_encoding],
                face_encoding
            )[0]

            confidence = max(0.0, 1 - distance)

            if match:
                return True, confidence, "Face verified."

            return False, confidence, "Face does not match logged-in employee."

        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, 0, str(e)

    def delete_face(self, employee_id):
        self.load_encodings()

        if employee_id in self.known_face_names:
            index = self.known_face_names.index(employee_id)
            self.known_face_names.pop(index)
            self.known_face_encodings.pop(index)
            self.save_encodings()
            return True, "Face deleted successfully."

        return False, "Face encoding not found."
