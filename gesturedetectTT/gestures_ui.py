import cv2
import mediapipe as mp
import pygame

class HandTracker:
    def __init__(self, window_width, window_height):
        self.window_width = window_width
        self.window_height = window_height
        
        # Initialize camera and MediaPipe
        self.cap = cv2.VideoCapture(0)
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Hand data
        self.landmarks = None
        self.hand_detected = False
        self.current_gesture = None

        self.prev_gesture = None
        self.gesture_stable_frames = 0
        self.click_cooldown = 0
        
        # Smoothing
        self.smoothed_pos = None
        self.smoothing_factor = 0.3  # Lower = smoother but more lag
        
    def get_hand_landmarks(self, hand):
        """Extract landmarks once to avoid redundant processing"""
        return [(p.x, p.y, p.z) for p in hand.landmark]
    
    def rock(self, landmarks):
        index_tip, middle_tip, ring_tip, pinky_tip = landmarks[8], landmarks[12], landmarks[16], landmarks[20]
        index_base, middle_base, ring_base, pinky_base = landmarks[5], landmarks[9], landmarks[13], landmarks[17]
        
        all_contracted = (
            index_tip[1] > index_base[1] and
            middle_tip[1] > middle_base[1] and
            ring_tip[1] > ring_base[1] and
            pinky_tip[1] > pinky_base[1]
        )
        return all_contracted

    def paper(self, landmarks):
        thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip = landmarks[4], landmarks[8], landmarks[12], landmarks[16], landmarks[20]
        thumb_base, index_base, middle_base, ring_base, pinky_base = landmarks[2], landmarks[5], landmarks[9], landmarks[13], landmarks[17]
        
        all_extended = (
            thumb_tip[1] < thumb_base[1] and
            index_tip[1] < index_base[1] and
            middle_tip[1] < middle_base[1] and
            ring_tip[1] < ring_base[1] and
            pinky_tip[1] < pinky_base[1]
        )
        return all_extended

    def scissors(self, landmarks):
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        ring_base = landmarks[13]
        pinky_base = landmarks[17]
        
        distance = ((index_tip[0] - middle_tip[0])**2 + (index_tip[1] - middle_tip[1])**2)**0.5
        
        fingers_separated = distance > 0.1
        other_fingers_curled = ring_tip[1] > ring_base[1] and pinky_tip[1] > pinky_base[1]
        
        return fingers_separated and other_fingers_curled

    def o_sign(self, landmarks):
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        distance = ((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)**0.5
        
        middle_base = landmarks[9]
        ring_base = landmarks[13]
        pinky_base = landmarks[17]
        
        other_fingers_extended = (
            middle_tip[1] < middle_base[1] and
            ring_tip[1] < ring_base[1] and
            pinky_tip[1] < pinky_base[1]
        )
        
        if distance < 0.07 and other_fingers_extended:
            x = (thumb_tip[0] + index_tip[0]) / 2
            y = (thumb_tip[1] + index_tip[1]) / 2
            return True, x, y
        return False, None, None
    
    def get_index_finger_pos(self, smooth=True):
        """Get pygame coordinates of index finger tip"""
        if self.landmarks:
            index_tip = self.landmarks[8]
            x = int(index_tip[0] * self.window_width)
            y = int(index_tip[1] * self.window_height)
            
            if smooth:
                if self.smoothed_pos is None:
                    self.smoothed_pos = (x, y)
                else:
                    # Exponential moving average for smoothing
                    smooth_x = self.smoothed_pos[0] * (1 - self.smoothing_factor) + x * self.smoothing_factor
                    smooth_y = self.smoothed_pos[1] * (1 - self.smoothing_factor) + y * self.smoothing_factor
                    self.smoothed_pos = (int(smooth_x), int(smooth_y))
                
                return self.smoothed_pos
            else:
                return (x, y)
    
        return None

    def detect_gesture(self):
        """Detect which gesture is being made"""
        if not self.landmarks:
            return None
        
        # Check gestures in priority order
        is_o, o_x, o_y = self.o_sign(self.landmarks)
        if is_o:
            return "o_sign"
        elif self.scissors(self.landmarks):
            return "scissors"
        elif self.paper(self.landmarks):
            return "paper"
        elif self.rock(self.landmarks):
            return "rock"
        return None
    
    def is_click_gesture(self):
        """Check if o_sign gesture just started (rising edge detection)"""
        if self.click_cooldown > 0:
            return False
        
        # Detect when gesture changes to o_sign
        if self.current_gesture == "o_sign" and self.prev_gesture != "o_sign":
            if self.gesture_stable_frames > 3:  # Require stable detection
                self.click_cooldown = 15  # Cooldown frames
                return True
        
        return False
    
    def update(self):
        """Process camera frame and detect hand"""
        ret, frame = self.cap.read()
        if not ret:
            self.hand_detected = False
            return
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # Reset data
        self.hand_detected = False
        self.landmarks = None
        prev_gesture = self.current_gesture
        self.current_gesture = None
        
        if results.multi_hand_landmarks:
            for hand in results.multi_hand_landmarks:
                self.hand_detected = True
                self.landmarks = self.get_hand_landmarks(hand)
                self.current_gesture = self.detect_gesture()
                break  # Only process first hand
        
        # Track gesture stability
        if self.current_gesture == prev_gesture:
            self.gesture_stable_frames += 1
        else:
            self.gesture_stable_frames = 0
            self.prev_gesture = prev_gesture
        
        # Update cooldown
        if self.click_cooldown > 0:
            self.click_cooldown -= 1
            
    def draw_indicator(self, surface):
        """Draw indicator at index finger position"""
        pos = self.get_index_finger_pos()
        if pos:
            x, y = pos
            
            # Color based on gesture
            colors = {
                "rock": (150, 150, 150),
                "paper": (200, 200, 200),
                "scissors": (255, 100, 100),
                "o_sign": (100, 200, 255)
            }
            color = colors.get(self.current_gesture, (52, 152, 219))
            
            # Draw outer glow
            for i in range(3, 0, -1):
                alpha = 100 - (i * 30)
                radius = 15 + (i * 5)
                glow_surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*color, alpha), (radius, radius), radius)
                surface.blit(glow_surface, (x - radius, y - radius))
            
            # Draw main dot
            pygame.draw.circle(surface, color, (x, y), 10)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 8)
            pygame.draw.circle(surface, color, (x, y), 5)
            
            # Draw gesture name
            if self.current_gesture:
                font = pygame.font.Font(None, 24)
                text = font.render(self.current_gesture.upper(), True, (255, 255, 255))
                surface.blit(text, (x + 15, y - 10))
    
    def cleanup(self):
        """Release camera resources"""
        self.cap.release()
    

