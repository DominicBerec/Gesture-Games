import pygame
import sys
import math
import random
import os
from pygame import gfxdraw

class SpriteManager:
    def __init__(self):
        self.sprites = {}
        self.load_sprites()
    
    def load_sprites(self):
        sprite_paths = {
            'ancient': 'sprites/9-Slice/Ancient',
            'colored': 'sprites/9-Slice/Colored',
            'outline': 'sprites/9-Slice/Outline'
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
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        
        # Box dimensions
        self.box_width = 300
        self.box_height = 400
        self.box_spacing = 50
        
        # Create game boxes
        center_y = self.WINDOW_HEIGHT // 2
        left_x = (self.WINDOW_WIDTH - (2 * self.box_width + self.box_spacing)) // 2
        
        self.rps_box = pygame.Rect(left_x, center_y - self.box_height//2,
                                 self.box_width, self.box_height)
        self.ttt_box = pygame.Rect(left_x + self.box_width + self.box_spacing,
                                 center_y - self.box_height//2,
                                 self.box_width, self.box_height)
        
        # Load game-specific sprites
        self.load_game_sprites()
        
    def load_game_sprites(self):
        # Scale factor for game sprites
        scale = 3
        size = (32 * scale, 32 * scale)
        
        # Create placeholder sprites for RPS
        self.rock_sprite = pygame.Surface(size)
        self.paper_sprite = pygame.Surface(size)
        self.scissors_sprite = pygame.Surface(size)
        self.rock_sprite.fill((100, 100, 100))
        self.paper_sprite.fill((200, 200, 200))
        self.scissors_sprite.fill((150, 150, 150))
        
        # Create TTT grid
        self.grid_sprite = pygame.Surface((200, 200))
        pygame.draw.line(self.grid_sprite, (255, 255, 255), (66, 0), (66, 200), 4)
        pygame.draw.line(self.grid_sprite, (255, 255, 255), (132, 0), (132, 200), 4)
        pygame.draw.line(self.grid_sprite, (255, 255, 255), (0, 66), (200, 66), 4)
        pygame.draw.line(self.grid_sprite, (255, 255, 255), (0, 132), (200, 132), 4)
    
    def draw_mischievous_agent(self, x, y):
        # Draw the agent with a mischievous pose
        scale = 2
        pygame.draw.rect(self.screen, (41, 128, 185), (x, y, 30*scale, 30*scale))  # Head
        # Glasses with a tilted angle for mischievous look
        pygame.draw.rect(self.screen, (0, 0, 0), (x + 5*scale, y + 10*scale, 20*scale, 7*scale))
        # Smirk
        pygame.draw.arc(self.screen, (0, 0, 0), 
                       (x + 5*scale, y + 15*scale, 20*scale, 10*scale), 
                       0, 3.14, 2)
    
    def draw(self):
        # Draw RPS box
        self.sprite_manager.draw_9slice(self.screen, 'ancient',
                                      self.rps_box.x, self.rps_box.y,
                                      self.rps_box.width, self.rps_box.height,
                                      scale=2)
        
        # Draw TTT box
        self.sprite_manager.draw_9slice(self.screen, 'ancient',
                                      self.ttt_box.x, self.ttt_box.y,
                                      self.ttt_box.width, self.ttt_box.height,
                                      scale=2)
        
        # Draw RPS content
        title_font = pygame.font.Font(None, 36)
        rps_title = title_font.render("Rock Paper Scissors", True, (255, 255, 255))
        self.screen.blit(rps_title, (self.rps_box.centerx - rps_title.get_width()//2,
                                    self.rps_box.y + 20))
        
        # Draw RPS sprites
        sprite_y = self.rps_box.y + 100
        spacing = 80
        self.screen.blit(self.rock_sprite, (self.rps_box.x + 30, sprite_y))
        self.screen.blit(self.paper_sprite, (self.rps_box.x + 120, sprite_y))
        self.screen.blit(self.scissors_sprite, (self.rps_box.x + 210, sprite_y))
        
        # Draw mischievous agent
        self.draw_mischievous_agent(self.rps_box.x + 120, sprite_y + 120)
        
        # Draw TTT content
        ttt_title = title_font.render("Tic Tac Toe", True, (255, 255, 255))
        self.screen.blit(ttt_title, (self.ttt_box.centerx - ttt_title.get_width()//2,
                                    self.ttt_box.y + 20))
        
        # Draw TTT grid
        grid_pos = (self.ttt_box.centerx - self.grid_sprite.get_width()//2,
                   self.ttt_box.centery - self.grid_sprite.get_height()//2)
        self.screen.blit(self.grid_sprite, grid_pos)
        
        # Draw some X's and O's
        font = pygame.font.Font(None, 72)
        positions = [(0, 0), (1, 1), (2, 2), (0, 2)]
        cell_size = 66
        
        for i, (x, y) in enumerate(positions):
            symbol = "X" if i % 2 == 0 else "O"
            text = font.render(symbol, True, (255, 255, 255))
            pos_x = grid_pos[0] + x * cell_size + cell_size//2 - text.get_width()//2
            pos_y = grid_pos[1] + y * cell_size + cell_size//2 - text.get_height()//2
            self.screen.blit(text, (pos_x, pos_y))
    
    def handle_click(self, pos):
        if self.rps_box.collidepoint(pos):
            return "RPS"
        elif self.ttt_box.collidepoint(pos):
            return "TTT"
        return None

class MainMenu:
    def __init__(self):
        pygame.init()
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Game Agent")
        self.sprite_manager = SpriteManager()  # Initialize the sprite manager
        self.game_select = None
        
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
        self.font_size = 64
        self.button_font_size = 36
        self.font = pygame.font.Font(None, self.font_size)
        self.button_font = pygame.font.Font(None, self.button_font_size)
        
        # Button dimensions
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20
        
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
                'text': 'Team',
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

    def draw_main_menu(self):
        # Draw background
        self.screen.fill(self.BACKGROUND)
        self.draw_background()
        
        # Draw floating particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Create overlay
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.fill(self.BACKGROUND)
        overlay.set_alpha(100)
        self.screen.blit(overlay, (0, 0))
        
        # Draw title with shadow
        shadow_offset = 2
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
            hover = button['rect'].collidepoint(pygame.mouse.get_pos())
            self.draw_button(button, hover)
            
            if hover and random.random() < 0.1:
                self.particles.append(Particle(
                    random.randint(button['rect'].left, button['rect'].right),
                    random.randint(button['rect'].top, button['rect'].bottom)
                ))

    def run(self):
        clock = pygame.time.Clock()
        current_screen = "main_menu"
        
        while True:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
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
                                elif button['text'] == 'Team':
                                    print("Team clicked")
                    elif current_screen == "game_select":
                        game_choice = self.game_select.handle_click(mouse_pos)
                        if game_choice:
                            print(f"{game_choice} selected!")
                            current_screen = "main_menu"
                            self.game_select = None
            
            # Update particles
            self.update_particles()
            
            # Clear screen
            self.screen.fill(self.BACKGROUND)
            
            # Draw current screen
            if current_screen == "main_menu":
                self.draw_main_menu()
            elif current_screen == "game_select":
                self.game_select.draw()
            
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
