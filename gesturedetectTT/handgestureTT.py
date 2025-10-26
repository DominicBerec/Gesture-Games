import cv2

from gestures import get_hand_landmarks, o_sign, paper, rock, scissors
import mediapipe as mp

import sys
import os

# Get the absolute path of the directory containing the module you want to import
# For example, if 'my_module.py' is in '../another_directory' relative to the current script
module_dir1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'game_ui'))
module_dir2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gemini_enemy'))


# Add the directory to sys.path
sys.path.insert(0, module_dir1) # insert at the beginning for higher priority
sys.path.insert(0, module_dir2) # insert at the beginning for higher priority

from ttai import call_tt
import board

board = board.Board()

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
def draw_zone_borders(frame, colored_zones, zone_color, size):
    """Draw colored borders around each zone"""
    frame_thickness = 20
    for zone in colored_zones:
        x1_frac, y1_frac, x2_frac, y2_frac = zone["coords"]
        x1 = int(x1_frac * size)
        y1 = int(y1_frac * size)
        x2 = int(x2_frac * size)
        y2 = int(y2_frac * size)
        color = zone_color[zone["name"]]
        
        if y1 == 0:
            cv2.line(frame, (x1, 0), (x2, 0), color, frame_thickness)
        if y2 == size:
            cv2.line(frame, (x1, size-1), (x2, size-1), color, frame_thickness)
        if x1 == 0:
            cv2.line(frame, (0, y1), (0, y2), color, frame_thickness)
        if x2 == size:
            cv2.line(frame, (size-1, y1), (size-1, y2), color, frame_thickness)

def find_zone_at_position(x, y, colored_zones):
    """Find which zone contains the given coordinates"""
    for zone in colored_zones:
        x1, y1, x2, y2 = zone["coords"]
        if x1 <= x <= x2 and y1 <= y <= y2:
            return zone["name"]
    return None

def handle_o_gesture(frame, board, colored_zones, x, y):
    """Handle the O gesture detection and game logic"""

    if board.game_over:
        return
    
    zone_name = find_zone_at_position(x, y, colored_zones)
    if zone_name:
        row, col = color_to_row_col(zone_name)
        success = board.mark_square("O", row, col)
        
        if board.game_over:
            return
            
        if success:
            print("Success")
            board.print_board()
            x_move, y_move = call_tt(board.board)
            board.mark_square("X", x_move, y_move)
            board.print_board()
    


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

    frame = cv2.flip(frame,1)

    # Make frame square for MediaPipe
    h, w, _ = frame.shape
    size = min(h, w)
    frame = frame[0:size, 0:size]

    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process hands
    hand_results = hand_model.process(rgb_frame)

    # Draw hands and detect "O" gesture
    if hand_results.multi_hand_landmarks:
        for hand in hand_results.multi_hand_landmarks:
            # Draw landmarks ONCE
            drawer.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
            
            # Extract landmarks ONCE
            landmarks = get_hand_landmarks(hand)
            
            # Draw zone borders
            draw_zone_borders(frame, colored_zones, zone_color, size)
            
            # Check gestures in priority order
            is_o_sign, fingertip_x, fingertip_y = o_sign(landmarks)
            
            if is_o_sign:
                handle_o_gesture(frame, board, colored_zones, fingertip_x, fingertip_y)
                cv2.putText(frame, "O gesture", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 1)
            elif scissors(landmarks):
                cv2.putText(frame, "Scissors", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 1)
            elif paper(landmarks):
                cv2.putText(frame, "Paper", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 1)
            elif rock(landmarks):
                cv2.putText(frame, "Rock", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 1)
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
