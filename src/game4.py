import pygame
import random
import time
import serial
import subprocess
import json
import os
import sys

# Game result storage
results = []
DATA_FILE = "/home/amosor/data/scores/results_storage_game_4.json"

# Setup serial connection to ESP8266
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Return to main menu
def return_to_main_menu():
    print("Returning to main menu...")
    pygame.quit()
    subprocess.run(["python3", "main.py"])
    sys.exit()

# Initialize Pygame
pygame.init()

# Screen dimensions for the Raspberry Pi 7-inch touchscreen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 460
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game IV – Pressure Sensor")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)
GRAY = (169, 169, 169)
BROWN = (165, 42, 42)
LIGHT_RED = (255, 102, 102)
DARK_RED = (153, 0, 0)
COLOR_POOL = [RED, BLUE, GREEN, PURPLE, ORANGE, YELLOW, PINK, GRAY, BROWN]

# Pressure thresholds
SOFT_PRESS_MIN = 25
SOFT_PRESS_MAX = 80
HARD_PRESS_MIN = 81

# Define square positions for 4 squares (first two sequences of the game - seq. 1,2)
square_width_4 = SCREEN_WIDTH // 2
square_height_4 = SCREEN_HEIGHT // 2
squares_4 = [
    pygame.Rect(0, 0, square_width_4, square_height_4),  # Top-left
    pygame.Rect(square_width_4, 0, square_width_4, square_height_4),  # Top-right
    pygame.Rect(0, square_height_4, square_width_4, square_height_4),  # Bottom-left
    pygame.Rect(square_width_4, square_height_4, square_width_4, square_height_4),  # Bottom-right
]

# Define square positions for 8 squares (last two sequences of the game - seq. 3,4)
square_width_8 = SCREEN_WIDTH // 4
square_height_8 = SCREEN_HEIGHT // 2
squares_8 = [
    pygame.Rect(0, 0, square_width_8, square_height_8),  # Top-left 1
    pygame.Rect(square_width_8, 0, square_width_8, square_height_8),  # Top-left 2
    pygame.Rect(square_width_8 * 2, 0, square_width_8, square_height_8),  # Top-right 1
    pygame.Rect(square_width_8 * 3, 0, square_width_8, square_height_8),  # Top-right 2
    pygame.Rect(0, square_height_8, square_width_8, square_height_8),  # Bottom-left 1
    pygame.Rect(square_width_8, square_height_8, square_width_8, square_height_8),  # Bottom-left 2
    pygame.Rect(square_width_8 * 2, square_height_8, square_width_8, square_height_8),  # Bottom-right 1
    pygame.Rect(square_width_8 * 3, square_height_8, square_width_8, square_height_8),  # Bottom-right 2
]


def display_message(text, bg_color, text_color, duration):
    screen.fill(bg_color)
    font = pygame.font.Font(None, 50)

    # Manually split text into multiple lines
    lines = text.split("\n")

    # Calculate vertical positioning
    # Adjust to center text
    y_offset = SCREEN_HEIGHT // 2 - (len(lines) * 25)

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, text_color)
        # Space out lines
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 50))
        screen.blit(text_surface, text_rect)

    # Update entire screen with latest changes
    pygame.display.flip()
    time.sleep(duration)

def read_pressure():
    try:
        line = ser.readline().decode().strip()
        return int(line) if line.isdigit() else 0
    except:
        return 0

