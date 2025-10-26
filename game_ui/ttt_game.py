# ttt_game.py - Tic Tac Toe game window
import pygame
import cv2
import mediapipe as mp
from Board import Board
from ttai import call_tt, easy_tt_random, medium_tt

class TicTacToeGame:
    def __init__(self, screen, difficulty):
        self.screen = screen
        self.difficulty = difficulty
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Initialize board
        self.board = Board()
        
        # Game state
        self.last_o_gesture_time = 0
        self.o_gesture_cooldown = 800
        self.ai_move_delay = 500
        self.ai_move_scheduled = None
        self.pending_ai_move = None
        self.current_hover = None
        self.winner_line = None
        self.game_over_time = None
        
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
        
        # Colors
        self.COLOR_BG = (15, 23, 42)
        self.COLOR_DIVIDER = (71, 85, 105)
        self.COLOR_BOARD_BG = (30, 41, 59)
        self.COLOR_GRID = (99, 102, 241)
        self.COLOR_X = (239, 68, 68)
        self.COLOR_O = (59, 130, 246)
        self.COLOR_TEXT = (241, 245, 249)
        self.COLOR_TEXT_DIM = (148, 163, 184)
        self.COLOR_WIN = (34, 197, 94)
        self.COLOR_TIE = (251, 191, 36)
        self.COLOR_HOVER = (99, 102, 241, 60)
        
        # Board dimensions
        self.cell_size = 140
        self.board_width = self.cell_size * 3
        self.board_height = self.cell_size * 3
        self.board_x = self.WINDOW_WIDTH // 2 + (self.WINDOW_WIDTH // 4 - self.board_width // 2)
        self.board_y = (self.WINDOW_HEIGHT - self.board_height) // 2
        
        # Import gesture detection
        from gestures import get_hand_landmarks, o_sign
        self.get_hand_landmarks = get_hand_landmarks
        self.o_sign = o_sign
    
    def is_board_full(self):
        """Check if board is full (tie game)"""
        for row in self.board.board:
            for cell in row:
                if cell == ' ':
                    return False
        return True
    
    def get_cell_from_position(self, finger_x, finger_y):
        """Convert normalized finger position to board cell"""
        row = int(finger_y * 3)
        col = int(finger_x * 3)
        if 0 <= row < 3 and 0 <= col < 3:
            return row, col
        return None, None
    
    def get_winning_line(self):
        """Check for winning line and return coordinates"""
        board = self.board.board
        
        # Check rows
        for row in range(3):
            if board[row][0] == board[row][1] == board[row][2] != ' ':
                return [(row, 0), (row, 2)]
        
        # Check columns
        for col in range(3):
            if board[0][col] == board[1][col] == board[2][col] != ' ':
                return [(0, col), (2, col)]
        
        # Check diagonals
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return [(0, 0), (2, 2)]
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return [(0, 2), (2, 0)]
        
        return None
    
    def schedule_ai_move(self):
        """Schedule AI move with delay"""
        if self.difficulty == 'easy':
            ai_move = easy_tt_random(self.board.board)
        elif self.difficulty == 'medium':
            ai_move = medium_tt(self.board.board)
        else:
            ai_move = call_tt(self.board.board)
        
        if ai_move:
            self.pending_ai_move = ai_move
            self.ai_move_scheduled = pygame.time.get_ticks()
    
    def execute_ai_move(self):
        """Execute the pending AI move"""
        if self.pending_ai_move:
            self.board.mark_square('X', self.pending_ai_move[0], self.pending_ai_move[1])
            self.pending_ai_move = None
            self.ai_move_scheduled = None
            
            # Check if game ended
            winner = self.board.win_check()
            if winner or self.is_board_full():
                self.board.game_over = True
                self.winner_line = self.get_winning_line()
                self.game_over_time = pygame.time.get_ticks()
    
    def reset_game(self):
        """Reset the game for a new round"""
        self.board = Board()
        self.winner_line = None
        self.game_over_time = None
        self.pending_ai_move = None
        self.ai_move_scheduled = None
        self.current_hover = None
        self.last_o_gesture_time = 0
    
    def draw(self):
        self.screen.fill(self.COLOR_BG)
        
        # Check if AI move should be executed
        if self.ai_move_scheduled:
            current_time = pygame.time.get_ticks()
            if current_time - self.ai_move_scheduled >= self.ai_move_delay:
                self.execute_ai_move()
        
        # Draw camera feed and detect gestures
        detected_cell = None
        is_gesture_active = False
        
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
                        self.drawer.draw_landmarks(
                            frame_square, 
                            hand, 
                            mp.solutions.hands.HAND_CONNECTIONS,
                            self.drawer.DrawingSpec(color=(99, 102, 241), thickness=2, circle_radius=4),
                            self.drawer.DrawingSpec(color=(241, 245, 249), thickness=2)
                        )
                        
                        landmarks = self.get_hand_landmarks(hand)
                        is_o_sign, fingertip_x, fingertip_y = self.o_sign(landmarks)
                        
                        if is_o_sign:
                            is_gesture_active = True
                            row, col = self.get_cell_from_position(fingertip_x, fingertip_y)
                            
                            if row is not None and col is not None:
                                detected_cell = (row, col)
                                self.current_hover = detected_cell
                                
                                if (self.board.board[row][col] == ' ' and 
                                    not self.board.game_over and 
                                    not self.ai_move_scheduled):
                                    
                                    current_time = pygame.time.get_ticks()
                                    if current_time - self.last_o_gesture_time > self.o_gesture_cooldown:
                                        if self.board.mark_square('O', row, col):
                                            self.last_o_gesture_time = current_time
                                            
                                            # Check if game ended with player's move
                                            winner = self.board.win_check()
                                            if winner or self.is_board_full():
                                                self.board.game_over = True
                                                self.winner_line = self.get_winning_line()
                                                self.game_over_time = current_time
                                            else:
                                                self.schedule_ai_move()
                            
                            # Draw crosshair on camera
                            center_x = int(fingertip_x * size)
                            center_y = int(fingertip_y * size)
                            cv2.circle(frame_square, (center_x, center_y), 15, (59, 130, 246), 3)
                            cv2.circle(frame_square, (center_x, center_y), 3, (59, 130, 246), -1)
                            cv2.line(frame_square, (center_x - 25, center_y), (center_x - 10, center_y), (59, 130, 246), 2)
                            cv2.line(frame_square, (center_x + 10, center_y), (center_x + 25, center_y), (59, 130, 246), 2)
                            cv2.line(frame_square, (center_x, center_y - 25), (center_x, center_y - 10), (59, 130, 246), 2)
                            cv2.line(frame_square, (center_x, center_y + 10), (center_x, center_y + 25), (59, 130, 246), 2)
                
                if not is_gesture_active:
                    self.current_hover = None
                
                # Display camera
                frame_surface = pygame.surfarray.make_surface(
                    cv2.cvtColor(frame_square, cv2.COLOR_BGR2RGB).swapaxes(0,1)
                )
                scaled_frame = pygame.transform.scale(
                    frame_surface, 
                    (self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT)
                )
                self.screen.blit(scaled_frame, (0, 0))
        
        # Draw dividing line
        line_x = self.WINDOW_WIDTH // 2
        pygame.draw.line(self.screen, self.COLOR_DIVIDER, (line_x, 0), (line_x, self.WINDOW_HEIGHT), 4)
        
        self.draw_game_board()
    
    def draw_game_board(self):
        right_center_x = self.WINDOW_WIDTH * 3 // 4
        
        # Draw title
        title_font = pygame.font.Font(None, 56)
        title_text = title_font.render("Tic Tac Toe", True, self.COLOR_TEXT)
        self.screen.blit(title_text, title_text.get_rect(center=(right_center_x, 50)))
        
        # Difficulty badge
        diff_font = pygame.font.Font(None, 28)
        diff_text = diff_font.render(self.difficulty.upper(), True, self.COLOR_GRID)
        diff_bg = pygame.Surface((diff_text.get_width() + 24, 32), pygame.SRCALPHA)
        pygame.draw.rect(diff_bg, (*self.COLOR_GRID, 40), diff_bg.get_rect(), border_radius=8)
        pygame.draw.rect(diff_bg, self.COLOR_GRID, diff_bg.get_rect(), 2, border_radius=8)
        diff_bg.blit(diff_text, (12, 6))
        self.screen.blit(diff_bg, (right_center_x - diff_bg.get_width() // 2, 90))
        
        # Draw player indicators
        self.draw_player_indicators(right_center_x)
        
        # Draw board background
        pygame.draw.rect(self.screen, self.COLOR_BOARD_BG,
                        (self.board_x, self.board_y, self.board_width, self.board_height), 
                        border_radius=15)
        
        # Draw hover highlight
        if self.current_hover and not self.board.game_over and not self.ai_move_scheduled:
            row, col = self.current_hover
            if self.board.board[row][col] == ' ':
                hover_x = self.board_x + col * self.cell_size
                hover_y = self.board_y + row * self.cell_size
                hover_surf = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                pygame.draw.rect(hover_surf, self.COLOR_HOVER, hover_surf.get_rect())
                self.screen.blit(hover_surf, (hover_x, hover_y))
        
        # Draw border
        pygame.draw.rect(self.screen, self.COLOR_GRID,
                        (self.board_x, self.board_y, self.board_width, self.board_height), 
                        3, border_radius=15)
        
        # Draw grid lines
        for i in range(1, 3):
            # Vertical
            x = self.board_x + i * self.cell_size
            pygame.draw.line(self.screen, self.COLOR_GRID,
                           (x, self.board_y + 8),
                           (x, self.board_y + self.board_height - 8), 3)
            # Horizontal
            y = self.board_y + i * self.cell_size
            pygame.draw.line(self.screen, self.COLOR_GRID,
                           (self.board_x + 8, y),
                           (self.board_x + self.board_width - 8, y), 3)
        
        # Draw X's and O's
        for row in range(3):
            for col in range(3):
                cell_x = self.board_x + col * self.cell_size
                cell_y = self.board_y + row * self.cell_size
                center_x = cell_x + self.cell_size // 2
                center_y = cell_y + self.cell_size // 2
                
                if self.board.board[row][col] == 'X':
                    padding = 30
                    pygame.draw.line(self.screen, self.COLOR_X,
                                   (cell_x + padding, cell_y + padding),
                                   (cell_x + self.cell_size - padding, cell_y + self.cell_size - padding), 6)
                    pygame.draw.line(self.screen, self.COLOR_X,
                                   (cell_x + self.cell_size - padding, cell_y + padding),
                                   (cell_x + padding, cell_y + self.cell_size - padding), 6)
                
                elif self.board.board[row][col] == 'O':
                    radius = self.cell_size // 2 - 30
                    pygame.draw.circle(self.screen, self.COLOR_O,
                                     (center_x, center_y), radius, 6)
        
        # Draw winning line
        if self.winner_line and self.game_over_time:
            current_time = pygame.time.get_ticks()
            anim_progress = min(1.0, (current_time - self.game_over_time) / 400)
            
            start_row, start_col = self.winner_line[0]
            end_row, end_col = self.winner_line[1]
            
            start_x = self.board_x + start_col * self.cell_size + self.cell_size // 2
            start_y = self.board_y + start_row * self.cell_size + self.cell_size // 2
            end_x = self.board_x + end_col * self.cell_size + self.cell_size // 2
            end_y = self.board_y + end_row * self.cell_size + self.cell_size // 2
            
            current_end_x = start_x + (end_x - start_x) * anim_progress
            current_end_y = start_y + (end_y - start_y) * anim_progress
            
            pygame.draw.line(self.screen, self.COLOR_WIN,
                           (start_x, start_y), (current_end_x, current_end_y), 8)
        
        # Status
        self.draw_status(right_center_x)
    
    def draw_player_indicators(self, center_x):
        """Draw who's playing X and O"""
        indicator_y = 150
        
        # Player (O)
        player_surf = pygame.Surface((160, 50), pygame.SRCALPHA)
        is_player_turn = not self.board.game_over and not self.ai_move_scheduled
        
        if is_player_turn:
            pygame.draw.rect(player_surf, (*self.COLOR_O, 40), player_surf.get_rect(), border_radius=8)
            pygame.draw.rect(player_surf, self.COLOR_O, player_surf.get_rect(), 2, border_radius=8)
            o_color = self.COLOR_O
        else:
            pygame.draw.rect(player_surf, (*self.COLOR_TEXT_DIM, 20), player_surf.get_rect(), border_radius=8)
            o_color = self.COLOR_TEXT_DIM
        
        pygame.draw.circle(player_surf, o_color, (25, 25), 12, 3)
        font = pygame.font.Font(None, 28)
        text = font.render("YOU", True, o_color)
        player_surf.blit(text, (50, 17))
        
        self.screen.blit(player_surf, (center_x - 180, indicator_y))
        
        # Computer (X)
        comp_surf = pygame.Surface((160, 50), pygame.SRCALPHA)
        is_ai_turn = not self.board.game_over and self.ai_move_scheduled
        
        if is_ai_turn:
            pygame.draw.rect(comp_surf, (*self.COLOR_X, 40), comp_surf.get_rect(), border_radius=8)
            pygame.draw.rect(comp_surf, self.COLOR_X, comp_surf.get_rect(), 2, border_radius=8)
            x_color = self.COLOR_X
        else:
            pygame.draw.rect(comp_surf, (*self.COLOR_TEXT_DIM, 20), comp_surf.get_rect(), border_radius=8)
            x_color = self.COLOR_TEXT_DIM
        
        pygame.draw.line(comp_surf, x_color, (15, 15), (35, 35), 3)
        pygame.draw.line(comp_surf, x_color, (35, 15), (15, 35), 3)
        text = font.render("CPU", True, x_color)
        comp_surf.blit(text, (50, 17))
        
        self.screen.blit(comp_surf, (center_x + 20, indicator_y))
    
    def draw_status(self, center_x):
        """Draw status text and instructions"""
        status_y = self.board_y + self.board_height + 50
        
        font = pygame.font.Font(None, 44)
        inst_font = pygame.font.Font(None, 28)
        
        if self.board.game_over:
            winner = self.board.win_check()
            if winner == 'O':
                status_text = "You Win!"
                status_color = self.COLOR_WIN
            elif winner == 'X':
                status_text = "Computer Wins"
                status_color = self.COLOR_X
            else:
                status_text = "It's a Tie!"
                status_color = self.COLOR_TIE
            
            text = font.render(status_text, True, status_color)
            self.screen.blit(text, text.get_rect(center=(center_x, status_y)))
            
            # Play again button
            button_text = inst_font.render("Press R to Play Again", True, self.COLOR_TEXT)
            self.screen.blit(button_text, button_text.get_rect(center=(center_x, status_y + 50)))
            
            # ESC instruction
            esc_text = inst_font.render("Press ESC to return to menu", True, self.COLOR_TEXT_DIM)
            self.screen.blit(esc_text, esc_text.get_rect(center=(center_x, status_y + 85)))
            
        else:
            if self.ai_move_scheduled:
                status_text = "Computer is thinking..."
                status_color = self.COLOR_X
            else:
                status_text = "Your turn!"
                status_color = self.COLOR_O
            
            text = font.render(status_text, True, status_color)
            self.screen.blit(text, text.get_rect(center=(center_x, status_y)))
            
            # Instructions
            inst1 = inst_font.render("Make 'O' gesture and point at cell", True, self.COLOR_TEXT_DIM)
            self.screen.blit(inst1, inst1.get_rect(center=(center_x, status_y + 40)))
            
            inst2 = inst_font.render("Hold steady to place your mark", True, self.COLOR_TEXT_DIM)
            self.screen.blit(inst2, inst2.get_rect(center=(center_x, status_y + 70)))
            
            # ESC instruction
            esc_text = inst_font.render("Press ESC for menu", True, self.COLOR_TEXT_DIM)
            self.screen.blit(esc_text, esc_text.get_rect(center=(center_x, status_y + 105)))
    
    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if self.board.game_over:
                    self.reset_game()
    
    def handle_click(self, pos):
        """Handle mouse clicks on the board"""
        board_rel_x = pos[0] - self.board_x
        board_rel_y = pos[1] - self.board_y
        
        if 0 <= board_rel_x < self.board_width and 0 <= board_rel_y < self.board_height:
            col = board_rel_x // self.cell_size
            row = board_rel_y // self.cell_size
            
            if 0 <= row < 3 and 0 <= col < 3 and not self.board.game_over and not self.ai_move_scheduled:
                if self.board.mark_square('O', row, col):
                    winner = self.board.win_check()
                    if winner or self.is_board_full():
                        self.board.game_over = True
                        self.winner_line = self.get_winning_line()
                        self.game_over_time = pygame.time.get_ticks()
                    else:
                        self.schedule_ai_move()
    
    def cleanup(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        if hasattr(self, 'hand_model'):
            self.hand_model.close()