# rps_game.py - Rock Paper Scissors game window
import pygame
import cv2
import os
import mediapipe as mp
from rpsai import RPS

class RockPaperScissorsGame:
    def __init__(self, screen, difficulty):
        self.screen = screen
        self.difficulty = difficulty
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Initialize game
        self.game = RPS()
        
        # Game state phases
        self.PHASE_COUNTDOWN = "countdown"
        self.PHASE_CAPTURE = "capture"
        self.PHASE_RESULT = "result"
        self.PHASE_FINISHED = "finished"
        
        self.phase = self.PHASE_COUNTDOWN
        self.phase_start_time = pygame.time.get_ticks()
        self.countdown_value = 3
        self.captured_gesture = None
        
        # Gesture hold tracking
        self.current_held_gesture = None
        self.gesture_hold_start = None
        self.GESTURE_HOLD_TIME = 4000  # 4 seconds in milliseconds
        
        # Load sprites
        self.rps_sprites = self.load_rps_sprites()
        
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            
        # Initialize MediaPipe
        self.hand_model = mp.solutions.hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            static_image_mode=False
        )
        self.drawer = mp.solutions.drawing_utils
        
        # Import gesture detection
        from gestures import get_hand_landmarks, rock, paper, scissors
        self.get_hand_landmarks = get_hand_landmarks
        self.rock = rock
        self.paper = paper
        self.scissors = scissors
        
        # Colors
        self.COLOR_BG = (15, 23, 42)  # Dark blue-gray
        self.COLOR_DIVIDER = (71, 85, 105)  # Slate
        self.COLOR_WIN = (34, 197, 94)  # Green
        self.COLOR_LOSE = (239, 68, 68)  # Red
        self.COLOR_TIE = (251, 191, 36)  # Amber
        self.COLOR_TEXT = (241, 245, 249)  # Light gray
        self.COLOR_TEXT_DIM = (148, 163, 184)  # Dim gray
        self.COLOR_ACCENT = (99, 102, 241)  # Indigo
    
    def load_rps_sprites(self):
        sprites = {}
        sprite_path = os.path.join(os.path.dirname(__file__), 'sprites', 'custom')
        
        # Load RPS icons
        for name in ['rock', 'paper', 'scissors']:
            path = os.path.join(sprite_path, f'{name}_icon.png')
            if os.path.exists(path):
                sprites[name] = pygame.transform.scale(
                    pygame.image.load(path).convert_alpha(),
                    (220, 220)
                )
            else:
                # Create prettier fallback sprites
                surf = pygame.Surface((220, 220), pygame.SRCALPHA)
                colors = {
                    'rock': (239, 68, 68),      # Red
                    'paper': (34, 197, 94),     # Green
                    'scissors': (99, 102, 241)  # Indigo
                }
                
                # Draw outer glow
                for r in range(110, 85, -5):
                    alpha = int((110 - r) * 2)
                    pygame.draw.circle(surf, (*colors[name], alpha), (110, 110), r)
                
                # Draw main circle with gradient effect
                pygame.draw.circle(surf, colors[name], (110, 110), 85)
                
                # Add highlight
                pygame.draw.circle(surf, (255, 255, 255, 60), (95, 95), 30)
                
                # Draw symbol - use ASCII fallback instead of emoji
                font = pygame.font.Font(None, 80)
                symbols = {'rock': 'R', 'paper': 'P', 'scissors': 'S'}
                text = font.render(symbols[name], True, (255, 255, 255))
                surf.blit(text, text.get_rect(center=(110, 110)))
                
                sprites[name] = surf
        
        # Create countdown sprites with animations
        font = pygame.font.Font(None, 200)
        for i in range(1, 4):
            surf = pygame.Surface((250, 250), pygame.SRCALPHA)
            
            # Outer circle
            pygame.draw.circle(surf, (99, 102, 241, 100), (125, 125), 110)
            pygame.draw.circle(surf, (99, 102, 241), (125, 125), 110, 5)
            
            # Number with shadow
            num_text = str(4-i)
            shadow = font.render(num_text, True, (0, 0, 0, 100))
            surf.blit(shadow, shadow.get_rect(center=(128, 128)))
            
            text = font.render(num_text, True, (255, 255, 255))
            surf.blit(text, text.get_rect(center=(125, 125)))
            
            sprites[f'countdown_{i}'] = surf
        
        # GO sprite with emphasis
        go_surf = pygame.Surface((280, 280), pygame.SRCALPHA)
        
        # Pulsing circles
        for r in range(130, 100, -10):
            alpha = int((130 - r) * 3)
            pygame.draw.circle(go_surf, (239, 68, 68, alpha), (140, 140), r)
        
        pygame.draw.circle(go_surf, (239, 68, 68), (140, 140), 100)
        pygame.draw.circle(go_surf, (255, 255, 255), (140, 140), 100, 6)
        
        go_font = pygame.font.Font(None, 140)
        shadow = go_font.render("GO!", True, (0, 0, 0, 150))
        go_surf.blit(shadow, shadow.get_rect(center=(143, 143)))
        
        go_text = go_font.render("GO!", True, (255, 255, 255))
        go_surf.blit(go_text, go_text.get_rect(center=(140, 140)))
        
        sprites['go'] = go_surf
        
        return sprites
    
    def reset_round(self):
        """Reset for a new round"""
        self.phase = self.PHASE_COUNTDOWN
        self.phase_start_time = pygame.time.get_ticks()
        self.countdown_value = 3
        self.captured_gesture = None
        self.current_held_gesture = None
        self.gesture_hold_start = None
    
    def detect_rps_gesture(self, landmarks):
        """Detect rock, paper, or scissors gesture"""
        if self.rock(landmarks):
            return "rock"
        elif self.paper(landmarks):
            return "paper"
        elif self.scissors(landmarks):
            return "scissors"
        return None
    
    def update_phase(self, current_time, detected_gesture):
        """Update game phase based on time and input"""
        elapsed = current_time - self.phase_start_time
        
        if self.phase == self.PHASE_COUNTDOWN:
            # Update countdown every second
            new_countdown = 3 - (elapsed // 1000)
            if new_countdown != self.countdown_value and new_countdown >= 0:
                self.countdown_value = new_countdown
            
            # Move to capture phase after countdown
            if elapsed >= 3000:
                self.phase = self.PHASE_CAPTURE
                self.phase_start_time = current_time
        
        elif self.phase == self.PHASE_CAPTURE:
            # Track gesture holding
            if detected_gesture:
                current_time_ms = pygame.time.get_ticks()
                
                # If this is a new gesture or different from what we're tracking
                if detected_gesture != self.current_held_gesture:
                    self.current_held_gesture = detected_gesture
                    self.gesture_hold_start = current_time_ms
                
                # Check if gesture has been held long enough
                elif not self.captured_gesture:
                    hold_duration = current_time_ms - self.gesture_hold_start
                    if hold_duration >= self.GESTURE_HOLD_TIME:
                        self.captured_gesture = detected_gesture
                        self.game.play(detected_gesture)
            else:
                # No gesture detected, reset tracking
                self.current_held_gesture = None
                self.gesture_hold_start = None
            
            # Move to result phase after extended time (12 seconds total)
            if elapsed >= 12000:
                if not self.captured_gesture:
                    # No gesture detected, treat as timeout/forfeit
                    self.game.play("rock")  # Default to rock
                    self.captured_gesture = "rock"
                
                self.phase = self.PHASE_RESULT
                self.phase_start_time = current_time
        
        elif self.phase == self.PHASE_RESULT:
            # Show results for 3 seconds
            if elapsed >= 3000:
                if self.game.game_finished:
                    self.phase = self.PHASE_FINISHED
                else:
                    self.reset_round()
    
    def draw(self):
        self.screen.fill(self.COLOR_BG)
        
        # Draw camera feed and detect gestures
        detected_gesture = None
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                size = min(h, w)
                frame_square = frame[0:size, 0:size]
                rgb_frame = cv2.cvtColor(frame_square, cv2.COLOR_BGR2RGB)
                
                # Process hands
                hand_results = self.hand_model.process(rgb_frame)
                
                if hand_results.multi_hand_landmarks:
                    for hand in hand_results.multi_hand_landmarks:
                        # Draw landmarks with custom colors
                        self.drawer.draw_landmarks(
                            frame_square, 
                            hand, 
                            mp.solutions.hands.HAND_CONNECTIONS,
                            self.drawer.DrawingSpec(color=(99, 102, 241), thickness=2, circle_radius=4),
                            self.drawer.DrawingSpec(color=(241, 245, 249), thickness=2)
                        )
                        landmarks = self.get_hand_landmarks(hand)
                        detected_gesture = self.detect_rps_gesture(landmarks)
                
                # Display camera with rounded corners effect
                frame_surface = pygame.surfarray.make_surface(
                    cv2.cvtColor(frame_square, cv2.COLOR_BGR2RGB).swapaxes(0,1)
                )
                scaled_frame = pygame.transform.scale(
                    frame_surface, 
                    (self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT)
                )
                self.screen.blit(scaled_frame, (0, 0))
                
                # Add vignette effect to camera
                vignette = pygame.Surface((self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(vignette, (0, 0, 0, 60), vignette.get_rect(), 40)
                self.screen.blit(vignette, (0, 0))
        
        # Draw elegant dividing line
        line_x = self.WINDOW_WIDTH // 2
        pygame.draw.line(self.screen, self.COLOR_DIVIDER, (line_x, 0), (line_x, self.WINDOW_HEIGHT), 4)
        
        # Add subtle glow to divider
        for i in range(1, 4):
            alpha = 20 - (i * 5)
            color_with_alpha = (self.COLOR_ACCENT[0], self.COLOR_ACCENT[1], self.COLOR_ACCENT[2], alpha)
            # Create a surface for alpha blending
            glow_surf = pygame.Surface((1, self.WINDOW_HEIGHT), pygame.SRCALPHA)
            glow_surf.fill(color_with_alpha)
            self.screen.blit(glow_surf, (line_x - i, 0))
            self.screen.blit(glow_surf, (line_x + i, 0))
        
        # Update phase
        current_time = pygame.time.get_ticks()
        self.update_phase(current_time, detected_gesture)
        
        # Draw game area
        self.draw_game_area(detected_gesture)
    
    def draw_game_area(self, detected_gesture):
        right_center_x = self.WINDOW_WIDTH * 3 // 4
        center_y = self.WINDOW_HEIGHT // 2
        
        # Draw title with decorative elements
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render(f"Rock Paper Scissors", True, self.COLOR_TEXT)
        title_rect = title_text.get_rect(center=(right_center_x, 70))
        self.screen.blit(title_text, title_rect)
        
        # Difficulty badge
        diff_font = pygame.font.Font(None, 32)
        diff_text = diff_font.render(self.difficulty.upper(), True, self.COLOR_ACCENT)
        diff_bg = pygame.Surface((diff_text.get_width() + 30, 35), pygame.SRCALPHA)
        pygame.draw.rect(diff_bg, (*self.COLOR_ACCENT, 40), diff_bg.get_rect(), border_radius=8)
        pygame.draw.rect(diff_bg, self.COLOR_ACCENT, diff_bg.get_rect(), 2, border_radius=8)
        diff_bg.blit(diff_text, (15, 5))
        self.screen.blit(diff_bg, (right_center_x - diff_bg.get_width() // 2, 110))
        
        if self.phase == self.PHASE_FINISHED:
            self.draw_game_over(right_center_x, center_y)
        elif self.phase == self.PHASE_COUNTDOWN:
            self.draw_countdown_phase(right_center_x, center_y)
        elif self.phase == self.PHASE_CAPTURE:
            self.draw_capture_phase(right_center_x, center_y, detected_gesture)
        elif self.phase == self.PHASE_RESULT:
            self.draw_result_phase(right_center_x, center_y)
        
        # Draw score bar at bottom
        self.draw_score_bar(right_center_x)
    
    def draw_countdown_phase(self, x, y):
        if self.countdown_value > 0:
            sprite = self.rps_sprites[f'countdown_{self.countdown_value}']
            self.screen.blit(sprite, sprite.get_rect(center=(x, y)))
            
            font = pygame.font.Font(None, 40)
            text = font.render("Get ready with your gesture!", True, self.COLOR_TEXT_DIM)
            self.screen.blit(text, text.get_rect(center=(x, y + 180)))
    
    def draw_capture_phase(self, x, y, detected_gesture):
        sprite = self.rps_sprites['go']
        self.screen.blit(sprite, sprite.get_rect(center=(x, y)))
        
        font = pygame.font.Font(None, 44)
        
        if self.captured_gesture:
            text = font.render(f"Locked in: {self.captured_gesture.upper()}!", True, self.COLOR_ACCENT)
            self.screen.blit(text, text.get_rect(center=(x, y + 200)))
        elif detected_gesture and self.gesture_hold_start:
            # Show hold progress
            current_time = pygame.time.get_ticks()
            hold_duration = current_time - self.gesture_hold_start
            progress = min(hold_duration / self.GESTURE_HOLD_TIME, 1.0)
            
            # Draw progress bar
            bar_width = 400
            bar_height = 30
            bar_x = x - bar_width // 2
            bar_y = y + 180
            
            # Background
            pygame.draw.rect(self.screen, (71, 85, 105), 
                           (bar_x, bar_y, bar_width, bar_height), border_radius=15)
            
            # Progress fill
            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(self.screen, self.COLOR_WIN, 
                               (bar_x, bar_y, fill_width, bar_height), border_radius=15)
            
            # Border
            pygame.draw.rect(self.screen, self.COLOR_ACCENT, 
                           (bar_x, bar_y, bar_width, bar_height), 3, border_radius=15)
            
            # Text above progress bar
            text = font.render(f"Hold {detected_gesture.upper()}... {progress * 100:.0f}%", 
                             True, self.COLOR_TEXT)
            self.screen.blit(text, text.get_rect(center=(x, bar_y - 30)))
        else:
            text = font.render("Show your move and HOLD for 4 seconds!", True, self.COLOR_TEXT)
            self.screen.blit(text, text.get_rect(center=(x, y + 200)))
    
    def draw_result_phase(self, x, y):
        if self.captured_gesture and self.game.computer_choice:
            # Draw move cards
            card_spacing = 280
            
            # Player card
            self.draw_move_card(x - card_spacing // 2, y, 
                              self.captured_gesture, "Your Move", True)
            
            # Computer card
            self.draw_move_card(x + card_spacing // 2, y, 
                              self.game.computer_choice, "Computer", False)
            
            # Draw VS text between cards
            vs_font = pygame.font.Font(None, 72)
            vs_text = vs_font.render("VS", True, self.COLOR_TEXT_DIM)
            self.screen.blit(vs_text, vs_text.get_rect(center=(x, y)))
            
            # Show result below
            if self.game.last_result:
                result_lines = self.game.last_result.split('. ')
                result_text = result_lines[-1] if len(result_lines) > 1 else self.game.last_result
                
                if "You win" in result_text:
                    result_color = self.COLOR_WIN
                elif "Computer wins" in result_text:
                    result_color = self.COLOR_LOSE
                else:
                    result_color = self.COLOR_TIE
                
                result_font = pygame.font.Font(None, 52)
                result_surface = result_font.render(result_text, True, result_color)
                
                # Result background
                result_bg = pygame.Surface((result_surface.get_width() + 40, 60), pygame.SRCALPHA)
                pygame.draw.rect(result_bg, (*result_color, 30), result_bg.get_rect(), border_radius=12)
                pygame.draw.rect(result_bg, result_color, result_bg.get_rect(), 3, border_radius=12)
                result_bg.blit(result_surface, (20, 12))
                
                self.screen.blit(result_bg, result_bg.get_rect(center=(x, y + 200)))
    
    def draw_move_card(self, x, y, move, label, is_player):
        # Card background
        card_width, card_height = 240, 320
        card = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        
        # Glow effect
        glow_color = self.COLOR_ACCENT if is_player else self.COLOR_LOSE
        for i in range(10, 0, -2):
            alpha = (10 - i) * 8
            pygame.draw.rect(card, (*glow_color, alpha), 
                           (i, i, card_width - 2*i, card_height - 2*i), 
                           border_radius=20)
        
        # Main card
        pygame.draw.rect(card, (30, 41, 59), (0, 0, card_width, card_height), border_radius=20)
        pygame.draw.rect(card, glow_color, (0, 0, card_width, card_height), 3, border_radius=20)
        
        # Label
        label_font = pygame.font.Font(None, 36)
        label_surface = label_font.render(label, True, self.COLOR_TEXT)
        card.blit(label_surface, label_surface.get_rect(center=(card_width // 2, 30)))
        
        # Move sprite
        sprite = self.rps_sprites[move]
        sprite_rect = sprite.get_rect(center=(card_width // 2, card_height // 2 + 10))
        card.blit(sprite, sprite_rect)
        
        # Move name
        name_font = pygame.font.Font(None, 32)
        name_surface = name_font.render(move.upper(), True, glow_color)
        card.blit(name_surface, name_surface.get_rect(center=(card_width // 2, card_height - 30)))
        
        self.screen.blit(card, card.get_rect(center=(x, y)))
    
    def draw_game_over(self, x, y):
        # Determine winner
        if self.game.player_score > self.game.computer_score:
            result = "Victory!"
            subtitle = "You defeated the computer!"
            color = self.COLOR_WIN
        elif self.game.computer_score > self.game.player_score:
            result = "Defeat"
            subtitle = "The computer wins this time"
            color = self.COLOR_LOSE
        else:
            result = "Draw"
            subtitle = "It's a tie game!"
            color = self.COLOR_TIE
        
        # Large result text
        result_font = pygame.font.Font(None, 120)
        result_text = result_font.render(result, True, color)
        self.screen.blit(result_text, result_text.get_rect(center=(x, y - 60)))
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 40)
        subtitle_text = subtitle_font.render(subtitle, True, self.COLOR_TEXT_DIM)
        self.screen.blit(subtitle_text, subtitle_text.get_rect(center=(x, y + 20)))
        
        # Final score
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(
            f"Final Score: {self.game.player_score} - {self.game.computer_score}", 
            True, self.COLOR_TEXT
        )
        self.screen.blit(score_text, score_text.get_rect(center=(x, y + 80)))
        
        # Return instruction
        inst_font = pygame.font.Font(None, 36)
        inst_text = inst_font.render("Press ESC to return to menu", True, self.COLOR_TEXT_DIM)
        self.screen.blit(inst_text, inst_text.get_rect(center=(x, y + 160)))
    
    def draw_score_bar(self, x):
        bar_height = 100
        bar_y = self.WINDOW_HEIGHT - bar_height
        
        # Background
        bar_bg = pygame.Surface((self.WINDOW_WIDTH // 2, bar_height), pygame.SRCALPHA)
        pygame.draw.rect(bar_bg, (30, 41, 59, 200), bar_bg.get_rect())
        pygame.draw.line(bar_bg, self.COLOR_DIVIDER, (0, 0), (self.WINDOW_WIDTH // 2, 0), 2)
        self.screen.blit(bar_bg, (self.WINDOW_WIDTH // 2, bar_y))
        
        # Round progress
        round_font = pygame.font.Font(None, 36)
        round_text = round_font.render(
            f"Round {self.game.rounds_played}/{self.game.max_rounds}", 
            True, self.COLOR_TEXT_DIM
        )
        self.screen.blit(round_text, round_text.get_rect(center=(x, bar_y + 25)))
        
        # Score
        score_font = pygame.font.Font(None, 48)
        score_str = f"{self.game.player_score}  -  {self.game.computer_score}"
        score_text = score_font.render(score_str, True, self.COLOR_TEXT)
        self.screen.blit(score_text, score_text.get_rect(center=(x, bar_y + 65)))
        
        # Player and Computer labels
        label_font = pygame.font.Font(None, 28)
        player_label = label_font.render("YOU", True, self.COLOR_ACCENT)
        comp_label = label_font.render("CPU", True, self.COLOR_LOSE)
        
        self.screen.blit(player_label, player_label.get_rect(center=(x - 100, bar_y + 65)))
        self.screen.blit(comp_label, comp_label.get_rect(center=(x + 100, bar_y + 65)))
    
    def handle_event(self, event):
        """Handle pygame events"""
        # Events are now handled internally by phase system
        pass
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        if hasattr(self, 'hand_model'):
            self.hand_model.close()