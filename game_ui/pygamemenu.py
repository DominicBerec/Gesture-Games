

import pygame
import sys
import math
import random
import os
import cv2
import numpy as np
import mediapipe as mp
from pygame import gfxdraw

# Add necessary module paths
module_dir1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gesturedetectTT'))
module_dir2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gemini_enemy'))

sys.path.insert(0, module_dir1)
sys.path.insert(0, module_dir2)

# Import game components
from Board import Board
from rpsai import RPS
from ttai import call_tt, easy_tt_random, medium_tt
from gestures_ui import (cleanup_hand_tracking, get_current_gesture, 
                      get_hand_position, setup_hand_tracking, 
                      update_hand_tracking, draw_hand_indicator, 
                      is_hand_click)


# Add the directory to sys.path
sys.path.insert(0, module_dir1) # insert at the beginning for higher priority


from gestures_ui import cleanup_hand_tracking, get_current_gesture, get_hand_position, setup_hand_tracking, update_hand_tracking, draw_hand_indicator, is_hand_click

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.load_sprites()
    
    def load_sprites(self):
        sprite_paths = {
            'ancient': 'sprites/9-Slice/Ancient',
            'colored': 'sprites/9-Slice/Colored',
            'outline': 'sprites/9-Slice/Outline',

        }
        
        for style, path in sprite_paths.items():
            style_sprites = {}
            full_path = os.path.join(os.path.dirname(__file__), path)
            if os.path.exists(full_path):
                for file in os.listdir(full_path):
                    if file.endswith('.png'):
                        sprite_name = os.path.splitext(file)[0]
                        sprite_path = os.path.join(full_path, file)
                        style_sprites[sprite_name] = pygame.image.load(sprite_path).convert_alpha()
            self.sprites[style] = style_sprites
    
    def get_sprite(self, style, name):
        return self.sprites.get(style, {}).get(name)

    def draw_9slice(self, surface, style, x, y, width, height, scale=1):
        # Get corner and edge sprites
        top_left = self.get_sprite(style, 'top_left')
        top_right = self.get_sprite(style, 'top_right')
        bottom_left = self.get_sprite(style, 'bottom_left')
        bottom_right = self.get_sprite(style, 'bottom_right')
        left = self.get_sprite(style, 'left')
        right = self.get_sprite(style, 'right')
        top = self.get_sprite(style, 'top')
        bottom = self.get_sprite(style, 'bottom')
        center = self.get_sprite(style, 'center')
        
        if not all([top_left, top_right, bottom_left, bottom_right, 
                   left, right, top, bottom, center]):
            return
        
        # Scale sprites
        slice_size = 16 * scale
        
        # Draw corners
        surface.blit(pygame.transform.scale(top_left, (slice_size, slice_size)), (x, y))
        surface.blit(pygame.transform.scale(top_right, (slice_size, slice_size)), (x + width - slice_size, y))
        surface.blit(pygame.transform.scale(bottom_left, (slice_size, slice_size)), (x, y + height - slice_size))
        surface.blit(pygame.transform.scale(bottom_right, (slice_size, slice_size)), (x + width - slice_size, y + height - slice_size))
        
        # Draw edges
        for i in range(slice_size, width - slice_size, slice_size):
            surface.blit(pygame.transform.scale(top, (slice_size, slice_size)), (x + i, y))
            surface.blit(pygame.transform.scale(bottom, (slice_size, slice_size)), (x + i, y + height - slice_size))
        
        for i in range(slice_size, height - slice_size, slice_size):
            surface.blit(pygame.transform.scale(left, (slice_size, slice_size)), (x, y + i))
            surface.blit(pygame.transform.scale(right, (slice_size, slice_size)), (x + width - slice_size, y + i))
        
        # Draw center
        for i in range(slice_size, width - slice_size, slice_size):
            for j in range(slice_size, height - slice_size, slice_size):
                surface.blit(pygame.transform.scale(center, (slice_size, slice_size)), (x + i, y + j))

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.size = random.randint(2, 4)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(200, 255))
        self.life = random.randint(30, 90)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1
        self.size = max(0, self.size - 0.05)

    def draw(self, surface):
        if self.size > 0:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))

