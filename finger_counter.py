import cv2
import mediapipe as mp
import math

def main():
    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.6)
    
    mp_drawing = mp.solutions.drawing_utils
    
    # Start video capture
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        # Flip image horizontally for a mirror effect
        image = cv2.flip(image, 1)
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process the image
        results = hands.process(image_rgb)
        
        # Draw hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Count fingers with improved logic
                finger_count, handedness = count_fingers(hand_landmarks)
                
                # Display finger count and hand orientation
                cv2.putText(image, f"Fingers: {finger_count}", (10, 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(image, f"Hand: {handedness}", (10, 100), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Show the image
        cv2.imshow('Optimized Finger Counter', image)
        
        # Exit on 'q' key press
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

def count_fingers(hand_landmarks):
    # Landmark indices
    wrist = 0
    thumb_joints = [1, 2, 3, 4]  # From base to tip
    finger_joints = [
        [5, 6, 7, 8],    # Index
        [9, 10, 11, 12],  # Middle
        [13, 14, 15, 16], # Ring
        [17, 18, 19, 20]  # Pinky
    ]
    
    # Determine handedness (left or right)
    handedness = "left" if hand_landmarks.landmark[5].x > hand_landmarks.landmark[17].x else "right"
    
    # Count extended fingers
    finger_count = 0
    
    # Check thumb (special logic)
    thumb_tip = hand_landmarks.landmark[thumb_joints[-1]]
    thumb_mcp = hand_landmarks.landmark[thumb_joints[0]]
    thumb_pip = hand_landmarks.landmark[thumb_joints[1]]
    
    # Calculate thumb extension based on hand orientation
    if handedness == "right":
        thumb_extended = thumb_tip.x < thumb_pip.x
    else:
        thumb_extended = thumb_tip.x > thumb_pip.x
    
    if thumb_extended:
        finger_count += 1
    
    # Check other fingers
    for finger in finger_joints:
        tip = hand_landmarks.landmark[finger[-1]]
        dip = hand_landmarks.landmark[finger[-2]]
        pip = hand_landmarks.landmark[finger[-3]]
        mcp = hand_landmarks.landmark[finger[-4]]
        
        # Finger is extended if tip is significantly above PIP
        # and the angle between segments is less than 160 degrees
        finger_extended = (tip.y < pip.y * 0.9) and (
            calculate_angle(tip, dip, pip) < 160 or 
            calculate_angle(dip, pip, mcp) < 160)
        
        if finger_extended:
            finger_count += 1
    
    return finger_count, handedness

def calculate_angle(a, b, c):
    # Calculate the angle between three points (in degrees)
    ba = (a.x - b.x, a.y - b.y)
    bc = (c.x - b.x, c.y - b.y)
    
    dot_product = ba[0] * bc[0] + ba[1] * bc[1]
    magnitude_ba = math.sqrt(ba[0]**2 + ba[1]**2)
    magnitude_bc = math.sqrt(bc[0]**2 + bc[1]**2)
    
    angle = math.acos(dot_product / (magnitude_ba * magnitude_bc))
    return math.degrees(angle)

if __name__ == "__main__":
    main()