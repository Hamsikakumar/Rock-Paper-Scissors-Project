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
            fingers.append(1) 
        else:
            fingers.append(0)

    if sum(fingers) == 0: return "Rock"
    if sum(fingers) == 4: return "Paper"
    if fingers[0] == 1 and fingers[1] == 1 and sum(fingers[2:]) == 0: return "Scissors"
    return "Unknown"

cap = cv2.VideoCapture(0)
state = "Counting" # Start directly with counting
timer = time.time()
user_move = ""
computer_move = ""
result = ""

# Score Tracking
user_score = 0
cpu_score = 0

while cap.isOpened():
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    current_hand_gesture = "None"
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            current_hand_gesture = get_gesture(hand_lms)
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    # --- SCOREBOARD UI ---
    cv2.rectangle(img, (0, 0), (640, 60), (50, 50, 50), -1) # Dark header bar
    cv2.putText(img, f"YOU: {user_score}", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, f"CPU: {cpu_score}", (450, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # --- AUTOMATIC GAME LOGIC ---
    if state == "Counting":
        elapsed = time.time() - timer
        countdown = 3 - int(elapsed)
        
        # Display large countdown in the middle
        cv2.putText(img, str(countdown), (280, 280), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 10)
        
        if countdown <= 0:
            user_move = current_hand_gesture
            computer_move = random.choice(["Rock", "Paper", "Scissors"])
            
            if user_move == "Unknown" or user_move == "None":
                result = "NO HAND DETECTED!"
            elif user_move == computer_move:
                result = "TIE!"
            elif (user_move == "Rock" and computer_move == "Scissors") or \
                 (user_move == "Paper" and computer_move == "Rock") or \
                 (user_move == "Scissors" and computer_move == "Paper"):
                result = "POINT FOR YOU!"
                user_score += 1
            else:
                result = "CPU WINS POINT!"
                cpu_score += 1
            
            state = "Result"
            timer = time.time()

    elif state == "Result":
        # Show moves
        cv2.putText(img, f"Move: {user_move}", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Move: {computer_move}", (380, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(img, result, (100, 300), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 0), 3)
        
        # Show result for 2.5 seconds, then go back to counting
        if time.time() - timer > 2.5:
            state = "Counting"
            timer = time.time()

    cv2.imshow("Hands-Free RPS", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()