class GameSelect:
    def __init__(self, screen, sprite_manager):
        self.screen = screen
        self.sprite_manager = sprite_manager
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Box dimensions - more prominent boxes with fixed spacing
        self.box_width = 400  # Slightly smaller width
        self.box_height = 500  # Slightly smaller height
        self.box_spacing = 200  # Increased spacing between boxes
        
        # Create game boxes - centered and elevated
        center_y = self.WINDOW_HEIGHT // 2 - 50  # Slightly elevated from center
        total_width = (2 * self.box_width) + self.box_spacing
        left_x = (self.WINDOW_WIDTH - total_width) // 2
        
        self.rps_box = pygame.Rect(left_x, center_y - self.box_height//2,
                                 self.box_width, self.box_height)
        self.ttt_box = pygame.Rect(left_x + self.box_width + self.box_spacing,
                                 center_y - self.box_height//2,
                                 self.box_width, self.box_height)
        
        # Load game-specific sprites
        self.load_game_sprites()
        
        # Create background particles system
        self.particles = []
        self.last_particle_time = 0
        
    def load_game_sprites(self):
        # Scale factor for game sprites
        self.icon_size = 128
        
        # Load RPS sprites from custom folder
        sprite_path = os.path.join(os.path.dirname(__file__), 'sprites', 'custom')
        
        # Create RPS sprites with loaded images
        self.rps_sprites = {
            'rock': self.load_and_scale_sprite(os.path.join(sprite_path, 'rock_icon.png')),
            'paper': self.load_and_scale_sprite(os.path.join(sprite_path, 'paper_icon.png')),
            'scissors': self.load_and_scale_sprite(os.path.join(sprite_path, 'scissors_icon.png'))
        }
        
        # Create TTT sprites
        self.ttt_sprites = {
            'x': self.load_and_scale_sprite(os.path.join(sprite_path, 'x.png')),
            'o': self.load_and_scale_sprite(os.path.join(sprite_path, 'o.png'))
        }
    
    def load_and_scale_sprite(self, path):
        try:
            # Create a default sprite if file doesn't exist
            if not os.path.exists(path):
                surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                pygame.draw.circle(surface, (200, 200, 200, 200), 
                                (self.icon_size//2, self.icon_size//2), 
                                self.icon_size//2)
                return surface
            
            # Load and scale the sprite
            image = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(image, (self.icon_size, self.icon_size))
        except:
            # Fallback if loading fails
            surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
            pygame.draw.circle(surface, (200, 200, 200, 200), 
                            (self.icon_size//2, self.icon_size//2), 
                            self.icon_size//2)
            return surface
    
    def create_circle_icon(self, symbol, color):
        surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        
        # Draw circle background
        pygame.draw.circle(surface, (*color, 200), (self.icon_size//2, self.icon_size//2), self.icon_size//2)
        
        # Draw symbol
        font = pygame.font.Font(None, self.icon_size)
        text = font.render(symbol, True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.icon_size//2, self.icon_size//2))
        surface.blit(text, text_rect)
        
        return surface
    
    def draw_mischievous_agent(self, x, y):
        # Draw the agent with a mischievous pose
        scale = 10
        pygame.draw.rect(self.screen, (41, 128, 185), (x, y, 30*scale, 30*scale))  # Head
        # Glasses with a tilted angle for mischievous look
        pygame.draw.rect(self.screen, (0, 0, 0), (x + 5*scale, y + 10*scale, 20*scale, 7*scale))
        # Smirk
        pygame.draw.arc(self.screen, (0, 0, 0), 
                       (x + 5*scale, y + 15*scale, 20*scale, 10*scale), 
                       0, 3.14, 2)
    
    def draw(self):
        # Use the shared background if it exists
        if MainMenu.current_background:
            self.screen.blit(MainMenu.current_background, (0, 0))
        else:
            # Fallback to gradient background
            gradient_rect = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            gradient_rect.fill((44, 62, 80))  # Dark blue background
            self.screen.blit(gradient_rect, (0, 0))
        
        # Draw game boxes with modern style
        for box, title, sprites in [
            (self.rps_box, "Rock Paper Scissors", self.rps_sprites),
            (self.ttt_box, "Tic Tac Toe", self.ttt_sprites)
        ]:
            # Draw box background with rounded corners
            pygame.draw.rect(self.screen, (52, 73, 94), box, border_radius=30)  # Darker blue
            pygame.draw.rect(self.screen, (41, 128, 185), box, border_radius=30, width=3)  # Blue border
            
            # Draw title
            title_font = pygame.font.Font(None, 72)
            title_text = title_font.render(title, True, (255, 255, 255))
            title_rect = title_text.get_rect(centerx=box.centerx, top=box.top + 40)
            self.screen.blit(title_text, title_rect)
            
            # Draw game-specific content
            if box == self.rps_box:
                # Draw RPS sprites in a triangle formation
                center_x, center_y = box.centerx, box.centery
                spacing = self.icon_size + 30  # Increased spacing
                
                # Load and draw hand icons from custom sprites folder
                custom_path = os.path.join(os.path.dirname(__file__), 'sprites', 'custom')
                hand_icons = ['rock_icon', 'paper_icon', 'scissors_icon']
                
                # Define positions in a triangle formation
                positions = [
                    (center_x, center_y - spacing),  # Top center
                    (center_x - spacing, center_y + spacing),  # Bottom left
                    (center_x + spacing, center_y + spacing)   # Bottom right
                ]
                
                for i, icon in enumerate(hand_icons):
                    icon_path = os.path.join(custom_path, f'{icon}.png')
                    try:
                        icon_surface = pygame.image.load(icon_path).convert_alpha()
                        icon_surface = pygame.transform.scale(icon_surface, (self.icon_size, self.icon_size))
                    except:
                        # Fallback if sprite not found
                        icon_surface = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                        pygame.draw.rect(icon_surface, (200, 200, 200, 200), 
                                      (0, 0, self.icon_size, self.icon_size))
                    
                    x = positions[i][0] - self.icon_size // 2
                    y = positions[i][1] - self.icon_size // 2
                    self.screen.blit(icon_surface, (x, y))
            else:
                # Draw TTT preview with custom X and O
                center_x, center_y = box.centerx, box.centery
                positions = [
                    (center_x - 100, center_y - 50),
                    (center_x + 100, center_y - 50),
                    (center_x, center_y + 50)
                ]
                
                for i, pos in enumerate(positions):
                    if i % 2 == 0:  # Draw X
                        x = pos[0] - self.icon_size//2
                        y = pos[1] - self.icon_size//2
                        pygame.draw.line(self.screen, (255, 100, 100), 
                                       (x + 10, y + 10), 
                                       (x + self.icon_size - 10, y + self.icon_size - 10), 
                                       6)
                        pygame.draw.line(self.screen, (255, 100, 100), 
                                       (x + self.icon_size - 10, y + 10), 
                                       (x + 10, y + self.icon_size - 10), 
                                       6)
                    else:  # Draw O
                        pygame.draw.circle(self.screen, (100, 100, 255),
                                        (pos[0], pos[1]),
                                        self.icon_size//2 - 10, 6)
            
            # Draw hover effect if mouse is over the box
            mouse_pos = pygame.mouse.get_pos()
            if box.collidepoint(mouse_pos):
                glow = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
                pygame.draw.rect(glow, (41, 128, 185, 50), glow.get_rect(), border_radius=30)
                self.screen.blit(glow, box)
    
    def handle_click(self, pos):
        if self.rps_box.collidepoint(pos):
            return "RPS"
        elif self.ttt_box.collidepoint(pos):
            return "TTT"
        return None

class DifficultySelect:
    def __init__(self, screen, game_type):
        self.screen = screen
        self.game_type = game_type
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Box dimensions
        self.box_width = 300
        self.box_height = 400
        self.box_spacing = 50
        
        # Create difficulty boxes - centered horizontally
        total_width = (3 * self.box_width) + (2 * self.box_spacing)
        start_x = (self.WINDOW_WIDTH - total_width) // 2
        center_y = self.WINDOW_HEIGHT // 2 - self.box_height // 2
        
        self.difficulties = [
            {
                'name': 'Easy',
                'rect': pygame.Rect(start_x, center_y, self.box_width, self.box_height),
                'color': (46, 204, 113)  # Green
            },
            {
                'name': 'Medium',
                'rect': pygame.Rect(start_x + self.box_width + self.box_spacing, center_y, 
                                  self.box_width, self.box_height),
                'color': (241, 196, 15)  # Yellow
            },
            {
                'name': 'Hard',
                'rect': pygame.Rect(start_x + (self.box_width + self.box_spacing) * 2, 
                                  center_y, self.box_width, self.box_height),
                'color': (231, 76, 60)  # Red
            }
        ]
    
    def draw(self):
        # Draw background (using the shared background)
        if MainMenu.current_background:
            self.screen.blit(MainMenu.current_background, (0, 0))
        else:
            self.screen.fill((44, 62, 80))
        
        # Draw title
        font = pygame.font.Font(None, 74)
        title = f"Select {self.game_type} Difficulty"
        title_surface = font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw difficulty boxes
        for difficulty in self.difficulties:
            # Draw box with glow effect on hover
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = difficulty['rect'].collidepoint(mouse_pos)
            
            # Box background
            pygame.draw.rect(self.screen, difficulty['color'], difficulty['rect'], 
                           border_radius=15)
            
            # Hover effect
            if is_hovered:
                glow = pygame.Surface((difficulty['rect'].width, difficulty['rect'].height), 
                                    pygame.SRCALPHA)
                pygame.draw.rect(glow, (*difficulty['color'], 100), 
                               glow.get_rect(), border_radius=15)
                self.screen.blit(glow, difficulty['rect'])
            
            # Draw difficulty name
            font = pygame.font.Font(None, 48)
            text = font.render(difficulty['name'], True, (255, 255, 255))
            text_rect = text.get_rect(center=difficulty['rect'].center)
            self.screen.blit(text, text_rect)
    
    def handle_click(self, pos):
        for difficulty in self.difficulties:
            if difficulty['rect'].collidepoint(pos):
                return self.game_type, difficulty['name'].lower()
        return None

class GameWindow:
    def __init__(self, screen, game_type, difficulty):
        self.screen = screen
        self.game_type = game_type
        self.difficulty = difficulty
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Initialize game specific components based on game type
        if game_type == "TTT":
            self.board = Board()
            self.game = None
        elif game_type == "RPS":
            self.board = None
            self.game = RPS()
        else:
            raise ValueError(f"Invalid game type: {game_type}")
        
        # Initialize game state variables
        self.countdown = 3
        self.countdown_timer = None
        self.last_gesture = None
        self.last_move = None
        self.waiting_for_move = False
        self.move_locked = False
        self.round_end_timer = None
        
        # Load game sprites
        self.rps_sprites = self.load_rps_sprites() if game_type == "RPS" else None
            
        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            
        # Initialize MediaPipe with same settings as handgestureTT.py
        self.hand_model = mp.solutions.hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            static_image_mode=False
        )
        self.drawer = mp.solutions.drawing_utils
            
        # Margins and dimensions for game board
        self.cell_size = 150
        self.board_width = self.cell_size * 3
        self.board_height = self.cell_size * 3
        self.board_x = self.WINDOW_WIDTH // 2 + (self.WINDOW_WIDTH // 4 - self.board_width // 2)
        self.board_y = (self.WINDOW_HEIGHT - self.board_height) // 2
        
        # Import gesture detection functions
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gesturedetectTT'))
        from gestures import get_hand_landmarks, o_sign, paper, rock, scissors
        self.get_hand_landmarks = get_hand_landmarks
        self.o_sign = o_sign
        
        # Initialize first round
        if game_type == "RPS":
            self.reset_rps_round()
        
    def update(self):
        update_hand_tracking(self)
        
        ret, frame = self.cap.read()
        if ret:
            # Flip the frame horizontally for a mirror effect
            frame = cv2.flip(frame, 1)
            
            # Resize the frame to fit half the screen
            frame = cv2.resize(frame, (self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT))
            
            # Convert the frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create surface from the frame
            frame = frame.swapaxes(0, 1)
            pygame_surface = pygame.surfarray.make_surface(frame)
            
            return pygame_surface
        return None
    
    def draw(self):
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Flip the frame horizontally for selfie view
                frame = cv2.flip(frame, 1)
                
                # Make frame square for consistent detection
                h, w, _ = frame.shape
                size = min(h, w)
                frame_square = frame[0:size, 0:size]
                
                # Convert to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame_square, cv2.COLOR_BGR2RGB)
                
                # Process hands
                hand_results = self.hand_model.process(rgb_frame)
                
                # Draw hands and detect "O" gesture
                if hand_results.multi_hand_landmarks:
                    for hand in hand_results.multi_hand_landmarks:
                        # Draw landmarks
                        self.drawer.draw_landmarks(frame_square, hand, mp.solutions.hands.HAND_CONNECTIONS)
                        
                        # Extract landmarks and check for O gesture
                        landmarks = self.get_hand_landmarks(hand)
                        is_o_sign, fingertip_x, fingertip_y = self.o_sign(landmarks)
                        
                        if is_o_sign:
                            # Map fingertip position to board position
                            rel_x = fingertip_x  # Already normalized 0-1
                            rel_y = fingertip_y  # Already normalized 0-1
                            
                            # Convert to board coordinates
                            row = int(rel_y * 3)
                            col = int(rel_x * 3)
                            
                            # Try to make a move
                            if 0 <= row < 3 and 0 <= col < 3 and self.board.board[row][col] == ' ':
                                if self.board.mark_square('O', row, col):
                                    # Make AI move based on difficulty
                                    if not self.board.game_over:
                                        if self.difficulty == 'easy':
                                            import random
                                            empty_cells = [(r, c) for r in range(3) for c in range(3)
                                                        if self.board.board[r][c] == ' ']
                                            if empty_cells:
                                                ai_row, ai_col = random.choice(empty_cells)
                                                self.board.mark_square('X', ai_row, ai_col)
                                        else:  # medium or hard
                                            from ttai import call_tt
                                            ai_move = call_tt(self.board.board)
                                            if ai_move:
                                                self.board.mark_square('X', ai_move[0], ai_move[1])
                
                # Convert frame for display
                frame_surface = pygame.surfarray.make_surface(
                    cv2.cvtColor(frame_square, cv2.COLOR_BGR2RGB).swapaxes(0,1)
                )
                
                # Scale to fit left half of screen
                scaled_frame = pygame.transform.scale(
                    frame_surface, 
                    (self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT)
                )
                
                # Draw camera view on left half
                self.screen.blit(scaled_frame, (0, 0))
            else:
                # Show error message if frame capture failed
                font = pygame.font.Font(None, 36)
                text = font.render("Camera Error: Could not capture frame", True, (255, 0, 0))
                text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 4, self.WINDOW_HEIGHT // 2))
                self.screen.blit(text, text_rect)
        
        # Draw dividing line
        pygame.draw.line(self.screen, (255, 255, 255),
                        (self.WINDOW_WIDTH // 2, 0),
                        (self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT), 2)
        
        if self.game_type == "TTT":
            # Draw game board on right half
            self.draw_ttt_game()
            
            # Draw titles
            font = pygame.font.Font(None, 36)
            # Camera view title
            text = font.render("Camera View - Make 'O' gesture to place your mark", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 4, 30))
            self.screen.blit(text, text_rect)
            
            # Game view title
            text = font.render(f"Tic Tac Toe - {self.difficulty.capitalize()} Mode", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH * 3 // 4, 30))
            self.screen.blit(text, text_rect)
            
            # Draw instructions
            font = pygame.font.Font(None, 24)
            instructions = [
                "Instructions:",
                "1. Make an 'O' gesture with your hand in the camera view",
                "2. Position the gesture over a square to place your mark",
                "3. Press ESC to return to main menu"
            ]
            for i, line in enumerate(instructions):
                text = font.render(line, True, (255, 255, 255))
                self.screen.blit(text, (10, self.WINDOW_HEIGHT - 100 + i * 25))
        else:
            self.draw_rps_game()
            
        # Draw hand indicator if needed
        draw_hand_indicator(self)
    
    def reset_rps_round(self):
        """Reset the state for a new RPS round"""
        self.countdown = 3
        self.countdown_timer = pygame.time.get_ticks()
        self.last_move = None
        self.waiting_for_move = False
        self.move_locked = False
        self.round_end_timer = None
    
    def draw_ttt_game(self):
        # Draw board on the right half of the screen
        cell_size = 150
        board_width = cell_size * 3
        board_height = cell_size * 3
        board_x = self.WINDOW_WIDTH // 2 + (self.WINDOW_WIDTH // 4 - board_width // 2)
        board_y = (self.WINDOW_HEIGHT - board_height) // 2
        
        # Draw grid
        # Draw outer border
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (board_x, board_y, board_width, board_height), 2)
        
        # Draw inner grid lines
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(self.screen, (255, 255, 255),
                           (board_x + i * cell_size, board_y),
                           (board_x + i * cell_size, board_y + board_height), 2)
            # Horizontal lines
            pygame.draw.line(self.screen, (255, 255, 255),
                           (board_x, board_y + i * cell_size),
                           (board_x + board_width, board_y + i * cell_size), 2)
        
        # Draw X's and O's
        for row in range(3):
            for col in range(3):
                x = board_x + col * cell_size
                y = board_y + row * cell_size
                if self.board.board[row][col] == 'X':
                    # Draw X (red)
                    pygame.draw.line(self.screen, (255, 0, 0),
                                   (x + 20, y + 20),
                                   (x + cell_size - 20, y + cell_size - 20), 3)
                    pygame.draw.line(self.screen, (255, 0, 0),
                                   (x + cell_size - 20, y + 20),
                                   (x + 20, y + cell_size - 20), 3)
                elif self.board.board[row][col] == 'O':
                    # Draw O (blue)
                    pygame.draw.circle(self.screen, (0, 0, 255),
                                    (x + cell_size // 2, y + cell_size // 2),
                                    cell_size // 2 - 20, 3)
        
        # Handle gesture input and game logic
        gesture = get_current_gesture(self)
        hand_pos = get_hand_position(self)
        
        if gesture == "o_sign" and hand_pos and not self.board.game_over:
            # Convert hand position to board coordinates (from camera view)
            hand_x, hand_y = hand_pos
            if hand_x < self.WINDOW_WIDTH // 2:  # Only process gestures in camera view
                row = int((hand_y / self.WINDOW_HEIGHT) * 3)
                col = int((hand_x / (self.WINDOW_WIDTH // 2)) * 3)
                
                if 0 <= row < 3 and 0 <= col < 3 and self.board.board[row][col] == ' ':
                    if self.board.mark_square('O', row, col):
                        # Make AI move based on difficulty
                        if not self.board.game_over:
                            if self.difficulty == 'easy':
                                import random
                                empty_cells = [(r, c) for r in range(3) for c in range(3) 
                                             if self.board.board[r][c] == ' ']
                                if empty_cells:
                                    ai_row, ai_col = random.choice(empty_cells)
                                    self.board.mark_square('X', ai_row, ai_col)
                            elif self.difficulty == 'medium':
                                from ttai import medium_tt
                                ai_move = medium_tt(self.board.board)
                                if ai_move:
                                    self.board.mark_square('X', ai_move[0], ai_move[1])
                            else:  # hard
                                from ttai import call_tt
                                ai_move = call_tt(self.board.board)
                                if ai_move:
                                    self.board.mark_square('X', ai_move[0], ai_move[1])
        
        # Draw game status
        font = pygame.font.Font(None, 48)
        status_text = ""
        if self.board.game_over:
            winner = self.board.win_check()
            if winner:
                status_text = f"Player {winner} wins!"
            else:
                status_text = "It's a tie!"
        else:
            status_text = "Make an 'O' gesture in the camera view to place your mark"
        
        text = font.render(status_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH * 3 // 4, self.WINDOW_HEIGHT - 50))
        self.screen.blit(text, text_rect)
    
    def load_rps_sprites(self):
        sprites = {}
        sprite_path = os.path.join(os.path.dirname(__file__), 'sprites', 'custom')
        
        # Load the game sprites
        sprite_names = {
            'rock': 'rock_icon',
            'paper': 'paper_icon',
            'scissors': 'scissors_icon'
        }
        
        # Create countdown numbers with brighter colors and outline
        font = pygame.font.Font(None, 150)
        for i in range(1, 4):
            surf = pygame.Surface((200, 200), pygame.SRCALPHA)
            # Draw outline
            outline_text = font.render(str(4-i), True, (0, 0, 0))
            for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:  # Outline positions
                text_rect = outline_text.get_rect(center=(100+dx, 100+dy))
                surf.blit(outline_text, text_rect)
            # Draw main text
            text = font.render(str(4-i), True, (255, 255, 255))
            text_rect = text.get_rect(center=(100, 100))
            surf.blit(text, text_rect)
            sprites[f'countdown_{i}'] = surf
        
        # Create "GO!" text with outline
        go_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
        # Draw outline
        outline_text = font.render("GO!", True, (0, 0, 0))
        for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
            text_rect = outline_text.get_rect(center=(100+dx, 100+dy))
            go_surf.blit(outline_text, text_rect)
        # Draw main text
        go_text = font.render("GO!", True, (255, 0, 0))  # Make GO! red for emphasis
        go_rect = go_text.get_rect(center=(100, 100))
        go_surf.blit(go_text, go_rect)
        sprites['go'] = go_surf
        
        # Load custom RPS sprites
        for game_name, file_name in sprite_names.items():
            sprite_file = os.path.join(sprite_path, f'{file_name}.png')
            try:
                if os.path.exists(sprite_file):
                    sprite = pygame.image.load(sprite_file).convert_alpha()
                    sprites[game_name] = pygame.transform.scale(sprite, (200, 200))
                else:
                    print(f"Sprite file not found: {sprite_file}")
                    raise FileNotFoundError
            except Exception as e:
                print(f"Creating fallback sprite for {game_name}: {e}")
                # Create more distinctive placeholder sprites
                temp_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
                colors = {
                    'rock': ((200, 100, 100), "✊"),
                    'paper': ((100, 200, 100), "✋"),
                    'scissors': ((100, 100, 200), "✌")
                }
                color, symbol = colors.get(game_name, ((200, 200, 200), "?"))
                # Draw filled circle background
                pygame.draw.circle(temp_surface, (*color, 200), (100, 100), 90)
                # Draw symbol
                symbol_font = pygame.font.Font(None, 120)
                symbol_text = symbol_font.render(symbol, True, (255, 255, 255))
                symbol_rect = symbol_text.get_rect(center=(100, 100))
                temp_surface.blit(symbol_text, symbol_rect)
                sprites[game_name] = temp_surface
        
        return sprites

    def draw_rps_game(self):
        # Setup fonts and positions
        font = pygame.font.Font(None, 48)
        small_font = pygame.font.Font(None, 36)
        right_half_center_x = self.WINDOW_WIDTH * 3 // 4
        center_y = self.WINDOW_HEIGHT // 2
        
        # Get current time and gesture
        current_time = pygame.time.get_ticks()
        gesture = get_current_gesture(self) or "none"  # Default to "none" if no gesture detected
        
        # If game is finished, show final result and return
        if self.game.game_finished:
            # Determine winner
            if self.game.player_score > self.game.computer_score:
                result = "You won the game!"
            elif self.game.computer_score > self.game.player_score:
                result = "Computer won the game!"
            else:
                result = "It's a tie game!"
            
            # Draw final result
            result_surface = font.render(result, True, (255, 255, 255))
            result_rect = result_surface.get_rect(center=(right_half_center_x, center_y))
            self.screen.blit(result_surface, result_rect)
            
            # Show return to menu instruction
            instruction = "Press ESC to return to menu"
            inst_surface = font.render(instruction, True, (255, 255, 255))
            inst_rect = inst_surface.get_rect(center=(right_half_center_x, center_y + 100))
            self.screen.blit(inst_surface, inst_rect)
            return

        # Initialize countdown if needed
        if self.countdown_timer is None:
            self.countdown_timer = current_time
            self.countdown = 3
            self.last_gesture = None
        
        # Calculate time elapsed since last countdown update
        elapsed = current_time - self.countdown_timer
        
        # Update countdown every second
        if elapsed >= 1000:
            self.countdown_timer = current_time
            if self.countdown > 0:
                self.countdown -= 1
        
        # Display appropriate game phase
        if self.countdown > 0:
            # Phase 1: Countdown (3,2,1)
            sprite = self.rps_sprites[f'countdown_{self.countdown}']
            self.screen.blit(sprite, sprite.get_rect(center=(right_half_center_x, center_y)))
        
        elif elapsed < 1000:
            # Phase 2: GO!
            sprite = self.rps_sprites['go']
            self.screen.blit(sprite, sprite.get_rect(center=(right_half_center_x, center_y)))
        
        else:
            # Phase 3: Gameplay
            # Handle player move if gesture changed
            if gesture in ["rock", "paper", "scissors"] and gesture != self.last_gesture:
                self.last_gesture = gesture
                self.last_move = gesture
                self.game.play(gesture)
                
                # Reset for next round if not game over
                if not self.game.game_finished:
                    self.countdown = 3
                    self.countdown_timer = current_time + 1000
            
            # Display last played moves if available
            if self.last_move and self.game.computer_choice:
                # Player move (left side)
                player_sprite = self.rps_sprites[self.last_move]
                self.screen.blit(player_sprite, player_sprite.get_rect(
                    center=(right_half_center_x - 200, center_y)))
                
                # Computer move (right side)
                comp_sprite = self.rps_sprites[self.game.computer_choice]
                self.screen.blit(comp_sprite, comp_sprite.get_rect(
                    center=(right_half_center_x + 200, center_y)))
                
                # Labels
                for side, text, x_offset in [
                    ("Your Move", self.last_move, -200),
                    ("Computer's Move", self.game.computer_choice, 200)
                ]:
                    # Draw label above
                    label = small_font.render(side, True, (255, 255, 255))
                    self.screen.blit(label, label.get_rect(
                        center=(right_half_center_x + x_offset, center_y - 120)))
                    
                    # Draw move name below
                    move_text = small_font.render(text.capitalize(), True, (255, 255, 255))
                    self.screen.blit(move_text, move_text.get_rect(
                        center=(right_half_center_x + x_offset, center_y + 120)))

        # Always show current gesture preview at bottom
        if gesture in ["rock", "paper", "scissors"]:
            # Preview sprite
            current_sprite = self.rps_sprites[gesture]
            self.screen.blit(current_sprite, current_sprite.get_rect(
                center=(right_half_center_x, self.WINDOW_HEIGHT - 150)))
            
            # Preview label
            preview_text = f"Current gesture: {gesture.capitalize()}"
            preview_surface = small_font.render(preview_text, True, (255, 255, 255))
            self.screen.blit(preview_surface, preview_surface.get_rect(
                center=(right_half_center_x, self.WINDOW_HEIGHT - 50)))
        
        # Draw round result if available
        if self.game.last_result:
            result_surface = font.render(self.game.last_result, True, (255, 255, 255))
            self.screen.blit(result_surface, result_surface.get_rect(
                center=(right_half_center_x, self.WINDOW_HEIGHT - 100)))
    
    def cleanup(self):
        if self.cap:
            self.cap.release()
        if hasattr(self, 'hand_model'):
            self.hand_model.close()
            
    def reset_rps_round(self):
        """Reset the state for a new RPS round"""
        self.countdown = 3
        self.countdown_timer = pygame.time.get_ticks()
        self.last_move = None
        self.waiting_for_move = False
        self.move_locked = False
        self.round_end_timer = None

class MainMenu:
    # Class variable to store the current background
    current_background = None
    
    def __init__(self):
        pygame.init() # full width of the screen
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Game Agent")
        
        self.sprite_manager = SpriteManager()  # Initialize the sprite manager
        self.game_select = None
        
        # Load a random nature background
        self.background = self.load_random_background()
        # Store a global reference to the background
        MainMenu.current_background = self.background
        
        # Initialize hand tracking
        setup_hand_tracking(self)
        
        # Initialize background grid
        self.grid_size = 40
        self.grid = self.create_background_grid()
        self.particles = []
        
        # Animation variables
        self.animation_timer = 0
        self.hover_animations = {}
        
        # Colors
        self.BLUE = (41, 128, 185)
        self.DARK_BLUE = (0, 100, 200)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (150, 150, 150)
        self.ACCENT = (52, 152, 219)
        self.BACKGROUND = (44, 62, 80)
        
        # Pixelated font
        self.font_size = 128
        self.button_font_size = 36
        self.font = pygame.font.Font(None, self.font_size)
        self.button_font = pygame.font.Font(None, self.button_font_size)
        
        # Button dimensions
        self.button_width = 450
        self.button_height = 100
        self.button_spacing = 50
        
        # Button positions
        button_start_y = self.WINDOW_HEIGHT // 2
        self.buttons = [
            {
                'text': 'Play',
                'rect': pygame.Rect(
                    (self.WINDOW_WIDTH - self.button_width) // 2,
                    button_start_y,
                    self.button_width,
                    self.button_height
                )
            },
            {
                'text': 'Rules',
                'rect': pygame.Rect(
                    (self.WINDOW_WIDTH - self.button_width) // 2,
                    button_start_y + self.button_height + self.button_spacing,
                    self.button_width,
                    self.button_height
                )
            },
            {
                'text': 'Credits',
                'rect': pygame.Rect(
                    (self.WINDOW_WIDTH - self.button_width) // 2,
                    button_start_y + (self.button_height + self.button_spacing) * 2,
                    self.button_width,
                    self.button_height
                )
            }
        ]

    

    def create_background_grid(self):
        grid = []
        for y in range(0, self.WINDOW_HEIGHT + self.grid_size, self.grid_size):
            row = []
            for x in range(0, self.WINDOW_WIDTH + self.grid_size, self.grid_size):
                brightness = random.randint(30, 50)
                color = (brightness, brightness + 10, brightness + 20)
                row.append(color)
            grid.append(row)
        return grid

    def update_particles(self):
        # Add new particles occasionally
        if random.random() < 0.1:
            self.particles.append(Particle(
                random.randint(0, self.WINDOW_WIDTH),
                random.randint(0, self.WINDOW_HEIGHT)
            ))
        
        # Update existing particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()

    def draw_background(self):
        self.animation_timer += 0.01
        for y, row in enumerate(self.grid):
            for x, color in enumerate(row):
                offset = math.sin(self.animation_timer + x * 0.1 + y * 0.1) * 2
                rect = pygame.Rect(
                    x * self.grid_size,
                    y * self.grid_size + offset,
                    self.grid_size - 1,
                    self.grid_size - 1
                )
                pygame.draw.rect(self.screen, color, rect)

    def draw_pixelated_rect(self, surface, color, rect, border_radius=10):
        # Create a slightly darker version of the color for the border
        border_color = tuple(max(0, c - 30) for c in color)
        
        # Draw the main rectangle
        pygame.draw.rect(surface, color, rect, border_radius=border_radius)
        
        # Draw a pixel border
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=border_radius)
        
        # Add some pixel details
        pixel_size = 3
        for x in range(rect.left + pixel_size, rect.right - pixel_size, pixel_size * 2):
            for y in range(rect.top + pixel_size, rect.bottom - pixel_size, pixel_size * 2):
                if random.random() < 0.1:  # Only draw some pixels
                    lighter_color = tuple(min(255, c + 20) for c in color)
                    pygame.draw.rect(surface, lighter_color, 
                                  (x, y, pixel_size, pixel_size))
        
    def draw_mascot(self, x, y):
        # Head
        pygame.draw.rect(self.screen, self.BLUE, (x, y, 60, 60))
        
        # Glasses frame
        pygame.draw.rect(self.screen, self.BLACK, (x + 10, y + 20, 40, 15))
        
        # Glasses lenses
        pygame.draw.rect(self.screen, self.WHITE, (x + 12, y + 22, 16, 11))
        pygame.draw.rect(self.screen, self.WHITE, (x + 32, y + 22, 16, 11))
        
        # Suit
        pygame.draw.rect(self.screen, self.BLACK, (x + 10, y + 60, 40, 30))
        
        # Tie
        pygame.draw.rect(self.screen, self.BLUE, (x + 25, y + 60, 10, 20))

    def draw_button(self, button, hover=False):
        color = self.DARK_BLUE if hover else self.BLUE
        self.draw_pixelated_rect(self.screen, color, button['rect'])
        
        text_surface = self.button_font.render(button['text'], True, self.WHITE)
        text_rect = text_surface.get_rect(center=button['rect'].center)
        self.screen.blit(text_surface, text_rect)

    def draw_main_menu(self, mouse_pos):  # Add mouse_pos parameter
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BACKGROUND)
            self.draw_background()
        
        # Get current gesture for visual feedback
        gesture = get_current_gesture(self)
        
        # Draw floating particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Create overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.fill(self.BACKGROUND)
        overlay.set_alpha(100)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title with shadow
        shadow_offset = 5
        title_shadow = self.font.render("Game Agent", True, self.BLACK)
        title_text = self.font.render("Game Agent", True, self.WHITE)
        
        title_rect = title_text.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        shadow_rect = title_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_text, title_rect)
        
        # Draw mascot
        self.draw_mascot(self.WINDOW_WIDTH // 2 - 30, 150)
        
        # Draw buttons
        for button in self.buttons:
            hover = button['rect'].collidepoint(mouse_pos)  # Use passed mouse_pos instead
            self.draw_button(button, hover)
            
            if hover and random.random() < 0.1:
                self.particles.append(Particle(
                    random.randint(button['rect'].left, button['rect'].right),
                    random.randint(button['rect'].top, button['rect'].bottom)
                ))

    def load_random_background(self):
        background_path = os.path.join(os.path.dirname(__file__), 'backgrounds', 'craftpix-net-823949-free-nature-backgrounds-pixel-art')
        nature_folders = [f for f in os.listdir(background_path) if f.startswith('nature_') and os.path.isdir(os.path.join(background_path, f))]
        
        if nature_folders:
            # Select random nature folder
            chosen_folder = random.choice(nature_folders)
            folder_path = os.path.join(background_path, chosen_folder)
            
            # Find the first PNG file in the folder
            background_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
            if background_files:
                bg_path = os.path.join(folder_path, background_files[0])
                background = pygame.image.load(bg_path)
                return pygame.transform.scale(background, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        
        # Return None if no background could be loaded
        return None

    def run(self):
        clock = pygame.time.Clock()
        current_screen = "main_menu"
        setup_hand_tracking(self)
        
        # Screen objects
        difficulty_select = None
        game_window = None
        
        while True:
            # Update hand tracking
            update_hand_tracking(self)
            hand_pos = get_hand_position(self)
            mouse_pos = hand_pos if hand_pos else pygame.mouse.get_pos()
            
            # Check for o_sign gesture and handle button interactions
            gesture = get_current_gesture(self)
            hand_pos = get_hand_position(self)
            
            if hand_pos and gesture == "o_sign":
                # Check if hand is over any button
                if current_screen == "main_menu":
                    for button in self.buttons:
                        if button['rect'].collidepoint(hand_pos):
                            if is_hand_click(self):
                                # Add particles on click
                                for _ in range(20):
                                    self.particles.append(Particle(
                                        button['rect'].centerx,
                                        button['rect'].centery
                                    ))
                                # Execute button action
                                if button['text'] == 'Play':
                                    self.game_select = GameSelect(self.screen, self.sprite_manager)
                                    current_screen = "game_select"
                                elif button['text'] == 'Rules':
                                    print("Rules clicked")
                                elif button['text'] == 'Credits':
                                    print("Credits clicked")
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if game_window:
                        game_window.cleanup()
                    cleanup_hand_tracking(self)
                    pygame.quit()
                    sys.exit()
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if current_screen == "main_menu":
                        for button in self.buttons:
                            if button['rect'].collidepoint(mouse_pos):
                                # Add particles on click
                                for _ in range(20):
                                    self.particles.append(Particle(
                                        button['rect'].centerx,
                                        button['rect'].centery
                                    ))
                                # Handle button clicks here
                                if button['text'] == 'Play':
                                    self.game_select = GameSelect(self.screen, self.sprite_manager)
                                    current_screen = "game_select"
                                elif button['text'] == 'Rules':
                                    print("Rules clicked")
                                elif button['text'] == 'Credits':
                                    print("Credits clicked")
                    
                    elif current_screen == "game_select":
                        game_choice = self.game_select.handle_click(mouse_pos)
                        if game_choice:
                            difficulty_select = DifficultySelect(self.screen, game_choice)
                            current_screen = "difficulty_select"
                            self.game_select = None
                    
                    elif current_screen == "difficulty_select":
                        result = difficulty_select.handle_click(mouse_pos)
                        if result:
                            game_type, difficulty = result
                            game_window = GameWindow(self.screen, game_type, difficulty)
                            current_screen = "game"
                            difficulty_select = None
                    
                    elif current_screen == "game":
                        if game_window.game_type == "TTT":
                            # Convert mouse position to board coordinates
                            board_x = mouse_pos[0] - (self.WINDOW_WIDTH // 2)
                            cell_size = 150
                            if board_x >= 0:  # Only handle clicks on the right side
                                col = board_x // cell_size
                                row = mouse_pos[1] // cell_size
                                if 0 <= row < 3 and 0 <= col < 3:
                                    if game_window.board.mark_square('O', row, col):
                                        # AI move based on difficulty
                                        if not game_window.board.game_over:
                                            from ttai import call_tt, easy_tt_random, medium_tt
                                            if game_window.difficulty == 'easy':
                                                ai_move = easy_tt_random(game_window.board.board)
                                            elif game_window.difficulty == 'medium':
                                                ai_move = medium_tt(game_window.board.board)
                                            else:  # hard
                                                ai_move = call_tt(game_window.board.board)
                                            if ai_move:
                                                game_window.board.mark_square('X', ai_move[0], ai_move[1])
                        
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if current_screen == "game":
                        if game_window:
                            game_window.cleanup()
                        game_window = None
                        current_screen = "main_menu"
                    elif current_screen in ["difficulty_select", "game_select"]:
                        current_screen = "main_menu"
                        difficulty_select = None
                        self.game_select = None
            
            # Update particles
            self.update_particles()
            
            # Clear screen
            self.screen.fill(self.BACKGROUND)
            
            # Draw current screen
            if current_screen == "main_menu":
                self.draw_main_menu(mouse_pos)
            elif current_screen == "game_select":
                self.game_select.draw()
            elif current_screen == "difficulty_select":
                difficulty_select.draw()
            elif current_screen == "game":
                game_window.draw()

            draw_hand_indicator(self)
            
            pygame.display.flip()
            clock.tick(60)



            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                cleanup_hand_tracking(self)
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()


# Escape function
# Break function if esc key pressed

