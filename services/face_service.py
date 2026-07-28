try:
    import cv2
    CV2_AVAILABLE = True
except Exception:
    cv2 = None
    CV2_AVAILABLE = False

import numpy as np
from ai.face_recognition import FaceRecognitionSystem
from ai.emotion_detector import EmotionDetector

class FaceService:
    def __init__(self):
        self.face_recognition = FaceRecognitionSystem()
        self.emotion_detector = EmotionDetector()
    
    def capture_from_webcam(self):
        """Capture image from webcam (local desktop use only — not used by the web app)"""
        if not CV2_AVAILABLE:
            raise RuntimeError("opencv-python is not installed; webcam capture is unavailable.")

        cap = cv2.VideoCapture(0)
        
        print("Press SPACE to capture, ESC to cancel")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.imshow('Capture Face', frame)
            
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                cap.release()
                cv2.destroyAllWindows()
                return None
            elif key == 32:  # SPACE
                cap.release()
                cv2.destroyAllWindows()
                return frame
        
        cap.release()
        cv2.destroyAllWindows()
        return None
    
    def process_attendance_image(self, image):
        """Process image for attendance"""
        # Recognize face
        employee_id, confidence, face_message = self.face_recognition.recognize_face(
            image_array=image
        )
        
        # Detect emotion
        emotion, emotion_confidence, emotion_message = self.emotion_detector.detect_emotion(
            image_array=image
        )
        
        return {
            'employee_id': employee_id,
            'face_confidence': confidence,
            'face_message': face_message,
            'emotion': emotion,
            'emotion_confidence': emotion_confidence,
            'emotion_message': emotion_message
        }