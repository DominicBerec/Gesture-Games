# rules.py - Rules and instructions page
import pygame

class RulesPage:
    def __init__(self, screen):
        self.screen = screen
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Colors
        self.COLOR_BG = (15, 23, 42)
        self.COLOR_TEXT = (241, 245, 249)
        self.COLOR_TEXT_DIM = (148, 163, 184)
        self.COLOR_ACCENT = (99, 102, 241)
        self.COLOR_CARD_BG = (30, 41, 59)
        self.COLOR_HIGHLIGHT = (59, 130, 246)
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.heading_font = pygame.font.Font(None, 48)
        self.body_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 28)
        
        # Back button
        self.back_button = pygame.Rect(50, 50, 150, 60)
    
    def draw_card(self, x, y, width, height, title, lines):
        """Draw an info card with title and bullet points"""
        # Card background
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.COLOR_CARD_BG, card_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.COLOR_ACCENT, card_rect, 3, border_radius=15)
        
        # Title
        title_surface = self.heading_font.render(title, True, self.COLOR_ACCENT)
        self.screen.blit(title_surface, (x + 30, y + 20))
        
        # Content lines
        y_offset = y + 80
        for line in lines:
            # Bullet point
            pygame.draw.circle(self.screen, self.COLOR_HIGHLIGHT, (x + 40, y_offset + 12), 5)
            
            # Text
            text_surface = self.body_font.render(line, True, self.COLOR_TEXT)
            self.screen.blit(text_surface, (x + 60, y_offset))
            y_offset += 45
    
    def draw_gesture_guide(self, x, y):
        """Draw gesture examples"""
        card_width = 320
        card_height = 200
        spacing = 40
        
        gestures = [
            ("Rock", "Make a fist"),
            ("Paper", "Open hand flat"),
            ("Scissors", "Two fingers up"),
            ("O-Sign", "Connect thumb & index")
        ]
        
        for i, (name, desc) in enumerate(gestures):
            card_x = x + (i % 4) * (card_width + spacing)
            card_y = y
            
            # Card
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            pygame.draw.rect(self.screen, self.COLOR_CARD_BG, card_rect, border_radius=12)
            pygame.draw.rect(self.screen, self.COLOR_HIGHLIGHT, card_rect, 2, border_radius=12)
            
            # Placeholder for gesture icon (large circle)
            center_x = card_x + card_width // 2
            center_y = card_y + 70
            pygame.draw.circle(self.screen, self.COLOR_ACCENT, (center_x, center_y), 40, 3)
            
            # Name
            name_surface = self.heading_font.render(name, True, self.COLOR_ACCENT)
            name_rect = name_surface.get_rect(center=(center_x, card_y + 135))
            self.screen.blit(name_surface, name_rect)
            
            # Description
            desc_surface = self.small_font.render(desc, True, self.COLOR_TEXT_DIM)
            desc_rect = desc_surface.get_rect(center=(center_x, card_y + 170))
            self.screen.blit(desc_surface, desc_rect)
    
    def draw(self):
        self.screen.fill(self.COLOR_BG)
        
        # Title
        title = self.title_font.render("How to Play", True, self.COLOR_TEXT)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Back button
        pygame.draw.rect(self.screen, self.COLOR_CARD_BG, self.back_button, border_radius=10)
        pygame.draw.rect(self.screen, self.COLOR_ACCENT, self.back_button, 2, border_radius=10)
        back_text = self.body_font.render("Back", True, self.COLOR_TEXT)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Calculate centered positions
        content_width = self.WINDOW_WIDTH - 160
        card_width = (content_width - 40) // 2
        left_x = 80
        right_x = left_x + card_width + 40
        
        # Main content area
        content_y = 160
        
        # Game Overview Card
        overview_lines = [
            "Play Tic Tac Toe or Rock Paper Scissors",
            "Use hand gestures detected by camera",
            "Compete against AI difficulty levels",
            "Choose Easy, Medium, or Hard mode"
        ]
        self.draw_card(left_x, content_y, card_width, 280, "Overview", overview_lines)
        
        # Controls Card
        controls_lines = [
            "Use O-Sign to select menu items",
            "Point at cells to place O in Tic Tac Toe",
            "Show gesture during countdown",
            "Press ESC to return to menu"
        ]
        self.draw_card(right_x, content_y, card_width, 280, "Controls", controls_lines)
        
        # Gesture Guide Section
        gesture_y = content_y + 320
        gesture_title = self.heading_font.render("Hand Gestures", True, self.COLOR_ACCENT)
        gesture_title_rect = gesture_title.get_rect(center=(self.WINDOW_WIDTH // 2, gesture_y))
        self.screen.blit(gesture_title, gesture_title_rect)
        
        # Calculate centered gesture cards
        gesture_cards_width = (320 * 4) + (40 * 3)
        gesture_start_x = (self.WINDOW_WIDTH - gesture_cards_width) // 2
        self.draw_gesture_guide(gesture_start_x, gesture_y + 60)
            
    def handle_click(self, pos):
        """Handle mouse/gesture clicks, return True if should go back"""
        if self.back_button.collidepoint(pos):
            return True
        return False