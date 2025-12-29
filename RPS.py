import cv2
import mediapipe as mp
import random
import time

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def get_gesture(hand_landmarks):
    # Mediapipe Landmark IDs: Index=8, Middle=12, Ring=16, Pinky=20
    # Knuckle IDs: Index=6, Middle=10, Ring=14, Pinky=18
    fingers = []
    
    # Check 4 fingers (excluding thumb for simplicity)
    for tip, knuckle in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[knuckle].y:
            fingers.append(1) # Finger is up
        else:
            fingers.append(0) # Finger is down

    if sum(fingers) == 0:
        return "Rock"
    elif sum(fingers) == 4:
        return "Paper"
    elif fingers[0] == 1 and fingers[1] == 1 and sum(fingers) == 2:
        return "Scissors"
    return "Unknown"

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, img = cap.read()
    img = cv2.flip(img, 1) # Flip for selfie view
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    gesture = "Show your hand"
    
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            gesture = get_gesture(hand_lms)
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    # Display the gesture on screen
    cv2.putText(img, f"Gesture: {gesture}", (10, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Rock Paper Scissors AI", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()