import os
import pickle

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except Exception:
    face_recognition = None
    FACE_RECOGNITION_AVAILABLE = False


def encode_faces_from_directory(directory_path, output_file='ai/trained_model.pkl'):
    """Encode all faces from a directory (standalone helper script, not used by the web app)"""
    if not FACE_RECOGNITION_AVAILABLE:
        raise RuntimeError("face-recognition/dlib is not installed; cannot encode faces.")

    known_encodings = []
    known_names = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Get employee ID from filename
            employee_id = os.path.splitext(filename)[0]
            
            # Load image
            image_path = os.path.join(directory_path, filename)
            image = face_recognition.load_image_file(image_path)
            
            # Get face encodings
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                known_encodings.append(encodings[0])
                known_names.append(employee_id)
                print(f"Encoded face for {employee_id}")
    
    # Save encodings
    data = {
        'encodings': known_encodings,
        'names': known_names
    }
    
    with open(output_file, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"Saved {len(known_encodings)} face encodings to {output_file}")
    return len(known_encodings)