def run_sequence(sequence_name, reaction_time, num_squares=4):
    correct = 0
    squares = squares_4 if num_squares == 4 else squares_8
    square_count = len(squares)

    challenge_indices = sorted(random.sample(range(12), 10))
    dark_red_indices = set(random.sample(challenge_indices, k=5))

    for iteration in range(12):
        if iteration in challenge_indices:
            is_dark = iteration in dark_red_indices
            red_color = DARK_RED if is_dark else LIGHT_RED
            available_colors = [red_color] + random.sample([BLUE, GREEN, PURPLE, ORANGE, YELLOW, PINK, GRAY, BROWN], square_count - 1)
        else:
            is_dark = None
            available_colors = random.sample([BLUE, GREEN, PURPLE, ORANGE, YELLOW, PINK, GRAY, BROWN], square_count)

        random.shuffle(available_colors)

        # Draw the squares
        screen.fill(BLACK)
        for i, square in enumerate(squares):
            pygame.draw.rect(screen, available_colors[i], square)
        pygame.display.flip()

        # Track max pressure during the window
        start_time = time.time()
        max_pressure = 0

        while time.time() - start_time < reaction_time:
            pressure = read_pressure()
            if pressure > max_pressure:
                max_pressure = pressure
            #time.sleep(0.01)

        # Evaluate pressure only if it was a valid challenge round
        if is_dark is True:
            if max_pressure > HARD_PRESS_MIN:
                correct += 1
                print(f"{sequence_name} - Iter {iteration+1}: DARK_RED, Max PRESS={max_pressure} - CORRECT")
            else:
                print(f"{sequence_name} - Iter {iteration+1}: DARK_RED, Max PRESS={max_pressure} - INCORRECT")
        elif is_dark is False:
            if SOFT_PRESS_MIN <= max_pressure <= SOFT_PRESS_MAX:
                correct += 1
                print(f"{sequence_name} - Iter {iteration+1}: LIGHT_RED, Max PRESS={max_pressure} - CORRECT")
            else:
                print(f"{sequence_name} - Iter {iteration+1}: LIGHT_RED, Max PRESS={max_pressure} - INCORRECT")
        else:
            print(f"{sequence_name} - Iter {iteration+1}: (SKIPPED) No RED shown - Max PRESS={max_pressure}")

        # Pause between iterations
        screen.fill(BLACK)
        pygame.display.flip()
        time.sleep(2)

    results.append((sequence_name, correct))


def display_results_table():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 24)

    # Load saved data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            past_data = json.load(f)
    else:
        past_data = {}

    # Update saved results
    for sequence_name, red_count in results:
        percent = (red_count / 10) * 100
        if sequence_name not in past_data:
            past_data[sequence_name] = {"previous": [], "best": 0.0}
        past_data[sequence_name]["previous"].insert(0, percent)
        past_data[sequence_name]["previous"] = past_data[sequence_name]["previous"][:3]
        past_data[sequence_name]["best"] = max(past_data[sequence_name]["best"], percent)

    with open(DATA_FILE, "w") as f:
        json.dump(past_data, f, indent=4)

    # Headers
    headers = ["NOW", "Nominal", "%", "PREV #1", "PREV #2", "PREV #3", "BEST"]
    x_positions = [10, 120, 210, 290, 370, 450, 530]

    for i, header in enumerate(headers):
        screen.blit(font.render(header, True, BLACK), (x_positions[i], 30))

    # Rows
    for idx, (sequence_name, red_count) in enumerate(results):
        row_y = 70 + idx * 40
        percent = (red_count / 10) * 100
        prev = past_data[sequence_name]["previous"]
        best = past_data[sequence_name]["best"]

        screen.blit(font.render(sequence_name, True, BLACK), (x_positions[0], row_y))
        screen.blit(font.render(f"{red_count} from 10", True, BLACK), (x_positions[1], row_y))
        screen.blit(font.render(f"{percent:.1f}%", True, BLACK), (x_positions[2], row_y))

        for j in range(3):
            val = f"{prev[j]:.1f}%" if j < len(prev) else "-"
            screen.blit(font.render(val, True, BLACK), (x_positions[3 + j], row_y))

        screen.blit(font.render(f"{best:.1f}%", True, BLACK), (x_positions[6], row_y))

    pygame.display.flip()
    time.sleep(10)


# Run Game IV
display_message("Game IV:\nPress SOFT for LIGHT RED\nPress HARD for DARK RED", RED, BLACK, 5)
run_sequence("Sequence 1", 1, num_squares=4)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 2", 0.5, num_squares=4)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 3", 1, num_squares=8)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 4", 0.5, num_squares=8)
display_message("END GAME", RED, BLACK, 2)
display_results_table()

# Instead of quitting, go back to main-menu
return_to_main_menu()
