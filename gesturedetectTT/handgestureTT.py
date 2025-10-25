import cv2
import mediapipe as mp

import sys
import os

# Get the absolute path of the directory containing the module you want to import
# For example, if 'my_module.py' is in '../another_directory' relative to the current script
module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game_ui'))

# Add the directory to sys.path
sys.path.insert(0, module_dir) # insert at the beginning for higher priority
import Board

board = Board.Board()

# Define zones with relative coordinates (fractions of the frame)
colored_zones = [
    {"name": "red", "coords": (0, 0, 0.33, 0.2)},       # top-left
    {"name": "yellow", "coords": (0.33, 0, 0.66, 0.2)}, # top-center
    {"name": "green", "coords": (0.66, 0, 1, 0.2)},     # top-right
    {"name": "black", "coords": (0, 0.8, 0.33, 1)},     # bottom-left
    {"name": "purple", "coords": (0.33, 0.8, 0.66, 1)}, # bottom-center
    {"name": "orange", "coords": (0.66, 0.8, 1, 1)},    # bottom-right
    {"name": "blue", "coords": (0, 0.33, 0.33, 0.66)},  # mid-left
    {"name": "brown", "coords": (0.33, 0.33, 0.66, 0.66)}, # center
    {"name": "pink", "coords": (0.66, 0.33, 1, 0.66)}      # mid-right
]

def color_to_row_col(color):
    color_positions = {
        "red": (0, 0),
        "yellow": (0, 1),
        "green": (0, 2),
        "blue": (1, 0),
        "brown": (1, 1),
        "pink": (1, 2),
        "black": (2, 0),
        "purple": (2, 1),
        "orange": (2, 2)
    }
    
    return color_positions.get(color.lower())

zone_color = { 
    "red" : (255,0,0),
    "yellow": (255,255,0),
    "green": (0,255,0),
    "black": (0,0,0),
    "purple": (128,0,128),
    "orange": (255,165,0),
    "blue": (0,0,255),
    "brown": (139,69,19),
    "pink": (255,105,180)
}



# Initialize MediaPipe modules
hand_model = mp.solutions.hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
    static_image_mode=False
)
drawer = mp.solutions.drawing_utils

# Start the webcam
camera = cv2.VideoCapture(0)

while True:
    frame_exists, frame = camera.read()
    if not frame_exists:
        print("No frame captured.")
        break

    # Make frame square for MediaPipe
    h, w, _ = frame.shape
    size = min(h, w)
    frame = frame[0:size, 0:size]

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hands
    hand_results = hand_model.process(rgb_frame)

    
    # Draw zones scaled to frame


        



    # Draw hands and detect "O" gesture
    if hand_results.multi_hand_landmarks:
        for hand in hand_results.multi_hand_landmarks:
            drawer.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)

            landmarks = [(p.x, p.y, p.z) for p in hand.landmark]
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            fingertip_x, fingertip_y, _ = landmarks[8]
            distance = ((thumb_tip[0]-index_tip[0])**2 + (thumb_tip[1]-index_tip[1])**2)**0.5
            if distance < 0.07:
                cv2.putText(frame, "O gesture", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 1)
                for zone in colored_zones:
                    x1_frac, y1_frac, x2_frac, y2_frac = zone["coords"]
                    x1 = int(x1_frac * size)
                    y1 = int(y1_frac * size)
                    x2 = int(x2_frac * size)
                    y2 = int(y2_frac * size)
                    for zone in colored_zones:
                        x1, y1, x2, y2 = zone["coords"]  # fractions 0-1
                        if x1 <= fingertip_x <= x2 and y1 <= fingertip_y <= y2:
                                current_zone = zone["name"]

                                row, col = color_to_row_col(current_zone)

                                board.mark_square(1, row, col)
                                board.print_board()






                
            else:
                cv2.putText(frame, "Detecting...", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2)

    flipped = cv2.flip(frame,3)
    # Show the frame
    cv2.imshow("Hand Tracker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Cleanup
camera.release()
cv2.destroyAllWindows()
hand_model.close()
