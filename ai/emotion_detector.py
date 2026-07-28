import traceback

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except Exception:
    DeepFace = None
    DEEPFACE_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    CV2_AVAILABLE = False

try:
    import numpy as np
except Exception:
    np = None


class EmotionDetector:
    """
    Wraps DeepFace for emotion detection.

    IMPORTANT: DeepFace/TensorFlow (and, separately, opencv-python) are
    two of the heaviest and most failure-prone dependencies on Windows.
    If either failed to install, this class still imports fine and the
    rest of the app (dashboards, employee management, payroll, etc.)
    keeps working — only detect_emotion() itself degrades gracefully to
    "Unknown" instead of throwing an ImportError that used to take down
    the whole `dashboard` blueprint (because AttendanceService imports
    this module, and routes/dashboard.py imports AttendanceService).
    """

    def __init__(self):
        self.emotions = [
            "angry",
            "disgust",
            "fear",
            "happy",
            "sad",
            "surprise",
            "neutral",
        ]
        self.available = DEEPFACE_AVAILABLE and CV2_AVAILABLE

    def detect_emotion(self, image_path=None, image_array=None):
        """
        Detect emotion from image file or webcam frame.
        Returns (emotion, confidence, message) — never raises.
        """

        if not self.available:
            missing = []
            if not DEEPFACE_AVAILABLE:
                missing.append('deepface/tensorflow')
            if not CV2_AVAILABLE:
                missing.append('opencv-python')
            return "Unknown", 0, (
                "Emotion detection is unavailable because these packages "
                f"failed to install: {', '.join(missing)}."
            )

        try:

            # -----------------------------
            # Image from file
            # -----------------------------
            if image_path:

                result = DeepFace.analyze(
                    img_path=image_path,
                    actions=["emotion"],
                    detector_backend="retinaface",
                    enforce_detection=False,
                    silent=True,
                )

            # -----------------------------
            # Image from webcam
            # -----------------------------
            elif image_array is not None:

                if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                    rgb_image = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                else:
                    rgb_image = image_array

                rgb_image = np.ascontiguousarray(rgb_image)
                rgb_image = rgb_image.astype(np.uint8)

                result = DeepFace.analyze(
                    img_path=rgb_image,
                    actions=["emotion"],
                    detector_backend="retinaface",
                    enforce_detection=False,
                    silent=True,
                )

            else:
                return None, 0, "No image provided"

            if isinstance(result, list):
                result = result[0]

            dominant = result.get("dominant_emotion")

            emotions = result.get("emotion", {})

            confidence = float(emotions.get(dominant, 0))

            if dominant is None:
                return "Unknown", 0, "No emotion detected"

            return dominant, confidence, "Emotion detected successfully"

        except Exception:
            traceback.print_exc()
            return "Unknown", 0, "Emotion detection failed"

    def detect_emotion_from_webcam(self):
        """Standalone local-testing helper — not used by the web app."""
        if not self.available:
            print("Emotion detection unavailable: deepface/opencv not installed.")
            return

        cap = cv2.VideoCapture(0)

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            try:

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                rgb = np.ascontiguousarray(rgb)
                rgb = rgb.astype(np.uint8)

                result = DeepFace.analyze(
                    img_path=rgb,
                    actions=["emotion"],
                    detector_backend="retinaface",
                    enforce_detection=False,
                    silent=True,
                )

                if isinstance(result, list):
                    result = result[0]

                emotion = result.get("dominant_emotion", "Unknown")
                confidence = result.get("emotion", {}).get(emotion, 0)

                cv2.putText(
                    frame,
                    f"{emotion} ({confidence:.1f}%)",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

            except Exception:
                traceback.print_exc()

            cv2.imshow("Emotion Detection", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

    def get_emotion_statistics(self, emotions_list):

        if not emotions_list:
            return {}

        counts = {}

        for emotion in emotions_list:
            counts[emotion] = counts.get(emotion, 0) + 1

        total = len(emotions_list)

        return {
            emotion: (count / total) * 100
            for emotion, count in counts.items()
        }