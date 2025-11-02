# Billiards Game

A 2D billiards game developed with Python and Pygame, supporting 3 game modes: Pool, Snooker, and Carom.

## 📋 Table of Contents

- [Overview](#overview)
- [How to Play](#how-to-play)
- [Directory Structure](#directory-structure)
- [Technologies Used](#technologies-used)
- [Installation and Running](#installation-and-running)
- [Game Mode Details](#game-mode-details)

---

## 🎮 Overview

Billiards Game is a billiards simulation game with 3 different game modes, each with its own rules and scoring system. The game features a physics system that simulates realistic collisions, friction, and reflections.

### Key Features:

- **3 Game Modes**: Pool (8-ball), Snooker, Carom
- **Realistic Physics**: Ball collisions, friction, table wall reflections
- **Scoring System**: Each mode has its own scoring system
- **Trajectory Preview**: Shows predicted ball path when aiming
- **Combo Bonus**: Bonus points for pocketing multiple balls in one shot
- **Level Management**: Automatically unlocks new levels upon completion

---

## 🎯 How to Play

### Basic Controls:

1. **Select Game Mode**: 
   - In the main menu, click "Map 1", "Map 2", or "Map 3" to select a mode
   - Click "Start" to begin

2. **Aiming and Shooting**:
   - Left-click anywhere when the cue ball is stationary
   - Hold and drag to adjust direction and power
   - Release to execute the shot
   - Drag length determines shot power (displayed on power bar)

3. **Trajectory Preview**:
   - While aiming, the game displays the predicted cue ball path (including wall reflections)
   - Gray dashed line shows the predicted trajectory

4. **Function Buttons**:
   - **Menu**: Return to main menu
   - **Reset**: Restart current level
   - **ESC**: Exit game or return to menu

### Game Rules by Mode:

#### Map 1: Pool (8-ball)
- **Objective**: Pocket all balls (except the cue ball)
- **Scoring**:
  - Balls 1-7 (Solid): 10 points each
  - Balls 9-15 (Stripe): 15 points each
  - Ball 8 (Black): 20 points
- **Combo Bonus**: +5 points for each additional ball when pocketing multiple balls in one shot
- **Completion**: When all balls (except cue ball) are pocketed

#### Map 2: Snooker
- **Objective**: Pot balls in order (red → color → red → color...)
- **Scoring**:
  - Red balls (number 1): 1 point each
  - Yellow (2): 2 points
  - Green (3): 3 points
  - Brown (4): 4 points
  - Blue (5): 5 points
  - Pink (6): 6 points
  - Black (7): 7 points
- **Rules**: Must pot a red ball first, then a color ball
- **Completion**: When all balls are pocketed

#### Map 3: Carom (Three Cushion)
- **Objective**: Hit the cue ball to contact both remaining balls in one shot
- **Modes**:
  - **Libre**: Just need to contact 2 balls (50 points)
  - **One cushion**: Must hit at least 1 cushion before contacting the second ball (not fully implemented)
  - **Three cushion**: Must hit at least 3 cushions before contacting the second ball (not fully implemented)
- **Features**: No pockets on the table, points only awarded for successful carom shots

---

## 📁 Directory Structure

```
game/
│
├── game bi-a.py           # Main game file
├── level_manager.py       # Manages progression and level unlocking
├── scoring_system.py      # Scoring system for different modes
├── README.md              # Documentation (this file)
│
├── maps/                   # Directory containing map configurations
│   ├── __init__.py        # Exports factory functions
│   ├── map2_snooker.py    # Snooker table configuration
│   └── map3_carom.py      # Carom table configuration
│
└── __pycache__/           # Python cache (auto-generated)
    ├── scoring_system.cpython-313.pyc
    └── level_manager.cpython-313.pyc
```

### File Descriptions:

- **`game bi-a.py`**: 
  - Main file containing all game logic
  - Classes: `Ball`, `Table`, `Game`
  - Handles: input, rendering, physics, collisions

- **`level_manager.py`**:
  - Class `LevelManager`: Manages progression
  - Determines which level unlocks after completing the current level

- **`scoring_system.py`**:
  - Class `ScoringSystem`: Scores for each game mode
  - Methods: `score_pool()`, `score_snooker()`, `score_carom()`

- **`maps/map2_snooker.py`**:
  - Function `create_snooker_map()`: Creates Snooker table configuration
  - Returns dict containing: width, height, pockets, balls, scoring function

- **`maps/map3_carom.py`**:
  - Function `create_carom_map()`: Creates Carom table configuration
  - Supports modes: 'libre', 'one', 'three'

---

## 🛠 Technologies Used

### Languages and Libraries:

1. **Python 3.13+**
   - Main programming language
   - Uses standard modules: `sys`, `math`, `random`

2. **Pygame**
   - Graphics and game development library
   - Handles: rendering, input, collision detection
   - Main module: `pygame`

### Python Modules Used:

```python
import pygame      # Game engine and graphics
import random      # Generate random numbers for ball colors
import math        # Mathematical calculations (hypot, vector operations)
import sys         # Program exit
```

### OOP Structure:

- **Class `Ball`**: 
  - Represents a billiard ball
  - Attributes: position, velocity, color, number, radius, mass
  - Methods: `update()`, `draw()`

- **Class `Table`**:
  - Represents the billiards table
  - Attributes: width, height, position, pockets, map_type
  - Methods: `setup_pockets()`, `draw()`

- **Class `Game`**:
  - Main class managing the entire game
  - Manages states: MENU, GAME, LEVEL_SELECT
  - Handles: input, collision, scoring, rendering

- **Class `LevelManager`**:
  - Manages progression between levels

- **Class `ScoringSystem`**:
  - Scores points based on game mode

### Physics Concepts Simulated:

1. **Friction**:
   - `FRICTION = 0.995`: Linear friction coefficient
   - Balls gradually lose velocity over time

2. **Ball-to-Ball Collisions**:
   - Uses impulse-based collision response
   - Restitution coefficient: `BALL_RESTITUTION = 0.98`
   - Calculations based on vectors and mass

3. **Ball-to-Wall Collisions**:
   - Reflection with energy loss coefficient: `WALL_BOUNCE_DAMP = 0.9`
   - Handles collisions with 4 table walls

4. **Trajectory Preview**:
   - Calculates trajectory with multiple reflections
   - Uses ray-casting to determine reflection points

---

## 🚀 Installation and Running

### System Requirements:

- Python 3.13 or higher
- Pygame library

### Installation Steps:

1. **Install Python**:
   - Download and install Python from [python.org](https://www.python.org/)

2. **Install Pygame**:
   ```bash
   pip install pygame
   ```

3. **Run the game**:
   ```bash
   python "game bi-a.py"
   ```
   Or:
   ```bash
   python game\ bi-a.py
   ```

### Notes:

- If you encounter file path errors, ensure you're in the project root directory
- Game runs at 800x600 resolution, adjustable in code

---

## 📖 Game Mode Details

### Map 1: Pool (8-ball)

**Table Configuration**:
- Size: 700x400 (default)
- 4 corner pockets

**Ball Layout**:
- 1 cue ball (white) at 25% left position
- 15 balls arranged in triangle at 70% right position
- Balls numbered 1-15

**Scoring System**:
- Base points according to ball number
- Combo bonus when pocketing multiple balls in one shot

### Map 2: Snooker

**Table Configuration**:
- Size: 760x460
- 6 pockets (4 corners + 2 middle pockets on top/bottom edges)

**Ball Layout**:
- 1 cue ball (white) at 20% table position
- 15 red balls in triangle at 72% table position
- 6 colored balls: Yellow (2), Green (3), Brown (4), Blue (5), Pink (6), Black (7)

**Special Rules**:
- Must pot red balls first, then color balls
- Colored balls should be respotted after potting (not yet implemented)

### Map 3: Carom

**Table Configuration**:
- Size: 760x460
- No pockets

**Ball Layout**:
- 3 balls: White (cue ball), Yellow (opponent ball), Red (target ball)

**Scoring**:
- Libre: +50 points when cue ball contacts both other balls
- One/three cushion modes not fully implemented

---

## 📝 Development Notes

### Features That Can Be Extended:

- [ ] Complete Carom one/three cushion modes
- [ ] Add animation when balls are pocketed
- [ ] Add sound effects for collisions and shots
- [ ] Support difficulty adjustment
- [ ] Add multiplayer mode
- [ ] Save high scores
- [ ] Add tutorial for each mode

### Adjustable Physics Constants:

- `FRICTION`: Adjust friction (default: 0.995)
- `INITIAL_SPEED`: Maximum shot speed (default: 40)
- `WALL_BOUNCE_DAMP`: Energy loss on wall bounce (default: 0.9)
- `BALL_RESTITUTION`: Coefficient of restitution between balls (default: 0.98)

---

## 📄 License

This game is developed for educational and entertainment purposes.

---

## 👨‍💻 Author

Developed by: [Author Name]

Created: 2024

---

**Enjoy playing! 🎱**


