import pygame
import random
import math
import sys
from level_manager import LevelManager
from maps.map2_snooker import create_snooker_map
from maps.map3_carom import create_carom_map
from scoring_system import ScoringSystem

pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BALL_RADIUS = 18
POCKET_RADIUS = 35
FRICTION = 0.995        # ma sát tuyến tính (gần thực tế)
MIN_SPEED = 0.05
INITIAL_SPEED = 40      # giới hạn tốc độ tối đa của cú đánh
WALL_BOUNCE_DAMP = 0.9  # mất năng lượng khi bật thành
BALL_RESTITUTION = 0.98 # độ đàn hồi va chạm giữa 2 bi
BALL_MASS = 1.0

# Colors - Enhanced color palette
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (34, 139, 34)  # Forest green for table
DARK_GREEN = (22, 101, 22)  # Darker green for table depth
BROWN = (101, 67, 33)  # Wood brown
LIGHT_BROWN = (139, 90, 43)  # Lighter wood
CUE_COLOR = (245, 245, 220)  # Beige cue stick
BUTTON_COLOR = (70, 70, 70)
BUTTON_HOVER_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0, 128)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)

# UI Colors
MENU_BG = (25, 25, 40)
TITLE_COLOR = (255, 255, 255)
SELECTED_COLOR = (255, 200, 0)
UI_BG = (40, 40, 50)
SCORE_COLOR = (255, 255, 200)

