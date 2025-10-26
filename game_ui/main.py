# main.py - Main menu and game launcher
import pygame
import sys
import math
import random
import os

# Add necessary module paths
module_dir1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gesturedetectTT'))
module_dir2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'gemini_enemy'))

sys.path.insert(0, module_dir1)
sys.path.insert(0, module_dir2)

from gestures_ui import (cleanup_hand_tracking, get_current_gesture, 
                      get_hand_position, setup_hand_tracking, 
                      update_hand_tracking, draw_hand_indicator)

# Import game windows
from ttt_game import TicTacToeGame
from rps_game import RockPaperScissorsGame
from game_select import GameSelect
from difficulty_select import DifficultySelect
from rules import RulesPage
from credits import CreditsPage

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

class MainMenu:
    current_background = None

    def add_shadow(self, text, x, y):
        shadow_offset = 5
        title_shadow = self.font.render(text, True, self.BLACK)
        title_text = self.font.render(text, True, self.WHITE)

        title_rect = title_text.get_rect(center=(x, y))
        shadow_rect = title_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset
        
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_text, title_rect)
    
    def __init__(self):
        pygame.init()
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Gesture Games")
        
        # Load background
        self.background = self.load_random_background()
        MainMenu.current_background = self.background
        
        # Initialize hand tracking
        setup_hand_tracking(self)
        
        # Background grid
        self.grid_size = 40
        self.grid = self.create_background_grid()
        self.particles = []
        
        # Animation
        self.animation_timer = 0
        
        # Colors
        self.BLUE = (41, 128, 185)
        self.DARK_BLUE = (0, 100, 200)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BACKGROUND = (44, 62, 80)
        
        # Fonts
        self.font_size = 128
        self.button_font_size = 75
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
        
        # Click detection
        self.last_click_time = 0
        self.click_cooldown = 500

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
        if random.random() < 0.1:
            self.particles.append(Particle(
                random.randint(0, self.WINDOW_WIDTH),
                random.randint(0, self.WINDOW_HEIGHT)
            ))
        
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
        border_color = tuple(max(0, c - 30) for c in color)
        pygame.draw.rect(surface, color, rect, border_radius=border_radius)
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=border_radius)
        
        pixel_size = 3
        for x in range(rect.left + pixel_size, rect.right - pixel_size, pixel_size * 2):
            for y in range(rect.top + pixel_size, rect.bottom - pixel_size, pixel_size * 2):
                if random.random() < 0.1:
                    lighter_color = tuple(min(255, c + 20) for c in color)
                    pygame.draw.rect(surface, lighter_color, 
                                  (x, y, pixel_size, pixel_size))
        
    def draw_mascot(self, x, y):
        pygame.draw.rect(self.screen, self.BLUE, (x, y, 60, 60))
        pygame.draw.rect(self.screen, self.BLACK, (x + 10, y + 20, 40, 15))
        pygame.draw.rect(self.screen, self.WHITE, (x + 12, y + 22, 16, 11))
        pygame.draw.rect(self.screen, self.WHITE, (x + 32, y + 22, 16, 11))
        pygame.draw.rect(self.screen, self.BLACK, (x + 10, y + 60, 40, 30))
        pygame.draw.rect(self.screen, self.BLUE, (x + 25, y + 60, 10, 20))

    def draw_button(self, button, hover=False):
        color = self.DARK_BLUE if hover else self.BLUE
        self.draw_pixelated_rect(self.screen, color, button['rect'])

        shadow_text = self.button_font.render(button['text'], True, self.BLACK)
        text_surface = self.button_font.render(button['text'], True, self.WHITE)
        shadow_rect = shadow_text.get_rect(center=(button['rect'].centerx + 4, button['rect'].centery + 4))
        text_rect = text_surface.get_rect(center=button['rect'].center)
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(text_surface, text_rect)

    def draw_main_menu(self, mouse_pos):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.BACKGROUND)
            self.draw_background()
        
        for particle in self.particles:
            particle.draw(self.screen)
        
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.fill(self.BACKGROUND)
        overlay.set_alpha(100)
        self.screen.blit(overlay, (0, 0))
        
        # Title with shadow
        self.add_shadow("Gesture Games", self.WINDOW_WIDTH // 2, 100)
        
        self.draw_mascot(self.WINDOW_WIDTH // 2 - 30, 150)
        
        # Draw buttons
        for button in self.buttons:
            hover = button['rect'].collidepoint(mouse_pos)
            self.draw_button(button, hover)
            
            if hover and random.random() < 0.1:
                self.particles.append(Particle(
                    random.randint(button['rect'].left, button['rect'].right),
                    random.randint(button['rect'].top, button['rect'].bottom)
                ))

    def load_random_background(self):
        background_path = os.path.join(os.path.dirname(__file__), 'backgrounds', 
                                      'craftpix-net-823949-free-nature-backgrounds-pixel-art')
        
        if os.path.exists(background_path):
            nature_folders = [f for f in os.listdir(background_path) 
                            if f.startswith('nature_') and 
                            os.path.isdir(os.path.join(background_path, f))]
            
            if nature_folders:
                chosen_folder = random.choice(nature_folders)
                folder_path = os.path.join(background_path, chosen_folder)
                background_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
                
                if background_files:
                    bg_path = os.path.join(folder_path, background_files[0])
                    background = pygame.image.load(bg_path)
                    return pygame.transform.scale(background, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        
        return None

    def run(self):
        clock = pygame.time.Clock()
        current_screen = "main_menu"
        
        game_select = None
        difficulty_select = None
        game_window = None
        rules_page = None
        credits_page = None
        
        while True:
            update_hand_tracking(self)
            hand_pos = get_hand_position(self)
            mouse_pos = hand_pos if hand_pos else pygame.mouse.get_pos()
            
            # Handle gesture clicks
            gesture = get_current_gesture(self)
            current_time = pygame.time.get_ticks()
            
            if hand_pos and gesture == "o_sign":
                if current_time - self.last_click_time > self.click_cooldown:
                    if current_screen == "main_menu":
                        for button in self.buttons:
                            if button['rect'].collidepoint(hand_pos):
                                self.last_click_time = current_time
                                for _ in range(20):
                                    self.particles.append(Particle(
                                        button['rect'].centerx,
                                        button['rect'].centery
                                    ))
                                
                                if button['text'] == 'Play':
                                    game_select = GameSelect(self.screen)
                                    current_screen = "game_select"
                                elif button['text'] == 'Rules':
                                    rules_page = RulesPage(self.screen)
                                    current_screen = "rules"
                                elif button['text'] == 'Credits':
                                    credits_page = CreditsPage(self.screen)
                                    current_screen = "credits"
                                break
                    
                    elif current_screen == "rules":
                        if rules_page.handle_click(hand_pos):
                            current_screen = "main_menu"
                            rules_page = None
                    
                    elif current_screen == "credits":
                        if credits_page.handle_click(hand_pos):
                            current_screen = "main_menu"
                            credits_page = None
                    
                    elif current_screen == "game_select":
                        game_choice = game_select.handle_click(hand_pos)
                        if game_choice:
                            difficulty_select = DifficultySelect(self.screen, game_choice)
                            current_screen = "difficulty_select"
                            game_select = None
                    
                    elif current_screen == "difficulty_select":
                        result = difficulty_select.handle_click(hand_pos)
                        if result:
                            game_type, difficulty = result
                            if game_type == "TTT":
                                game_window = TicTacToeGame(self.screen, difficulty)
                            else:
                                game_window = RockPaperScissorsGame(self.screen, difficulty)
                            current_screen = "game"
                            difficulty_select = None
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if game_window:
                        game_window.cleanup()
                    cleanup_hand_tracking(self)
                    pygame.quit()
                    sys.exit()
                
                # Handle game-specific events
                if event.type == pygame.USEREVENT and current_screen == "game" and game_window:
                    if hasattr(game_window, 'handle_event'):
                        game_window.handle_event(event)
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if current_time - self.last_click_time > self.click_cooldown:
                        if current_screen == "main_menu":
                            for button in self.buttons:
                                if button['rect'].collidepoint(mouse_pos):
                                    self.last_click_time = current_time
                                    for _ in range(20):
                                        self.particles.append(Particle(
                                            button['rect'].centerx,
                                            button['rect'].centery
                                        ))
                                    
                                    if button['text'] == 'Play':
                                        game_select = GameSelect(self.screen)
                                        current_screen = "game_select"
                                    elif button['text'] == 'Rules':
                                        rules_page = RulesPage(self.screen)
                                        current_screen = "rules"
                                    elif button['text'] == 'Credits':
                                        credits_page = CreditsPage(self.screen)
                                        current_screen = "credits"
                        
                        elif current_screen == "rules":
                            if rules_page.handle_click(mouse_pos):
                                current_screen = "main_menu"
                                rules_page = None
                        
                        elif current_screen == "credits":
                            if credits_page.handle_click(mouse_pos):
                                current_screen = "main_menu"
                                credits_page = None
                        
                        elif current_screen == "game_select":
                            game_choice = game_select.handle_click(mouse_pos)
                            if game_choice:
                                difficulty_select = DifficultySelect(self.screen, game_choice)
                                current_screen = "difficulty_select"
                                game_select = None
                        
                        elif current_screen == "difficulty_select":
                            result = difficulty_select.handle_click(mouse_pos)
                            if result:
                                game_type, difficulty = result
                                if game_type == "TTT":
                                    game_window = TicTacToeGame(self.screen, difficulty)
                                else:
                                    game_window = RockPaperScissorsGame(self.screen, difficulty)
                                current_screen = "game"
                                difficulty_select = None
                        
                        elif current_screen == "game" and game_window:
                            if hasattr(game_window, 'handle_click'):
                                game_window.handle_click(mouse_pos)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if current_screen == "game":
                            if game_window:
                                game_window.cleanup()
                                game_window = None
                            current_screen = "main_menu"
                            setup_hand_tracking(self)
                        elif current_screen == "main_menu":
                            exit()
                        elif current_screen in ["difficulty_select", "game_select", "rules", "credits"]:
                            current_screen = "main_menu"
                            difficulty_select = None
                            game_select = None
                            rules_page = None
                            credits_page = None
                    
                    # Pass other key events to game windows
                    if current_screen == "game" and game_window:
                        if hasattr(game_window, 'handle_event'):
                            game_window.handle_event(event)
            
            self.update_particles()
            self.screen.fill(self.BACKGROUND)
            
            if current_screen == "main_menu":
                self.draw_main_menu(mouse_pos)
            elif current_screen == "game_select":
                game_select.draw()
            elif current_screen == "difficulty_select":
                difficulty_select.draw()
            elif current_screen == "rules":
                rules_page.draw()
            elif current_screen == "credits":
                credits_page.draw()
            elif current_screen == "game":
                if game_window:
                    game_window.draw()

            draw_hand_indicator(self)
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()