# game_select.py - Game selection screen
import pygame
import os

class GameSelect:
    def __init__(self, screen):
        self.screen = screen
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Box dimensions
        self.box_width = 400
        self.box_height = 500
        self.box_spacing = 200
        
        # Create game boxes - centered
        center_y = self.WINDOW_HEIGHT // 2 - 50
        total_width = (2 * self.box_width) + self.box_spacing
        left_x = (self.WINDOW_WIDTH - total_width) // 2
        
        self.rps_box = pygame.Rect(left_x, center_y - self.box_height//2,
                                 self.box_width, self.box_height)
        self.ttt_box = pygame.Rect(left_x + self.box_width + self.box_spacing,
                                 center_y - self.box_height//2,
                                 self.box_width, self.box_height)
        
        # Load game sprites
        self.load_game_sprites()
        
        # Click detection
        self.last_click_time = 0
        self.click_cooldown = 500
        
    def load_game_sprites(self):
        self.icon_size = 120
        sprite_path = os.path.join(os.path.dirname(__file__), 'sprites', 'custom')
        
        # Load RPS sprites
        self.rps_sprites = {}
        for name in ['rock_icon', 'paper_icon', 'scissors_icon']:
            path = os.path.join(sprite_path, f'{name}.png')
            if os.path.exists(path):
                self.rps_sprites[name] = pygame.transform.scale(
                    pygame.image.load(path).convert_alpha(),
                    (self.icon_size, self.icon_size)
                )
            else:
                # Create fallback
                surf = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
                colors = {'rock_icon': (200, 100, 100), 'paper_icon': (100, 200, 100), 'scissors_icon': (100, 100, 200)}
                pygame.draw.circle(surf, (*colors.get(name, (200, 200, 200)), 200), 
                                 (self.icon_size//2, self.icon_size//2), 
                                 self.icon_size//2 - 10)
                self.rps_sprites[name] = surf
    
    def draw(self):
        # Use shared background from main menu
        from main import MainMenu
        if MainMenu.current_background:
            self.screen.blit(MainMenu.current_background, (0, 0))
        else:
            self.screen.fill((44, 62, 80))
        
        # Draw title
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("Select a Game", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw game boxes
        for box, title in [(self.rps_box, "Rock Paper Scissors"), (self.ttt_box, "Tic Tac Toe")]:
            # Box background
            pygame.draw.rect(self.screen, (52, 73, 94), box, border_radius=30)
            pygame.draw.rect(self.screen, (41, 128, 185), box, border_radius=30, width=3)
            
            # Title
            title_font = pygame.font.Font(None, 48)
            title_text = title_font.render(title, True, (255, 255, 255))
            title_rect = title_text.get_rect(centerx=box.centerx, top=box.top + 30)
            self.screen.blit(title_text, title_rect)
            
            # Draw game icons
            center_x, center_y = box.centerx, box.centery + 30
            
            if box == self.rps_box:
                # Draw RPS icons in horizontal row
                spacing = self.icon_size + 20
                start_x = center_x - (spacing * 1.5) + (self.icon_size // 2)
                
                for i, icon_name in enumerate(['rock_icon', 'paper_icon', 'scissors_icon']):
                    if icon_name in self.rps_sprites:
                        x = int(start_x + (i * spacing) - self.icon_size // 2)
                        y = center_y - self.icon_size // 2
                        self.screen.blit(self.rps_sprites[icon_name], (x, y))
            else:
                # Draw TTT preview - 3x3 mini grid
                grid_size = 40
                positions = []
                for row in range(3):
                    for col in range(3):
                        x = center_x - grid_size * 1.5 + col * grid_size
                        y = center_y - grid_size * 1.5 + row * grid_size
                        positions.append((x + grid_size//2, y + grid_size//2))
                        pygame.draw.rect(self.screen, (41, 128, 185),
                                       (x, y, grid_size, grid_size), 2)
                
                # Draw X's and O's
                symbols = [0, 1, 2, 1, 0, 1, 2, 1, 0]
                for i, (pos, symbol) in enumerate(zip(positions, symbols)):
                    if symbol == 0:  # X
                        size = 15
                        pygame.draw.line(self.screen, (255, 100, 100),
                                       (pos[0] - size, pos[1] - size),
                                       (pos[0] + size, pos[1] + size), 3)
                        pygame.draw.line(self.screen, (255, 100, 100),
                                       (pos[0] + size, pos[1] - size),
                                       (pos[0] - size, pos[1] + size), 3)
                    elif symbol == 1:  # O
                        pygame.draw.circle(self.screen, (100, 100, 255), pos, 12, 3)
            
            # Hover effect
            mouse_pos = pygame.mouse.get_pos()
            if box.collidepoint(mouse_pos):
                glow = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
                pygame.draw.rect(glow, (41, 128, 185, 50), glow.get_rect(), border_radius=30)
                self.screen.blit(glow, box)
        
        # Draw instructions
        font = pygame.font.Font(None, 32)
        inst_text = font.render("Click or make 'O' gesture to select", True, (255, 255, 255))
        inst_rect = inst_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def handle_click(self, pos):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time < self.click_cooldown:
            return None
            
        if self.rps_box.collidepoint(pos):
            self.last_click_time = current_time
            return "RPS"
        elif self.ttt_box.collidepoint(pos):
            self.last_click_time = current_time
            return "TTT"
        return None