class Ball:
    def __init__(self, x, y, number, color, is_cue=False):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(0, 0)
        self.number = number
        self.color = color
        self.in_pocket = False
        self.is_cue = is_cue
        self.radius = BALL_RADIUS
        self.mass = BALL_MASS

    def update(self):
        if self.in_pocket:
            return
        self.pos += self.vel
        # apply simple rolling friction
        self.vel *= FRICTION
        if self.vel.length() < MIN_SPEED:
            self.vel = pygame.Vector2(0, 0)

    def draw(self, screen):
        if self.in_pocket:
            return
        
        # Draw shadow first
        shadow_offset = 2
        shadow_pos = (int(self.pos.x + shadow_offset), int(self.pos.y + shadow_offset))
        shadow_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, 80), (self.radius, self.radius), self.radius)
        screen.blit(shadow_surface, (shadow_pos[0] - self.radius, shadow_pos[1] - self.radius))
        
        # Draw ball with gradient effect (simulated with highlight)
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw highlight for 3D effect
        highlight_pos = (int(self.pos.x - self.radius * 0.3), int(self.pos.y - self.radius * 0.3))
        highlight_radius = self.radius // 3
        highlight_surface = pygame.Surface((highlight_radius * 2, highlight_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(highlight_surface, (255, 255, 255, 150), (highlight_radius, highlight_radius), highlight_radius)
        screen.blit(highlight_surface, (highlight_pos[0] - highlight_radius, highlight_pos[1] - highlight_radius))
        
        # Draw border
        pygame.draw.circle(screen, (40, 40, 40), (int(self.pos.x), int(self.pos.y)), self.radius, 2)
        
        if not self.is_cue:
            # Draw stripe pattern for pool balls 9-15
            if 9 <= self.number <= 15:
                # Draw white stripe band
                stripe_width = self.radius * 1.2
                stripe_height = self.radius * 0.4
                stripe_rect = pygame.Rect(int(self.pos.x - stripe_width//2), 
                                         int(self.pos.y - stripe_height//2),
                                         int(stripe_width), int(stripe_height))
                pygame.draw.ellipse(screen, (255, 255, 255), stripe_rect)
            
            # Draw number with better styling
            font = pygame.font.Font(None, 20)
            font.set_bold(True)
            # Text shadow
            text = font.render(str(self.number), True, (0, 0, 0))
            text_rect = text.get_rect(center=(int(self.pos.x) + 1, int(self.pos.y) + 1))
            screen.blit(text, text_rect)
            # Text main
            text = font.render(str(self.number), True, WHITE)
            text_rect = text.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            screen.blit(text, text_rect)
        else:
            # Cue ball with distinct white appearance
            pygame.draw.circle(screen, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius)
            # Inner circle for depth
            pygame.draw.circle(screen, (245, 245, 245), (int(self.pos.x), int(self.pos.y)), self.radius - 2)

class Table:
    def __init__(self, map_type):
        self.width = 1000
        self.height = 550
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.map_type = map_type
        self.pockets = self.setup_pockets()
        
    def setup_pockets(self):
        # 4 corners for simplicity (can add middle pockets per map)
        pockets = [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x, self.y + self.height),
            (self.x + self.width, self.y + self.height)
        ]
        if self.map_type == 2:
            pockets.insert(2, (self.x + self.width//2, self.y))  # top middle
            pockets.insert(-2, (self.x + self.width//2, self.y + self.height))  # bottom middle
        return pockets

    def draw(self, screen):
        # Draw outer wood frame with gradient effect
        frame_thickness = 25
        # Outer shadow
        pygame.draw.rect(screen, (20, 20, 20), 
                        (self.x - frame_thickness - 3, self.y - frame_thickness - 3, 
                         self.width + 2*frame_thickness + 6, self.height + 2*frame_thickness + 6))
        # Wood frame - gradient from dark to light
        for i in range(frame_thickness):
            shade = 60 - i * 1
            pygame.draw.rect(screen, (shade, shade*0.6, shade*0.4), 
                           (self.x - frame_thickness + i, self.y - frame_thickness + i,
                            self.width + 2*(frame_thickness - i), self.height + 2*(frame_thickness - i)), 2)
        
        # Draw felt with gradient for depth
        # Main felt area
        pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        # Lighter center area for depth
        center_rect = pygame.Rect(self.x + self.width//4, self.y + self.height//4,
                                 self.width//2, self.height//2)
        for y in range(center_rect.top, center_rect.bottom):
            ratio = (y - center_rect.top) / center_rect.height
            color = tuple(int(GREEN[i] * (1 + 0.1 * (1 - ratio))) for i in range(3))
            pygame.draw.line(screen, color, (center_rect.left, y), (center_rect.right, y))
        
        # Draw cushions with 3D effect
        cushion_color = (139, 69, 19)  # Brown cushion
        # Top cushion
        pygame.draw.rect(screen, cushion_color, (self.x - 15, self.y - 15, self.width + 30, 15))
        # Bottom cushion
        pygame.draw.rect(screen, cushion_color, (self.x - 15, self.y + self.height, self.width + 30, 15))
        # Left cushion
        pygame.draw.rect(screen, cushion_color, (self.x - 15, self.y - 15, 15, self.height + 30))
        # Right cushion
        pygame.draw.rect(screen, cushion_color, (self.x + self.width, self.y - 15, 15, self.height + 30))
        # Cushion highlights
        pygame.draw.line(screen, (180, 100, 50), (self.x - 15, self.y - 15), 
                        (self.x + self.width + 15, self.y - 15), 2)
        pygame.draw.line(screen, (180, 100, 50), (self.x - 15, self.y - 15), 
                        (self.x - 15, self.y + self.height + 15), 2)
        
        # Draw pockets with depth effect
        for pocket in self.pockets:
            # Outer shadow ring
            pygame.draw.circle(screen, (0, 0, 0), pocket, POCKET_RADIUS + 3)
            # Main pocket (dark hole)
            pygame.draw.circle(screen, (10, 10, 10), pocket, POCKET_RADIUS)
            # Inner highlight for depth
            pygame.draw.circle(screen, (30, 30, 30), (pocket[0] - 3, pocket[1] - 3), POCKET_RADIUS - 5)

class Game:
    def __init__(self):
        # ...existing code...
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Billiards Game")
        self.clock = pygame.time.Clock()
        self.state = "MENU"
        self.balls = []
        self.prediction = ""
        self.map_type = 1
        self.table = Table(self.map_type)
        self.font = pygame.font.Font(None, 42)
        self.font_large = pygame.font.Font(None, 56)
        self.font_small = pygame.font.Font(None, 28)
        self.selected_ball = None
        self.aiming = False
        self.aim_start = None
        self.aim_end = None

        # Level manager
        self.level_manager = LevelManager(max_map=3)
        self.level_options = []

        # Scoring and shot tracking
        self.score = 0
        self.last_gain_text = ""
        self.shot_in_progress = False
        self.shot_pocketed_count = 0
        self.shot_score = 0

        # per-map config
        self.map_cfg = None
        # scoring callback
        self.score_ball = lambda number: 10 + number

        # carom-specific state
        self.carom_mode = None
        self.carom_first_contact_bounces = None
        self.carom_contacts = set()  # Track unique ball contacts in current shot
        self.shot_in_progress = False

        # Scoring system
        self.scoring = ScoringSystem()

        self.buttons = {
            'back': pygame.Rect(10, 60, 100, 35),
            'reset': pygame.Rect(120, 60, 100, 35)
        }
        
        # Pool 8-ball game state tracking
        self.pool_player_group = None  # 'solid' or 'stripe', None = not assigned yet
        self.pool_solids_pocketed = 0
        self.pool_stripes_pocketed = 0
        
        # Snooker game state tracking
        self.snooker_expecting_red = True  # True = expect red, False = expect color
        self.snooker_color_respot_positions = {}  # Track where colors should respot

    def start_level(self):
        """
        Bắt đầu level theo self.map_type.
        Lấy cấu hình từ các factory map và spawn các Ball.
        """
        # default Table centered; we'll override width/height from cfg
        self.balls = []
        self.prediction = ""
        self.map_cfg = None
        # choose map config
        if self.map_type == 2:
            cfg = create_snooker_map()
        elif self.map_type == 3:
            # default carom mode = 'libre' (người dùng có thể thay đổi nếu muốn)
            cfg = create_carom_map(mode='libre')
        else:
            # map1 default behavior: use previous simple rack (existing)
            cfg = None

        if cfg is not None:
            self.map_cfg = cfg
            # set table size and pockets based on relative coords
            self.table.width = cfg.get('width', self.table.width)
            self.table.height = cfg.get('height', self.table.height)
            # center table on screen
            self.table.x = (SCREEN_WIDTH - self.table.width) // 2
            self.table.y = (SCREEN_HEIGHT - self.table.height) // 2
            # compute absolute pocket positions
            pockets = []
            for rx, ry in cfg.get('pockets', []):
                pockets.append((int(self.table.x + rx * self.table.width), int(self.table.y + ry * self.table.height)))
            self.table.pockets = pockets

            # spawn balls
            for b in cfg.get('balls', []):
                x = int(self.table.x + b['rx'] * self.table.width)
                y = int(self.table.y + b['ry'] * self.table.height)
                self.balls.append(Ball(x, y, b.get('number', 0), b.get('color', (200,200,200)), is_cue=b.get('is_cue', False)))

            # set scoring callback
            self.score_ball = cfg.get('scoring', lambda n: 10 + (n or 0))

            # carom mode
            if cfg.get('mode') == 'libre' or cfg.get('mode') == 'one' or cfg.get('mode') == 'three' or cfg.get('mode') == 'carom':
                # if map 3 uses 'mode' key it will be 'libre'/'one'/'three'
                self.carom_mode = cfg.get('mode', 'libre')
            elif cfg.get('mode') == 'snooker':
                self.carom_mode = None
        else:
            # fallback: original map1 rack (unchanged)
            self.table = Table(self.map_type)
            # Cue ball position (near left quarter center)
            cue_x = self.table.x + int(self.table.width * 0.25)
            cue_y = self.table.y + self.table.height // 2
            cue = Ball(cue_x, cue_y, 0, WHITE, is_cue=True)
            self.balls.append(cue)
            # Rack triangle (15 balls) with proper pool colors
            rows = 5
            start_x = self.table.x + int(self.table.width * 0.70)
            start_y = self.table.y + self.table.height // 2
            offset = BALL_RADIUS * 2 + 0.5
            
            # Standard pool ball colors: 1-7 solid, 8 black, 9-15 stripe
            pool_colors = {
                1: (255, 255, 0),    # Yellow
                2: (0, 0, 255),      # Blue
                3: (255, 0, 0),      # Red
                4: (128, 0, 128),    # Purple
                5: (255, 165, 0),    # Orange
                6: (0, 255, 0),      # Green
                7: (128, 0, 0),      # Maroon
                8: (0, 0, 0),        # Black
                9: (255, 255, 0),    # Yellow stripe
                10: (0, 0, 255),     # Blue stripe
                11: (255, 0, 0),     # Red stripe
                12: (128, 0, 128),   # Purple stripe
                13: (255, 165, 0),   # Orange stripe
                14: (0, 255, 0),     # Green stripe
                15: (128, 0, 0),     # Maroon stripe
            }
            
            number = 1
            for r in range(rows):
                row_len = r + 1
                x = start_x + r * (BALL_RADIUS * 2 * 0.87)
                y = start_y - (row_len-1) * offset / 2
                for c in range(row_len):
                    col_y = y + c * offset
                    # Use proper color, fallback to random if needed
                    color = pool_colors.get(number, (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
                    self.balls.append(Ball(x, col_y, number, color))
                    number += 1
            self.score_ball = lambda b: 10 + (b.number or 0)
            self.carom_mode = None

        # reset shot/carom trackers
        self.shot_in_progress = False
        self.carom_contacts = set()
        self.carom_bounce_count = 0
        self.carom_first_contact_bounces = None
        self.last_gain_text = ""
        
        # Reset game mode specific state
        if self.map_type == 1:
            self.pool_player_group = None
            self.pool_solids_pocketed = 0
            self.pool_stripes_pocketed = 0
        elif self.map_type == 2:
            self.snooker_expecting_red = True
            self.scoring.red_count = 15
            self.scoring.last_red = False

    def check_collisions(self):
        """
        Mở rộng: 
        - gọi score_ball(ball) khi bi rơi (snooker sử dụng callback khác).
        - Track bounces cho Carom và detect carom contact sequence.
        """
        # Ball-Wall collisions
        for ball in self.balls:
            if ball.in_pocket:
                continue
            # left wall
            if ball.pos.x - ball.radius < self.table.x:
                ball.pos.x = self.table.x + ball.radius
                ball.vel.x = -ball.vel.x * WALL_BOUNCE_DAMP
                # count bounce for carom only when cue ball bounces while shot in progress
                if self.carom_mode and self.shot_in_progress and ball.is_cue:
                    self.carom_bounce_count += 1
            # right wall
            if ball.pos.x + ball.radius > self.table.x + self.table.width:
                ball.pos.x = self.table.x + self.table.width - ball.radius
                ball.vel.x = -ball.vel.x * WALL_BOUNCE_DAMP
                if self.carom_mode and self.shot_in_progress and ball.is_cue:
                    self.carom_bounce_count += 1
            # top
            if ball.pos.y - ball.radius < self.table.y:
                ball.pos.y = self.table.y + ball.radius
                ball.vel.y = -ball.vel.y * WALL_BOUNCE_DAMP
                if self.carom_mode and self.shot_in_progress and ball.is_cue:
                    self.carom_bounce_count += 1
            # bottom
            if ball.pos.y + ball.radius > self.table.y + self.table.height:
                ball.pos.y = self.table.y + self.table.height - ball.radius
                ball.vel.y = -ball.vel.y * WALL_BOUNCE_DAMP
                if self.carom_mode and self.shot_in_progress and ball.is_cue:
                    self.carom_bounce_count += 1

        # Ball-Ball collisions with Carom tracking
        for i in range(len(self.balls)):
            for j in range(i+1, len(self.balls)):
                a = self.balls[i]
                b = self.balls[j]
                if a.in_pocket or b.in_pocket:
                    continue
                    
                delta = b.pos - a.pos
                dist = delta.length()
                if dist < a.radius + b.radius:
                    # Track Carom contacts when cue ball hits others
                    # Store tuple (ball_number, bounce_count_at_contact) for proper tracking
                    if self.map_type == 3 and self.shot_in_progress:
                        if a.is_cue:
                            self.carom_contacts.add((b.number, self.carom_bounce_count))
                        elif b.is_cue:
                            self.carom_contacts.add((a.number, self.carom_bounce_count))
                    
                    # Regular collision physics
                    overlap = a.radius + b.radius - dist
                    direction = delta.normalize()
                    a.pos -= direction * (overlap * 0.5)
                    b.pos += direction * (overlap * 0.5)

                    # relative velocity
                    rv = b.vel - a.vel
                    vel_along_normal = rv.dot(direction)
                    if vel_along_normal > 0:
                        continue
                    # impulse scalar
                    e = BALL_RESTITUTION
                    j = -(1 + e) * vel_along_normal
                    j /= (1 / a.mass + 1 / b.mass)
                    impulse = direction * j
                    a.vel -= impulse * (1 / a.mass)
                    b.vel += impulse * (1 / b.mass)

        # Ball-Pocket check with realistic scoring
        for ball in self.balls:
            if ball.in_pocket:
                continue
                
            for pocket in self.table.pockets:
                dx = ball.pos.x - pocket[0]
                dy = ball.pos.y - pocket[1]
                if math.hypot(dx, dy) < POCKET_RADIUS:
                    ball.in_pocket = True
                    ball.vel = pygame.Vector2(0, 0)
                    ball.pos = pygame.Vector2(pocket[0], pocket[1])
                    
                    if not ball.is_cue:
                        pts = 0
                        valid_shot = True
                        
                        if self.map_type == 1:
                            # Pool 8-ball scoring with proper rules
                            pts, valid_shot = self.score_pool_ball(ball.number)
                        elif self.map_type == 2:
                            # Snooker scoring with proper rules
                            pts, valid_shot = self.score_snooker_ball(ball.number)
                            
                        if valid_shot and pts > 0:
                            self.score += pts
                            self.shot_score += pts
                            self.shot_pocketed_count += 1
                            self.last_gain_text = f"+{pts} pts"
                            self.prediction = f"Ball {ball.number} pocketed!"
                        elif not valid_shot:
                            self.prediction = "Invalid shot!"
                            self.last_gain_text = "No points - wrong ball"
                            
                    elif ball.is_cue:
                        # Respawn cue ball
                        ball.in_pocket = False
                        ball.pos = pygame.Vector2(
                            self.table.x + int(self.table.width * 0.25),
                            self.table.y + self.table.height // 2
                        )
                        ball.vel = pygame.Vector2(0, 0)
                        self.prediction = "Cue ball in pocket!"
                        
        # Check for Carom shot completion (handled in main loop)
    
    def score_pool_ball(self, ball_number):
        """
        Score Pool 8-ball ball with proper rules:
        - First ball determines player's group (solid 1-7 or stripe 9-15)
        - Must clear all balls of your group before shooting 8-ball
        - 8-ball is worth 20 points
        Returns: (points, valid_shot)
        """
        if ball_number == 8:
            # Check if player can shoot 8-ball
            if self.pool_player_group is None:
                return 0, False  # Can't shoot 8-ball first
            
            if self.pool_player_group == 'solid':
                if self.pool_solids_pocketed < 7:
                    return 0, False  # Must clear all solids first
            elif self.pool_player_group == 'stripe':
                if self.pool_stripes_pocketed < 7:
                    return 0, False  # Must clear all stripes first
            
            return 20, True
        
        elif 1 <= ball_number <= 7:  # Solids
            if self.pool_player_group is None:
                # First ball determines group
                self.pool_player_group = 'solid'
                self.pool_solids_pocketed = 1
                return 10, True
            elif self.pool_player_group == 'solid':
                self.pool_solids_pocketed += 1
                return 10, True
            else:
                return 0, False  # Wrong group
        
        elif 9 <= ball_number <= 15:  # Stripes
            if self.pool_player_group is None:
                # First ball determines group
                self.pool_player_group = 'stripe'
                self.pool_stripes_pocketed = 1
                return 15, True
            elif self.pool_player_group == 'stripe':
                self.pool_stripes_pocketed += 1
                return 15, True
            else:
                return 0, False  # Wrong group
        
        return 0, False
    
    def score_snooker_ball(self, ball_number):
        """
        Score Snooker ball with proper rules:
        - Must alternate: red -> color -> red -> color
        - Red balls: 1 point each
        - Color balls: respot after potting (not fully implemented)
        Returns: (points, valid_shot)
        """
        if ball_number == 1:  # Red ball
            if not self.snooker_expecting_red:
                return 0, False  # Must pot red first
            self.snooker_expecting_red = False
            self.scoring.last_red = True
            self.scoring.red_count -= 1
            return 1, True
        
        elif 2 <= ball_number <= 7:  # Color balls
            if self.snooker_expecting_red:
                if self.scoring.red_count > 0:
                    return 0, False  # Must pot red first if reds remain
            # Valid color shot
            self.snooker_expecting_red = True  # After color, expect red again
            self.scoring.last_red = False
            # Note: In real snooker, color would respot, but we'll just continue
            return ball_number, True
        
        return 0, False

    def draw_menu(self):
        # Enhanced gradient background with animated feel
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(20 + ratio * 25)
            g = int(20 + ratio * 25)
            b = int(35 + ratio * 15)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Decorative lines at top and bottom
        pygame.draw.line(self.screen, GOLD, (0, 0), (SCREEN_WIDTH, 0), 3)
        pygame.draw.line(self.screen, GOLD, (0, SCREEN_HEIGHT-1), (SCREEN_WIDTH, SCREEN_HEIGHT-1), 3)
        
        # Title with enhanced shadow effect
        title_text = "🎱 BILLIARDS GAME"
        title = self.font_large.render(title_text, True, TITLE_COLOR)
        title_shadow = self.font_large.render(title_text, True, (0, 0, 0))
        title_x = SCREEN_WIDTH//2 - title.get_width()//2
        title_y = 50
        # Multiple shadow layers for depth
        for offset in [(3, 3), (2, 2), (1, 1)]:
            self.screen.blit(title_shadow, (title_x + offset[0], title_y + offset[1]))
        self.screen.blit(title, (title_x, title_y))
        
        # Map selection cards with descriptions
        map_info = [
            ("Pool 8-Ball", "Pocket all balls\nFirst ball determines\nyour group", "🎯"),
            ("Snooker", "Alternate red\nand color balls\nScore highest!", "🎨"),
            ("Carom", "Hit both balls\nin one shot\nNo pockets!", "⚡")
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        card_spacing = 240
        start_x = (SCREEN_WIDTH - (card_spacing * 2)) // 2
        
        for i in range(1, 4):
            x = start_x + (i - 1) * card_spacing
            y = 140
            w = 220
            h = 180
            rect = pygame.Rect(x, y, w, h)
            hover = rect.collidepoint(mouse_pos)
            selected = self.map_type == i
            
            # Card background
            if selected:
                # Selected card - glowing effect
                for glow in range(5, 0, -1):
                    alpha = 50 - glow * 8
                    glow_rect = pygame.Surface((w + glow*4, h + glow*4), pygame.SRCALPHA)
                    glow_rect.fill((*SELECTED_COLOR[:3], alpha))
                    self.screen.blit(glow_rect, (x - glow*2 - 10, y - glow*2 - 10))
                card_color = (70, 70, 90)
                border_color = SELECTED_COLOR
            elif hover:
                card_color = (65, 65, 85)
                border_color = (200, 200, 200)
            else:
                card_color = (50, 50, 65)
                border_color = (100, 100, 100)
            
            # Draw card
            pygame.draw.rect(self.screen, card_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 3)
            
            # Icon
            icon_text = self.font_large.render(map_info[i-1][2], True, SELECTED_COLOR if selected else SILVER)
            self.screen.blit(icon_text, (x + w//2 - icon_text.get_width()//2, y + 15))
            
            # Map name
            name_text = self.font.render(map_info[i-1][0], True, WHITE)
            self.screen.blit(name_text, (x + w//2 - name_text.get_width()//2, y + 50))
            
            # Description
            desc_lines = map_info[i-1][1].split('\n')
            for idx, line in enumerate(desc_lines):
                desc = self.font_small.render(line, True, (180, 180, 180))
                self.screen.blit(desc, (x + w//2 - desc.get_width()//2, y + 90 + idx * 20))
            
            # Map number badge
            badge_size = 35
            badge_x = x + w - badge_size - 10
            badge_y = y + 10
            pygame.draw.circle(self.screen, SELECTED_COLOR if selected else (80, 80, 80), 
                             (badge_x + badge_size//2, badge_y + badge_size//2), badge_size//2)
            num_text = self.font_small.render(str(i), True, WHITE)
            self.screen.blit(num_text, (badge_x + badge_size//2 - num_text.get_width()//2,
                                       badge_y + badge_size//2 - num_text.get_height()//2))
        
        # Start button with enhanced design
        start_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 60)
        hover_start = start_rect.collidepoint(mouse_pos)
        
        # Button glow
        if hover_start:
            for glow in range(3, 0, -1):
                glow_rect = pygame.Surface((start_rect.width + glow*4, start_rect.height + glow*4), pygame.SRCALPHA)
                glow_rect.fill((*GREEN[:3], 30 - glow * 8))
                self.screen.blit(glow_rect, (start_rect.x - glow*2, start_rect.y - glow*2))
        
        # Button
        btn_color = (60, 150, 60) if hover_start else GREEN
        pygame.draw.rect(self.screen, btn_color, start_rect)
        pygame.draw.rect(self.screen, (120, 255, 120), start_rect, 2)
        
        start_text = self.font_large.render("▶ START", True, WHITE)
        self.screen.blit(start_text, (start_rect.centerx - start_text.get_width()//2,
                                      start_rect.centery - start_text.get_height()//2))
        
        # Instructions at bottom
        instructions = "Click a game mode above, then click START to begin"
        inst_text = self.font_small.render(instructions, True, (150, 150, 150))
        self.screen.blit(inst_text, (SCREEN_WIDTH//2 - inst_text.get_width()//2, SCREEN_HEIGHT - 30))

    def draw_level_select(self):
        # Draw gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(25 + ratio * 30)
            g = int(25 + ratio * 30)
            b = int(40 + ratio * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Title with shadow
        title_text = "LEVEL COMPLETE!"
        subtitle_text = "Choose next map:"
        title = self.font_large.render(title_text, True, GOLD)
        title_shadow = self.font_large.render(title_text, True, (0, 0, 0))
        title_x = SCREEN_WIDTH//2 - title.get_width()//2
        self.screen.blit(title_shadow, (title_x + 2, 82))
        self.screen.blit(title, (title_x, 80))
        
        subtitle = self.font.render(subtitle_text, True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 140))
        
        # Level buttons with modern design
        start_x = SCREEN_WIDTH//2 - (120 * len(self.level_options))//2
        y = 220
        mouse_pos = pygame.mouse.get_pos()
        
        for idx, m in enumerate(self.level_options):
            x = start_x + idx*130
            rect = pygame.Rect(x, y, 110, 70)
            hover = rect.collidepoint(mouse_pos)
            
            if hover:
                pygame.draw.rect(self.screen, SELECTED_COLOR, (x-2, y-2, 114, 74), border_radius=10)
                pygame.draw.rect(self.screen, (70, 70, 90), rect, border_radius=10)
            else:
                pygame.draw.rect(self.screen, (60, 60, 80), rect, border_radius=10)
            
            text = self.font.render(f"Map {m}", True, WHITE if hover else SILVER)
            self.screen.blit(text, (rect.centerx - text.get_width()//2,
                                    rect.centery - text.get_height()//2))
        
        # Back button
        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 60, 350, 120, 45)
        hover = back_rect.collidepoint(mouse_pos)
        
        if hover:
            pygame.draw.rect(self.screen, (150, 50, 50), back_rect, border_radius=8)
        else:
            pygame.draw.rect(self.screen, RED, back_rect, border_radius=8)
        
        back_text = self.font.render("Menu", True, WHITE)
        self.screen.blit(back_text, (back_rect.centerx - back_text.get_width()//2,
                                     back_rect.centery - back_text.get_height()//2))

    def _compute_reflected_path(self, origin, direction, max_segments=4, max_length=1200):
        # returns list of points [origin, p1, p2, ...] for drawing projected trajectory with reflections
        pts = [origin.copy()]
        p = origin.copy()
        dirv = direction.normalize()
        remaining = max_length
        left = self.table.x + BALL_RADIUS
        right = self.table.x + self.table.width - BALL_RADIUS
        top = self.table.y + BALL_RADIUS
        bottom = self.table.y + self.table.height - BALL_RADIUS

        for _ in range(max_segments):
            if remaining <= 0:
                break
            tx = float('inf')
            ty = float('inf')
            if abs(dirv.x) > 1e-6:
                if dirv.x > 0:
                    tx = (right - p.x) / dirv.x
                else:
                    tx = (left - p.x) / dirv.x
            if abs(dirv.y) > 1e-6:
                if dirv.y > 0:
                    ty = (bottom - p.y) / dirv.y
                else:
                    ty = (top - p.y) / dirv.y
            # choose nearest positive
            t = min([t for t in (tx, ty) if t > 1e-6], default=None)
            if t is None:
                # goes nowhere (parallel), extend by remaining
                next_p = p + dirv * remaining
                pts.append(next_p)
                break
            travel = min(t, remaining)
            next_p = p + dirv * travel
            pts.append(next_p)
            remaining -= travel
            p = next_p
            # reflect
            # if tx is chosen (vertical wall), reflect x component
            # compare which t matched (within small epsilon)
            if abs(t - tx) < 1e-4:
                dirv.x = -dirv.x
            elif abs(t - ty) < 1e-4:
                dirv.y = -dirv.y
            else:
                break
        return pts

    def draw_cue(self):
        # draw cue stick and power bar when aiming + trajectory preview
        cue_ball = next((b for b in self.balls if b.is_cue), None)
        if not cue_ball:
            return
        if self.aiming:
            mouse = pygame.Vector2(pygame.mouse.get_pos())
            # direction from cue ball to mouse (drag direction)
            dirv = (self.aim_start - mouse)
            if dirv.length() == 0:
                return
            direction = dirv.normalize()
            # cue stick length proportional to power
            power = min(dirv.length(), INITIAL_SPEED)
            stick_len = 120 + power
            start = cue_ball.pos - direction * 8  # gap
            end = cue_ball.pos - direction * stick_len
            pygame.draw.line(self.screen, CUE_COLOR, (int(start.x), int(start.y)), (int(end.x), int(end.y)), 6)
            # power bar
            bar_w = 200
            bar_h = 12
            bar_x = 30
            bar_y = SCREEN_HEIGHT - 50
            pygame.draw.rect(self.screen, (80,80,80), (bar_x, bar_y, bar_w, bar_h))
            p = power / INITIAL_SPEED
            pygame.draw.rect(self.screen, (200,50,50), (bar_x, bar_y, int(bar_w * p), bar_h))

            # trajectory preview (reflecting)
            preview_dir = direction
            pts = self._compute_reflected_path(cue_ball.pos, preview_dir, max_segments=5, max_length=800 + int(power*6))
            # draw dotted segments
            for i in range(len(pts)-1):
                a = pts[i]
                b = pts[i+1]
                # draw dashed line
                seg_v = b - a
                seg_len = seg_v.length()
                if seg_len == 0:
                    continue
                seg_dir = seg_v.normalize()
                dash = 12
                drawn = 0
                while drawn < seg_len:
                    s = a + seg_dir * drawn
                    e = a + seg_dir * min(drawn + dash*0.6, seg_len)
                    pygame.draw.line(self.screen, (220,220,220), (int(s.x), int(s.y)), (int(e.x), int(e.y)), 2)
                    drawn += dash

    def draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw Back button with modern style
        hover = self.buttons['back'].collidepoint(mouse_pos)
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.buttons['back'], border_radius=5)
        pygame.draw.rect(self.screen, (90, 90, 90), self.buttons['back'], width=2, border_radius=5)
        
        back_text = self.font_small.render("Menu", True, BUTTON_TEXT_COLOR)
        back_rect = back_text.get_rect(center=self.buttons['back'].center)
        self.screen.blit(back_text, back_rect)
        
        # Draw Reset button with modern style
        hover = self.buttons['reset'].collidepoint(mouse_pos)
        color = BUTTON_HOVER_COLOR if hover else BUTTON_COLOR
        pygame.draw.rect(self.screen, color, self.buttons['reset'], border_radius=5)
        pygame.draw.rect(self.screen, (90, 90, 90), self.buttons['reset'], width=2, border_radius=5)
        
        reset_text = self.font_small.render("Reset", True, BUTTON_TEXT_COLOR)
        reset_rect = reset_text.get_rect(center=self.buttons['reset'].center)
        self.screen.blit(reset_text, reset_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Handle button clicks during GAME state
                    if self.state == "GAME":
                        if self.buttons['back'].collidepoint(mouse_pos):
                            self.state = "MENU"
                            continue
                        elif self.buttons['reset'].collidepoint(mouse_pos):
                            self.start_level()  # Reset current map
                            continue

                    # map selection with card design
                    if self.state == "MENU":
                        map_info = [
                            ("Pool 8-Ball", "Pocket all balls\nFirst ball determines\nyour group", "🎯"),
                            ("Snooker", "Alternate red\nand color balls\nScore highest!", "🎨"),
                            ("Carom", "Hit both balls\nin one shot\nNo pockets!", "⚡")
                        ]
                        card_spacing = 240
                        start_x = (SCREEN_WIDTH - (card_spacing * 2)) // 2
                        
                        # Check card clicks
                        for i in range(1, 4):
                            x = start_x + (i - 1) * card_spacing
                            y = 140
                            w = 220
                            h = 180
                            rect = pygame.Rect(x, y, w, h)
                            if rect.collidepoint(mouse_pos):
                                self.map_type = i
                                self.table = Table(self.map_type)
                                break
                        
                        # Start button
                        start_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, 450, 200, 60)
                        if start_rect.collidepoint(mouse_pos):
                            self.state = "GAME"
                            self.start_level()

                    elif self.state == "GAME":
                        # Start aiming if cue ball is stationary: allow click anywhere when stationary (easier)
                        cue_ball = next((b for b in self.balls if b.is_cue), None)
                        if cue_ball and not cue_ball.in_pocket:
                            if cue_ball.vel.length() == 0:
                                self.aiming = True
                                self.aim_start = pygame.Vector2(mouse_pos)

                    elif self.state == "LEVEL_SELECT":
                        start_x = SCREEN_WIDTH//2 - (100 * len(self.level_options))//2
                        y = 200
                        clicked = False
                        for idx, m in enumerate(self.level_options):
                            rect = pygame.Rect(start_x + idx*110, y, 100, 50)
                            if rect.collidepoint(mouse_pos):
                                self.map_type = m
                                self.start_level()
                                self.state = "GAME"
                                clicked = True
                                break
                        back_rect = pygame.Rect(SCREEN_WIDTH//2 - 50, 350, 100, 40)
                        if back_rect.collidepoint(mouse_pos) and not clicked:
                            self.state = "MENU"

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.state == "GAME" and self.aiming and self.aim_start:
                        self.aim_end = pygame.Vector2(pygame.mouse.get_pos())
                        cue_ball = next((b for b in self.balls if b.is_cue), None)
                        dirv = self.aim_start - self.aim_end
                        if cue_ball and dirv.length() > 0:
                            # Start new shot tracking
                            self.shot_in_progress = True
                            self.carom_contacts.clear()
                            
                            power = min(dirv.length(), INITIAL_SPEED)
                            # stronger power scaling to make it easier
                            vel = dirv.normalize() * (power * 0.8)
                            cue_ball.vel = vel
                            # mark shot started for combo tracking
                            self.shot_in_progress = True
                            self.shot_pocketed_count = 0
                            self.shot_score = 0
                            self.last_gain_text = ""
                            # carom trackers reset at shot start
                            if self.carom_mode:
                                self.carom_bounce_count = 0
                                self.carom_contacts = set()
                                self.carom_first_contact_bounces = None
                        self.aiming = False
                        self.aim_start = None
                        self.aim_end = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "GAME":
                            self.state = "MENU"
                        else:
                            running = False
                    if event.key == pygame.K_SPACE and self.state == "GAME":
                        # small debug: nudge all balls slightly
                        for ball in self.balls:
                            if not ball.in_pocket:
                                ball.vel += pygame.Vector2(random.uniform(-1,1), random.uniform(-1,1))

            # --- update/draw cycles (use your existing code) ---
            if self.state == "MENU":
                self.draw_menu()

            elif self.state == "GAME":
                self.screen.fill(BROWN)
                self.table.draw(self.screen)

                # Update and draw balls
                for ball in self.balls:
                    ball.update()

                self.check_collisions()

                for ball in self.balls:
                    ball.draw(self.screen)

                # Draw cue if needed
                self.draw_cue()

                # Draw UI buttons on top
                self.draw_buttons()

                # check if all balls stopped -> finalize shot combo / bonus OR carom success
                any_moving = any((not b.in_pocket) and (b.vel.length() > 0.01) for b in self.balls)
                if not any_moving and self.shot_in_progress:
                    # If carom map, evaluate contacts
                    if self.carom_mode:
                        # contacts list holds tuples (ball_number, bounce_count_at_contact)
                        # Convert set to list to access elements
                        contacts_list = list(self.carom_contacts)
                        
                        if len(contacts_list) >= 2:
                            # Sort by bounce count to get order of contact
                            contacts_list.sort(key=lambda x: x[1])
                            first_contact = contacts_list[0]
                            second_contact = contacts_list[1]
                            
                            # Get unique ball numbers contacted
                            unique_balls = set(c[0] for c in contacts_list)
                            
                            # Success requires both other balls (not cue) contacted
                            target_balls = set(b.number for b in self.balls if not b.is_cue and not b.in_pocket)
                            
                            if len(unique_balls) >= 2 and unique_balls >= target_balls:
                                # Check bounce requirements
                                bounces_before_second = second_contact[1] - first_contact[1]
                                ok = False
                                
                                if self.carom_mode == 'libre':
                                    ok = True  # No bounce requirement
                                elif self.carom_mode == 'one':
                                    ok = (bounces_before_second >= 1)  # At least 1 bounce between contacts
                                elif self.carom_mode == 'three':
                                    ok = (bounces_before_second >= 3)  # At least 3 bounces between contacts
                                
                                if ok:
                                    # Calculate points based on mode
                                    if self.carom_mode == 'libre':
                                        points = 1
                                    elif self.carom_mode == 'one':
                                        points = 20
                                    elif self.carom_mode == 'three':
                                        points = 50
                                    else:
                                        points = 1
                                    
                                    self.score += points
                                    self.last_gain_text = f"Carom Success +{points}"
                                    # mark level complete immediately
                                    self.level_options = self.level_manager.get_progression(self.table.map_type)
                                    self.state = "LEVEL_SELECT"
                                else:
                                    self.last_gain_text = f"Carom Failed - Need {3 if self.carom_mode == 'three' else 1} bounce(s)"
                            else:
                                self.last_gain_text = "Carom Failed - Must hit both balls"
                        else:
                            self.last_gain_text = "Carom Failed - Must hit both balls"
                    else:
                        # finish shot: give combo bonus if >1 ball pocketed this shot
                        if self.shot_pocketed_count > 1:
                            bonus = self.shot_pocketed_count * 5
                            self.score += bonus
                            self.last_gain_text = f"Combo x{self.shot_pocketed_count} +{bonus} pts"
                        elif self.shot_pocketed_count == 1:
                            # keep last_gain_text from pocketing
                            pass
                        # check level complete: all non-cue balls pocketed
                        noncue = [b for b in self.balls if not b.is_cue]
                        if noncue and all(b.in_pocket for b in noncue):
                            self.level_options = self.level_manager.get_progression(self.table.map_type)
                            self.state = "LEVEL_SELECT"

                    # reset shot tracking
                    self.shot_in_progress = False
                    self.shot_pocketed_count = 0
                    self.shot_score = 0
                    # reset carom trackers
                    self.carom_contacts = set()
                    self.carom_bounce_count = 0
                    self.carom_first_contact_bounces = None

                # Enhanced UI panels with modern design
                # Calculate safe zones (avoid buttons and table)
                button_bottom = 60 + 35  # Buttons end at y=95
                table_top = self.table.y  # Table starts here (felt area, excluding frame)
                table_bottom = self.table.y + self.table.height  # Table ends here
                score_panel_height = 130
                margin = 20  # Generous margin from table to avoid any overlap
                
                # Score panel (right side) - positioned to avoid table completely
                # Strategy: Try top, if not enough space, use bottom
                
                # Check space above table
                space_above = table_top - 10  # From screen top to table top
                
                if space_above >= score_panel_height + margin:
                    # Enough space above - place at top-right
                    score_panel_y = 10
                    # Double-check: panel bottom must be above table top with margin
                    panel_bottom = score_panel_y + score_panel_height
                    if panel_bottom > table_top - margin:
                        score_panel_y = table_top - score_panel_height - margin
                        score_panel_y = max(10, score_panel_y)  # Don't go above screen
                else:
                    # Not enough space above - place below table
                    # Priority: Must be below table with margin, then fit on screen
                    min_y_below_table = table_bottom + margin  # Minimum y to be below table
                    
                    # Check if we can fit below table
                    available_space_below = SCREEN_HEIGHT - min_y_below_table - 10
                    
                    if available_space_below >= score_panel_height:
                        # Enough space below table - place with margin
                        score_panel_y = min_y_below_table
                    elif available_space_below >= 80:
                        # Limited space - reduce panel height but keep it below table
                        score_panel_y = min_y_below_table
                        score_panel_height = available_space_below
                    else:
                        # Very limited space - place as far right as possible
                        # Place panel at edge, but ensure it's still below table
                        score_panel_y = max(min_y_below_table, SCREEN_HEIGHT - score_panel_height - 10)
                        # Final check: if still overlapping table, reduce height
                        if score_panel_y < table_bottom + margin:
                            score_panel_y = table_bottom + margin
                            score_panel_height = min(score_panel_height, SCREEN_HEIGHT - score_panel_y - 10)
                
                # Final verification: ensure panel doesn't overlap table
                panel_top = score_panel_y
                panel_bottom = score_panel_y + score_panel_height
                # Panel must be either completely above or completely below table
                if panel_bottom > table_top - margin and panel_top < table_bottom + margin:
                    # Panel overlaps table - force it below
                    score_panel_y = table_bottom + margin
                    # Recalculate panel bottom
                    panel_bottom = score_panel_y + score_panel_height
                    # If doesn't fit, reduce height
                    if panel_bottom > SCREEN_HEIGHT - 10:
                        score_panel_height = max(80, SCREEN_HEIGHT - score_panel_y - 10)
                
                # Ensure score_panel_height is at least minimum usable size
                score_panel_height = max(80, min(130, score_panel_height))
                
                # Create panel with final calculated dimensions
                score_panel = pygame.Surface((220, score_panel_height), pygame.SRCALPHA)
                score_panel.fill((0, 0, 0, 200))
                # Add border
                pygame.draw.rect(score_panel, GOLD, (0, 0, 220, score_panel_height), 2)
                self.screen.blit(score_panel, (SCREEN_WIDTH - 230, score_panel_y))
                
                # Score label with icon
                score_label = self.font_small.render("⭐ SCORE", True, SILVER)
                self.screen.blit(score_label, (SCREEN_WIDTH - 220, score_panel_y + 10))
                
                # Score value with formatting
                score_text = self.font_large.render(f"{self.score:,}", True, GOLD)
                self.screen.blit(score_text, (SCREEN_WIDTH - 220, score_panel_y + 30))
                
                # Last gain text with animation effect
                if self.last_gain_text:
                    lg = self.font_small.render(self.last_gain_text, True, (255, 240, 100))
                    # Add background for better visibility
                    lg_bg = pygame.Surface((lg.get_width() + 10, lg.get_height() + 4), pygame.SRCALPHA)
                    lg_bg.fill((0, 0, 0, 150))
                    self.screen.blit(lg_bg, (SCREEN_WIDTH - 220 - 5, score_panel_y + 85))
                    self.screen.blit(lg, (SCREEN_WIDTH - 220, score_panel_y + 87))
                
                # Game mode panel - positioned to avoid table overlap
                # Check if space below buttons is safe
                mode_panel_height = 80
                mode_panel_width = 250
                margin = 15
                
                # Try to place below buttons first
                preferred_y = button_bottom + 10
                preferred_bottom = preferred_y + mode_panel_height
                
                # Check if panel would overlap with table
                if preferred_bottom > table_top - margin:
                    # Panel would overlap table - move to bottom left
                    mode_panel_y = table_bottom + margin
                    # Ensure it fits on screen
                    if mode_panel_y + mode_panel_height > SCREEN_HEIGHT - 10:
                        mode_panel_y = SCREEN_HEIGHT - mode_panel_height - 10
                else:
                    # Safe to place below buttons
                    mode_panel_y = preferred_y
                
                # Final check: ensure no overlap with table
                panel_top = mode_panel_y
                panel_bottom = mode_panel_y + mode_panel_height
                if panel_bottom > table_top - margin and panel_top < table_bottom + margin:
                    # Still overlapping - force to bottom
                    mode_panel_y = table_bottom + margin
                    if mode_panel_y + mode_panel_height > SCREEN_HEIGHT - 10:
                        mode_panel_height = SCREEN_HEIGHT - mode_panel_y - 10
                
                mode_panel = pygame.Surface((mode_panel_width, mode_panel_height), pygame.SRCALPHA)
                mode_panel.fill((0, 0, 0, 200))
                pygame.draw.rect(mode_panel, SELECTED_COLOR, (0, 0, mode_panel_width, mode_panel_height), 2)
                self.screen.blit(mode_panel, (10, mode_panel_y))
                
                mode_names = ["Pool 8-Ball", "Snooker", "Carom"]
                mode_text = self.font_small.render(f"Mode: {mode_names[self.map_type-1]}", True, WHITE)
                self.screen.blit(mode_text, (20, mode_panel_y + 10))
                
                # Game mode specific stats (adjust position based on panel height)
                # Use proportional spacing that adapts to panel height
                text_spacing = max(20, mode_panel_height // 4)
                line1_y = mode_panel_y + text_spacing
                line2_y = mode_panel_y + text_spacing * 2
                
                if self.map_type == 1:  # Pool
                    if self.pool_player_group:
                        group_text = f"Group: {self.pool_player_group.upper()}"
                        group_label = self.font_small.render(group_text, True, SCORE_COLOR)
                        self.screen.blit(group_label, (20, line1_y))
                        
                        if mode_panel_height >= 60:  # Only show if enough space
                            remaining = 7 - (self.pool_solids_pocketed if self.pool_player_group == 'solid' else self.pool_stripes_pocketed)
                            remaining_text = self.font_small.render(f"Remaining: {remaining}", True, (200, 200, 200))
                            self.screen.blit(remaining_text, (20, line2_y))
                elif self.map_type == 2:  # Snooker
                    if mode_panel_height >= 60:  # Only show if enough space
                        reds_text = self.font_small.render(f"Reds left: {self.scoring.red_count}", True, RED)
                        self.screen.blit(reds_text, (20, line1_y))
                        
                        expect_text = "Expect: RED" if self.snooker_expecting_red else "Expect: COLOR"
                        expect_label = self.font_small.render(expect_text, True, SCORE_COLOR)
                        self.screen.blit(expect_label, (20, line2_y))
                elif self.map_type == 3:  # Carom
                    if mode_panel_height >= 50:  # Only show if enough space
                        mode_text_carom = f"Mode: {self.carom_mode.upper()}" if self.carom_mode else "Mode: LIBRE"
                        mode_label = self.font_small.render(mode_text_carom, True, SCORE_COLOR)
                        self.screen.blit(mode_label, (20, line1_y))
                
                # Prediction/Status panel (bottom left)
                if self.prediction:
                    pred_panel = pygame.Surface((max(300, self.font_small.size(self.prediction)[0] + 20), 50), pygame.SRCALPHA)
                    pred_panel.fill((0, 0, 0, 200))
                    pygame.draw.rect(pred_panel, (100, 255, 100), (0, 0, pred_panel.get_width(), 50), 2)
                    self.screen.blit(pred_panel, (10, SCREEN_HEIGHT - 60))
                    
                    pred_text = self.font_small.render(self.prediction, True, (200, 255, 200))
                    self.screen.blit(pred_text, (20, SCREEN_HEIGHT - 45))

            elif self.state == "LEVEL_SELECT":
                self.draw_level_select()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()