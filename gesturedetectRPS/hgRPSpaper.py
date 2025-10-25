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

Paper = False

while True:
    frame_exists, frame = camera.read()
    if not frame_exists:
        print("No frame captured.")
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    size = min(h, w)
    frame = frame[0:size, 0:size]

    # Process this frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hand_results = hand_model.process(rgb_frame)

    message = "No hand detected"

    if hand_results.multi_hand_landmarks:
        for hand in hand_results.multi_hand_landmarks:
            drawer.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
            landmarks = [(p.x, p.y, p.z) for p in hand.landmark]

            # Get fingertip landmarks
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]

            # Get base landmarks (knuckles)
            thumb_base = landmarks[2]
            index_base = landmarks[5]
            middle_base = landmarks[9]
            ring_base = landmarks[13]
            pinky_base = landmarks[17]

            # Check if all fingers are extended (tip y < base y for upright hand)
            # NOTE: in Mediapipe, smaller y = higher up on the screen
            all_extended = (
                thumb_tip[1] < thumb_base[1] and
                index_tip[1] < index_base[1] and
                middle_tip[1] < middle_base[1] and
                ring_tip[1] < ring_base[1] and
                pinky_tip[1] < pinky_base[1]
            )

            if all_extended:
                message = "Paper"
                Paper = True
            else:
                message = "Detecting..."

    # Draw message
    cv2.putText(frame, message, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2,
                (0, 255, 0) if message == "Paper" else (255, 255, 255), 3)

    cv2.imshow("Hand Tracker", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

camera.release()
cv2.destroyAllWindows()
hand_model.close()
