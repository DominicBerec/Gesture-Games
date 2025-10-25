import cv2
import mediapipe as mp

# Initialize MediaPipe modules
hand_model = mp.solutions.hands.Hands(   # creates the hand detector
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
drawer = mp.solutions.drawing_utils      # for drawing landmarks and lines

# Start the webcam
camera = cv2.VideoCapture(0)

while True:
    frame_exists, frame = camera.read()
    if not frame_exists:
        print("No frame captured.")
        break

    # Convert OpenCV's BGR image to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame through MediaPipe to find hands
    hand_results = hand_model.process(rgb_frame)

    # If any hands are detected
    if hand_results.multi_hand_landmarks:
        for hand in hand_results.multi_hand_landmarks:

            # Draw the hand connections and landmarks on the image
            drawer.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)

            # Create a list of (x, y, z) coordinates for the 21 landmarks
            landmarks = []
            for point in hand.landmark:
                landmarks.append((point.x, point.y, point.z))

            # Example: access thumb and index finger tips
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]

            # Calculate distance between them to detect an "O" gesture
            distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5
            if distance < 0.05:
                cv2.putText(frame, "O gesture", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            else:
                cv2.putText(frame, "Detecting...", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    # Flip horizontally so it looks like a mirror
    flipped = cv2.flip(frame, 2)

    # Display the frame
    cv2.imshow("Hand Tracker",flipped)

    # Exit when pressing ESC
    if cv2.waitKey(5) & 0xFF == 27:
        break

# When done, release resources
camera.release()
cv2.destroyAllWindows()
hand_model.close()
