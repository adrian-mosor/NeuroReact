import pygame
import random
import time
import serial
import os
import json

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 460
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game IV - Pressure Sensor")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
LIGHT_RED = (255, 102, 102)
DARK_RED = (153, 0, 0)

# Define serial port and baud rate for NodeMCU
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

# Pressure thresholds
SOFT_PRESS_MIN = 40
SOFT_PRESS_MAX = 100
HARD_PRESS_MIN = 101

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

# Define sequences
sequences = ["Sequence 1", "Sequence 2", "Sequence 3", "Sequence 4"]
results = []
DATA_FILE = "/home/amosor/data/scores/results_storage_game_4.json"

# Function to display messages
def display_message(text, bg_color, text_color, duration):
    screen.fill(bg_color)
    font = pygame.font.Font(None, 50)
    lines = text.split("\n")
    y_offset = SCREEN_HEIGHT // 2 - (len(lines) * 25)

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, text_color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 50))
        screen.blit(text_surface, text_rect)

    pygame.display.flip()
    time.sleep(duration)

# Function to get a pressure reading from serial
def read_pressure():
    try:
        line = ser.readline().decode().strip()
        return int(line) if line.isdigit() else 0
    except:
        return 0

# Function to run a sequence
def run_sequence(sequence_name, reaction_time, num_squares=4):
    correct = 0
    squares = squares_4 if num_squares == 4 else squares_8

    challenge_indices = sorted(random.sample(range(12), 10))
    dark_red_indices = set(random.sample(challenge_indices, k=5))

    for iteration in range(12):
        if iteration in challenge_indices:
            is_dark = iteration in dark_red_indices
            target_color = DARK_RED if is_dark else LIGHT_RED
        else:
            is_dark = None
            target_color = BLACK

        screen.fill(target_color)
        pygame.display.flip()

        start_time = time.time()
        responded = False

        while time.time() - start_time < reaction_time:
            pressure = read_pressure()
            if pressure:
                if is_dark is True and pressure > HARD_PRESS_MIN:
                    correct += 1
                    print(f"{sequence_name} - Iter {iteration+1}: DARK_RED, PRESS={pressure} - Correct")
                    responded = True
                    break
                elif is_dark is False and SOFT_PRESS_MIN <= pressure <= SOFT_PRESS_MAX:
                    correct += 1
                    print(f"{sequence_name} - Iter {iteration+1}: LIGHT_RED, PRESS={pressure} - Correct")
                    responded = True
                    break
                elif is_dark is not None:
                    # Wrong pressure but color was valid
                    print(f"{sequence_name} - Iter {iteration+1}: Wrong PRESS={pressure} for {'DARK_RED' if is_dark else 'LIGHT_RED'}")
                    responded = True  # Still counts as a response, just incorrect
                    break
                else:
                    # Color was BLACK or invalid, this iteration is not scorable
                    print(f"{sequence_name} - Iter {iteration+1}: PRESS={pressure} ignored (No valid RED color shown)")
                    responded = True
                    break

        if not responded:
            if is_dark is not None:
                print(f"{sequence_name} - Iter {iteration+1}: No input - Missed opportunity for {'DARK_RED' if is_dark else 'LIGHT_RED'}")
            else:
                print(f"{sequence_name} - Iter {iteration+1}: (SKIPPED) No DARK_RED or LIGHT_RED shown")


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

# Run the game
display_message("Game IV:\nPress SOFT for LIGHT RED\nPress HARD for DARK RED", WHITE, BLACK, 5)
run_sequence("Sequence 1", 1)
display_message("Next Level", WHITE, BLACK, 2)
run_sequence("Sequence 2", 0.5)
display_message("Next Level", WHITE, BLACK, 2)
run_sequence("Sequence 3", 1)
display_message("Next Level", WHITE, BLACK, 2)
run_sequence("Sequence 4", 0.5)
display_message("END GAME", WHITE, BLACK, 2)
display_results_table()
pygame.quit()

