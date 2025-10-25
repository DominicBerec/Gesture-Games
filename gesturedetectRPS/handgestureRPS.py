import cv2
import mediapipe as mp

# Initialize MediaPipe
hand_model = mp.solutions.hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
    static_image_mode=False
)
drawer = mp.solutions.drawing_utils
camera = cv2.VideoCapture(0)

Scissors = False

# --- MAIN LOOP ---
while True:
    frame_exists, frame = camera.read()
    if not frame_exists:
        print("No frame captured.")
        break
    frame = cv2.flip(frame,3)

    # Flip the frame ONLY if needed (try both to test)
    # Try flip 1 first; if text is mirrored, change to 0 or remove flip.
    h , w, _ = frame.shape
    size = min(h,w)
    frame = frame[0:size, 0:size]  # ← flip horizontally for mirror-like movement

    # Process this frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_results = hand_model.process(rgb_frame)


    if hand_results.multi_hand_landmarks:
        for hand in hand_results.multi_hand_landmarks:
            drawer.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
            landmarks = [(p.x, p.y, p.z) for p in hand.landmark]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]

            # Distance between fingertips
            distance = ((index_tip[0] - middle_tip[0])**2 +
                        (index_tip[1] - middle_tip[1])**2)**0.5

            if distance > 0.1:
                cv2.putText(frame, "Scissors", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2,(0, 255, 0),1)
                Scissors = True
            else:
                cv2.putText(frame, "Detecting...", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2,(255, 255, 255),2)
    # Add text directly on the display frame
    

    # Show window
    cv2.imshow("Hand Tracker", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()
hand_model.close()
