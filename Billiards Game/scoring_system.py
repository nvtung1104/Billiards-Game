class ScoringSystem:
    def __init__(self, game_mode=1):
        self.game_mode = game_mode
        self.current_score = 0
        self.current_break = 0  # For tracking consecutive points
        self.red_count = 15  # For snooker
        self.last_red = False  # Track if last ball was red in snooker
        self.carom_cushions = 0  # Track cushion hits for carom
        self.carom_contacts = []  # Track ball contacts for carom

    def score_pool(self, ball_number):
        """Map 1: 8-Ball Pool scoring
        - Balls 1-7: Solids (10 points each)
        - Balls 9-15: Stripes (15 points each)
        - Ball 8: 20 points if all others of player's type are pocketed
        """
        if ball_number == 8:
            return 20
        elif 1 <= ball_number <= 7:  # Solids
            return 10
        elif 9 <= ball_number <= 15:  # Stripes 
            return 15
        return 0

    def score_snooker(self, ball_number):
        """Map 2: Snooker scoring
        - Red balls: 1 point each (ball_number == 1)
        - Yellow: 2 points (ball_number == 2)
        - Green: 3 points
        - Brown: 4 points  
        - Blue: 5 points
        - Pink: 6 points
        - Black: 7 points
        Must alternate red then color
        """
        if ball_number == 1:  # Red
            self.red_count -= 1
            self.last_red = True
            return 1
        elif 2 <= ball_number <= 7:  # Colors
            if not self.last_red and self.red_count > 0:
                return 0  # Invalid - must pot red first
            self.last_red = False
            return ball_number
        return 0

    def score_carom(self, cushions_hit, ball_contacts):
        """Map 3: Carom billiards scoring
        libre: 10 points for hitting both other balls
        one cushion: 20 points if hit cushion before second ball
        three cushion: 50 points if hit 3 cushions before second ball
        """
        if len(ball_contacts) < 2:
            return 0
            
        if self.game_mode == 'libre':
            return 10
        elif self.game_mode == 'one' and cushions_hit >= 1:
            return 20
        elif self.game_mode == 'three' and cushions_hit >= 3:
            return 50
        return 0

    def reset(self):
        self.current_score = 0
        self.current_break = 0
        self.red_count = 15
        self.last_red = False
        self.carom_cushions = 0
        self.carom_contacts = []