def setup_hand_tracking(main_menu):
    """Initialize hand tracking for the main menu"""
    main_menu.hand_tracker = HandTracker(
        main_menu.WINDOW_WIDTH,
        main_menu.WINDOW_HEIGHT
    )

def update_hand_tracking(main_menu):
    """Update hand tracking - call this once per frame"""
    if hasattr(main_menu, 'hand_tracker'):
        main_menu.hand_tracker.update()

def get_hand_position(main_menu):
    """Get current hand position or None"""
    if hasattr(main_menu, 'hand_tracker'):
        return main_menu.hand_tracker.get_index_finger_pos()
    return None

def get_current_gesture(main_menu):
    """Get current gesture being made"""
    if hasattr(main_menu, 'hand_tracker'):
        return main_menu.hand_tracker.current_gesture
    return None

def draw_hand_indicator(main_menu):
    """Draw hand tracking indicator"""
    if hasattr(main_menu, 'hand_tracker'):
        main_menu.hand_tracker.draw_indicator(main_menu.screen)

def cleanup_hand_tracking(main_menu):
    """Clean up hand tracking resources"""
    if hasattr(main_menu, 'hand_tracker'):
        main_menu.hand_tracker.cleanup()

def is_hand_click(main_menu):
    """Check if hand made a click gesture"""
    if hasattr(main_menu, 'hand_tracker'):
        return main_menu.hand_tracker.is_click_gesture()
    return False