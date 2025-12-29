import cv2
import mediapipe as mp
import random
import time
import winsound  # Built-in Windows library for sound

# Initialize Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

def get_gesture(hand_landmarks):
    fingers = []
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
state = "Counting"
timer = time.time()
user_score, cpu_score = 0, 0
user_move, computer_move, result = "", "", ""
last_count = -1

while cap.isOpened():
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)
    h, w, _ = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    current_hand_gesture = "None"
    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            current_hand_gesture = get_gesture(hand_lms)
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS,
                                 mp_draw.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                                 mp_draw.DrawingSpec(color=(255,255,255), thickness=2))

    # --- FANCY UI OVERLAY ---
    # Create a semi-transparent header
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)

    # Score Text
    cv2.putText(img, f"PLAYER: {user_score}", (30, 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, f"CPU: {cpu_score}", (w-200, 50), cv2.FONT_HERSHEY_TRIPLEX, 1, (0, 0, 255), 2)

    # --- GAME LOGIC ---
    if state == "Counting":
        elapsed = time.time() - timer
        countdown = 3 - int(elapsed)
        
        if countdown != last_count and countdown > 0:
            winsound.Beep(600, 200) # Low beep for 3, 2, 1
            last_count = countdown

        # Draw large countdown
        cv2.putText(img, str(countdown), (w//2-50, h//2+50), cv2.FONT_HERSHEY_TRIPLEX, 6, (0, 255, 255), 15)
        
        if countdown <= 0:
            winsound.Beep(1200, 400) # High beep for "GO!"
            user_move = current_hand_gesture
            computer_move = random.choice(["Rock", "Paper", "Scissors"])
            
            if user_move in ["Unknown", "None"]:
                result = "NO HAND!"
            elif user_move == computer_move:
                result = "TIE!"
            elif (user_move == "Rock" and computer_move == "Scissors") or \
                 (user_move == "Paper" and computer_move == "Rock") or \
                 (user_move == "Scissors" and computer_move == "Paper"):
                result = "YOU WIN!"
                user_score += 1
            else:
                result = "CPU WINS!"
                cpu_score += 1
            
            state = "Result"
            timer = time.time()

    elif state == "Result":
        # Draw Result Box
        cv2.rectangle(img, (w//2-250, h//2-100), (w//2+250, h//2+100), (255, 255, 255), -1)
        cv2.putText(img, result, (w//2-180, h//2), cv2.FONT_HERSHEY_TRIPLEX, 2, (0, 0, 0), 3)
        cv2.putText(img, f"CPU chose {computer_move}", (w//2-140, h//2+60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
        
        if time.time() - timer > 2.5:
            state = "Counting"
            timer = time.time()
            last_count = -1

    cv2.imshow("Extreme Rock Paper Scissors", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()