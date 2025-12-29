import cv2
import mediapipe as mp
import random
import time

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def get_gesture(hand_landmarks):
    fingers = []
    # Finger tip IDs vs Knuckle IDs
    for tip, knuckle in zip([8, 12, 16, 20], [6, 10, 14, 18]):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[knuckle].y:
            fingers.append(1) # Up
        else:
            fingers.append(0) # Down

    if sum(fingers) == 0: return "Rock"
    if sum(fingers) == 4: return "Paper"
    if fingers[0] == 1 and fingers[1] == 1 and sum(fingers[2:]) == 0: return "Scissors"
    return "Unknown"

cap = cv2.VideoCapture(0)
state = "Waiting" # Can be: Waiting, Counting, Result
timer = 0
user_move = ""
computer_move = ""
result = ""

while cap.isOpened():
    success, img = cap.read()
    img = cv2.flip(img, 1) # Mirror view
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    current_hand_gesture = "None"
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            current_hand_gesture = get_gesture(hand_lms)
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    # --- GAME UI LOGIC ---
    if state == "Waiting":
        cv2.putText(img, "Press 'S' to Start", (160, 240), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            state = "Counting"
            timer = time.time()

    elif state == "Counting":
        elapsed = time.time() - timer
        countdown = 3 - int(elapsed)
        cv2.putText(img, str(countdown), (300, 260), cv2.FONT_HERSHEY_DUPLEX, 4, (0, 255, 255), 10)
        
        if countdown <= 0:
            user_move = current_hand_gesture
            computer_move = random.choice(["Rock", "Paper", "Scissors"])
            
            # Determine Winner
            if user_move == computer_move: result = "TIE!"
            elif (user_move == "Rock" and computer_move == "Scissors") or \
                 (user_move == "Paper" and computer_move == "Rock") or \
                 (user_move == "Scissors" and computer_move == "Paper"):
                result = "YOU WIN!"
            else: result = "CPU WINS!"
            
            state = "Result"
            timer = time.time()

    elif state == "Result":
        cv2.putText(img, f"YOU: {user_move}", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"CPU: {computer_move}", (380, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, result, (200, 250), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 0), 4)
        
        if time.time() - timer > 3: # Wait 3 seconds then reset
            state = "Waiting"

    cv2.imshow("Rock Paper Scissors", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()