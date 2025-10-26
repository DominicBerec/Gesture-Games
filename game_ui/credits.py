# credits.py - Credits page
import pygame
import math

class CreditsPage:
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
        self.title_font = pygame.font.Font(None, 80)
        self.heading_font = pygame.font.Font(None, 48)
        self.body_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 26)
        
        # Animation
        self.animation_time = 0
        
        # Back button
        self.back_button = pygame.Rect(50, 50, 150, 60)
        
        # Scroll offset for long content
        self.scroll_offset = 0
        self.max_scroll = 0
    
    def draw_section(self, y, title, items, color):
        """Draw a credit section with title and items"""
        # Title with underline
        title_surface = self.heading_font.render(title, True, color)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, y))
        self.screen.blit(title_surface, title_rect)
        
        # Underline
        underline_width = title_rect.width + 40
        pygame.draw.line(self.screen, color,
                        (self.WINDOW_WIDTH // 2 - underline_width // 2, y + 35),
                        (self.WINDOW_WIDTH // 2 + underline_width // 2, y + 35), 3)
        
        # Items
        item_y = y + 65
        for item in items:
            text_surface = self.body_font.render(item, True, self.COLOR_TEXT)
            text_rect = text_surface.get_rect(center=(self.WINDOW_WIDTH // 2, item_y))
            self.screen.blit(text_surface, text_rect)
            item_y += 40
        
        return item_y + 20
    
    def draw_tech_card(self, x, y, tech_name, purpose):
        """Draw a technology card"""
        card_width = 380
        card_height = 140
        
        # Animated pulse effect
        pulse = math.sin(self.animation_time + x * 0.01) * 2
        
        card_rect = pygame.Rect(x - pulse, y - pulse, card_width + pulse * 2, card_height + pulse * 2)
        pygame.draw.rect(self.screen, self.COLOR_CARD_BG, card_rect, border_radius=15)
        pygame.draw.rect(self.screen, self.COLOR_ACCENT, card_rect, 3, border_radius=15)
        
        # Tech name
        name_surface = self.heading_font.render(tech_name, True, self.COLOR_ACCENT)
        name_rect = name_surface.get_rect(center=(x + card_width // 2, y + 45))
        self.screen.blit(name_surface, name_rect)
        
        # Purpose
        purpose_surface = self.small_font.render(purpose, True, self.COLOR_TEXT_DIM)
        purpose_rect = purpose_surface.get_rect(center=(x + card_width // 2, y + 90))
        self.screen.blit(purpose_surface, purpose_rect)
    
    def draw(self):
        self.screen.fill(self.COLOR_BG)
        self.animation_time += 0.05
        
        # Back button (fixed position)
        pygame.draw.rect(self.screen, self.COLOR_CARD_BG, self.back_button, border_radius=10)
        pygame.draw.rect(self.screen, self.COLOR_ACCENT, self.back_button, 2, border_radius=10)
        back_text = self.body_font.render("Back", True, self.COLOR_TEXT)
        back_rect = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, back_rect)
        
        # Main title
        title = self.title_font.render("Credits", True, self.COLOR_TEXT)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)
        
        subtitle = self.body_font.render("Gesture Games - Hand Gesture Gaming System", True, self.COLOR_TEXT_DIM)
        subtitle_rect = subtitle.get_rect(center=(self.WINDOW_WIDTH // 2, 140))
        self.screen.blit(subtitle, subtitle_rect)
        
        current_y = 200
        
        # Development Team
        current_y = self.draw_section(
            current_y,
            "Development Team",
            ["Dominic, Luciano, Paul, Ainesh"],
            self.COLOR_ACCENT
        )
        
        # Technologies Used
        current_y += 20
        tech_title = self.heading_font.render("Technologies Used", True, self.COLOR_HIGHLIGHT)
        tech_rect = tech_title.get_rect(center=(self.WINDOW_WIDTH // 2, current_y))
        self.screen.blit(tech_title, tech_rect)
        
        pygame.draw.line(self.screen, self.COLOR_HIGHLIGHT,
                        (self.WINDOW_WIDTH // 2 - tech_rect.width // 2 - 20, current_y + 35),
                        (self.WINDOW_WIDTH // 2 + tech_rect.width // 2 + 20, current_y + 35), 3)
        
        # Tech cards
        tech_y = current_y + 70
        tech_cards = [
            ("Pygame", "Game Engine & Graphics"),
            ("OpenCV", "Camera & Image Processing"),
            ("MediaPipe", "Hand Gesture Detection"),
            ("Python", "Core Programming Language")
        ]
        
        cards_per_row = 2
        card_width = 380
        card_spacing = 40
        total_width = cards_per_row * card_width + (cards_per_row - 1) * card_spacing
        start_x = (self.WINDOW_WIDTH - total_width) // 2
        
        for i, (name, purpose) in enumerate(tech_cards):
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * (card_width + card_spacing)
            y = tech_y + row * 170
            self.draw_tech_card(x, y, name, purpose)

    def handle_click(self, pos):
        """Handle mouse/gesture clicks, return True if should go back"""
        if self.back_button.collidepoint(pos):
            return True
        return False