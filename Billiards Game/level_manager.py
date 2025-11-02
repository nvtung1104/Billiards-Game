class LevelManager:
    def __init__(self, max_map=3):
        self.max_map = max_map

    def get_progression(self, current_map):
        if current_map == 1:
            return [m for m in range(2, self.max_map + 1)]
        next_map = current_map + 1
        if next_map <= self.max_map:
            return [next_map]
        return [1]