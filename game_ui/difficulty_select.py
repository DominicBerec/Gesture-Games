# difficulty_select.py - Difficulty selection screen
import pygame

class DifficultySelect:
    def __init__(self, screen, game_type):
        self.screen = screen
        self.game_type = game_type
        self.WINDOW_WIDTH = pygame.display.Info().current_w
        self.WINDOW_HEIGHT = pygame.display.Info().current_h
        
        # Box dimensions
        self.box_width = 350
        self.box_height = 450
        self.box_spacing = 80
        
        # Create difficulty boxes
        total_width = (3 * self.box_width) + (2 * self.box_spacing)
        start_x = (self.WINDOW_WIDTH - total_width) // 2
        center_y = self.WINDOW_HEIGHT // 2 - self.box_height // 2
        
        self.difficulties = [
            {
                'name': 'Easy',
                'rect': pygame.Rect(start_x, center_y, self.box_width, self.box_height),
                'color': (46, 204, 113),
                'description': 'Random moves'
            },
            {
                'name': 'Medium',
                'rect': pygame.Rect(start_x + self.box_width + self.box_spacing, center_y, 
                                  self.box_width, self.box_height),
                'color': (241, 196, 15),
                'description': 'Blocks wins'
            },
            {
                'name': 'Hard',
                'rect': pygame.Rect(start_x + (self.box_width + self.box_spacing) * 2, 
                                  center_y, self.box_width, self.box_height),
                'color': (231, 76, 60),
                'description': 'Unbeatable AI'
            }
        ]
        
        # Click detection
        self.last_click_time = 0
        self.click_cooldown = 500
    
    def draw(self):
        # Draw background
        from main import MainMenu
        if MainMenu.current_background:
            self.screen.blit(MainMenu.current_background, (0, 0))
        else:
            self.screen.fill((44, 62, 80))
        
        # Draw title
        font = pygame.font.Font(None, 96)
        title = f"Select {self.game_type} Difficulty"
        title_surface = font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_surface, title_rect)
        
        # Draw difficulty boxes
        mouse_pos = pygame.mouse.get_pos()
        for difficulty in self.difficulties:
            is_hovered = difficulty['rect'].collidepoint(mouse_pos)
            
            # Box background with shadow
            shadow_rect = difficulty['rect'].copy()
            shadow_rect.x += 5
            shadow_rect.y += 5
            pygame.draw.rect(self.screen, (0, 0, 0, 100), shadow_rect, border_radius=20)
            
            # Main box
            pygame.draw.rect(self.screen, difficulty['color'], difficulty['rect'], 
                           border_radius=20)
            
            # Hover effect
            if is_hovered:
                glow = pygame.Surface((difficulty['rect'].width, difficulty['rect'].height), 
                                    pygame.SRCALPHA)
                pygame.draw.rect(glow, (255, 255, 255, 80), 
                               glow.get_rect(), border_radius=20)
                self.screen.blit(glow, difficulty['rect'])
            
            # Difficulty name
            font = pygame.font.Font(None, 64)
            text = font.render(difficulty['name'], True, (255, 255, 255))
            text_rect = text.get_rect(centerx=difficulty['rect'].centerx,
                                     centery=difficulty['rect'].centery - 20)
            self.screen.blit(text, text_rect)
            
            # Description
            desc_font = pygame.font.Font(None, 32)
            desc_text = desc_font.render(difficulty['description'], True, (255, 255, 255))
            desc_rect = desc_text.get_rect(centerx=difficulty['rect'].centerx,
                                          centery=difficulty['rect'].centery + 40)
            self.screen.blit(desc_text, desc_rect)
        
        # Instructions
        inst_font = pygame.font.Font(None, 32)
        inst_text = inst_font.render("Click or make 'O' gesture to select", True, (255, 255, 255))
        inst_rect = inst_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 50))
        self.screen.blit(inst_text, inst_rect)
    
    def handle_click(self, pos):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_click_time < self.click_cooldown:
            return None
            
        for difficulty in self.difficulties:
            if difficulty['rect'].collidepoint(pos):
                self.last_click_time = current_time
                return self.game_type, difficulty['name'].lower()
        return None