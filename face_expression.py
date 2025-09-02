import cv2
import mediapipe as mp
import numpy as np
from collections import deque

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_faces=1)

mp_drawing = mp.solutions.drawing_utils

# Emotion recognition based on facial landmarks
def recognize_emotion(landmarks, image_shape):
    # Get specific landmark points
    landmarks = landmarks.landmark
    
    # Calculate mouth openness
    mouth_vert = landmarks[13].y - landmarks[14].y
    mouth_horiz = landmarks[308].x - landmarks[78].x
    mouth_ratio = mouth_vert / mouth_horiz
    
    # Calculate eyebrow position (average of both eyebrows)
    left_eyebrow = (landmarks[65].y + landmarks[66].y) / 2
    right_eyebrow = (landmarks[295].y + landmarks[296].y) / 2
    eyebrow_avg = (left_eyebrow + right_eyebrow) / 2
    
    # Calculate eye openness
    left_eye_vert = landmarks[159].y - landmarks[145].y
    right_eye_vert = landmarks[386].y - landmarks[374].y
    eye_avg = (left_eye_vert + right_eye_vert) / 2
    
    # Emotion determination logic
    if mouth_ratio > 0.4 and eye_avg < 0.02:
        return "Happy"
    elif eyebrow_avg < 0.3 and mouth_ratio < 0.2:
        return "Angry"
    elif eye_avg < 0.015 and mouth_ratio > 0.3:
        return "Surprised"
    elif mouth_ratio > 0.3 and eyebrow_avg > 0.35:
        return "Sad"
    elif eye_avg < 0.02 and mouth_ratio > 0.25:
        return "Cry"
    else:
        return "Neutral"

# Smoothing using a queue for more stable results
emotion_history = deque(maxlen=10)

# Start video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue
    
    # Flip the image horizontally for a mirror effect
    image = cv2.flip(image, 1)
    
    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # To improve performance, optionally mark the image as not writeable
    image_rgb.flags.writeable = False
    
    # Process the image and detect faces
    results = face_mesh.process(image_rgb)
    
    # Draw the face mesh annotations on the image
    image_rgb.flags.writeable = True
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Recognize emotion
            emotion = recognize_emotion(face_landmarks, image.shape)
            emotion_history.append(emotion)
            
            # Get the most frequent emotion in history for smoothing
            if len(emotion_history) > 0:
                final_emotion = max(set(emotion_history), key=emotion_history.count)
            else:
                final_emotion = emotion
            
            # Draw face landmarks (optional)
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=(0, 255, 0), thickness=1, circle_radius=1))
            
            # Display emotion text
            cv2.putText(image, f"Emotion: {final_emotion}", (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    # Show the image
    cv2.imshow('Emotion Recognition', image)
    
    # Exit on 'q' key press
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()