import pygame
import random
import time
import sys
import subprocess
import json
import os

results = []  # Stores (sequence_name, red_press_count)
DATA_FILE = "/home/amosor/data/scores/results_storage_game_1.json"

def return_to_main_menu():
    print("Returning to main menu...")
    pygame.quit()

    # Relaucnh main.py
    subprocess.run(["python3", "main.py"])
    sys.exit()

# Initialize Pygame
pygame.init()

# Screen dimensions for the Raspberry Pi 7-inch touchscreen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 460
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Neurokinetic Reaction Test")

# Color palette
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)
BROWN = (165, 42, 42)

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

# Game settings
# Each sequence runs for 12 rounds
iterations_per_sequence = 12

# Store user reaction times
reaction_times = []

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

def run_sequence(sequence_name, reaction_time, num_squares=4):
    # Randomly select 10 out of 12 rounds where RED appears
    rounds_with_red = random.sample(range(iterations_per_sequence), 10)

    COLOR_POOL = [BLUE, GREEN, PURPLE, ORANGE, YELLOW, PINK, WHITE, GRAY, BROWN]
    
    # Track red presses
    red_press_count = 0

    # Choose squares based on sequence type
    squares = squares_4 if num_squares == 4 else squares_8
    square_count = len(squares)

    for iteration in range(iterations_per_sequence):
        if iteration in rounds_with_red:  # Ensure RED appears in this round
            available_colors = [RED]  # Start with RED
            remaining_colors = random.sample(COLOR_POOL, square_count - 1)
            available_colors.extend(remaining_colors)  # Fill remaining squares
        else:  # This round has no RED
            available_colors = random.sample(COLOR_POOL, square_count)

        random.shuffle(available_colors)  # Randomize order

        # Track which square actually has RED
        red_square_index = available_colors.index(RED) if RED in available_colors else None

        screen.fill(BLACK)  # Clear screen
        for i, square in enumerate(squares):
            pygame.draw.rect(screen, available_colors[i], square)

        pygame.display.flip()

        reaction_start_time = time.time()
        user_pressed = False

        # User has reaction_time seconds to react
        while time.time() - reaction_start_time < reaction_time:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    for i, square in enumerate(squares):
                        if square.collidepoint(x, y):
                            reaction_time_taken = time.time() - reaction_start_time
                            reaction_times.append(reaction_time_taken)

                            # Check if user clicked the ACTUAL RED square
                            if red_square_index is not None and i == red_square_index:
                                red_press_count += 1

                            print(f"{sequence_name} - Iteration {iteration + 1}: Reaction Time: {reaction_time_taken:.3f} sec (Clicked Red: {i == red_square_index})")
                            user_pressed = True
                            break
                if user_pressed:
                    break  # Exit waiting loop immediately

        # Show black screen for 2 seconds between iterations
        screen.fill(BLACK)
        pygame.display.flip()
        time.sleep(2)

    # Store results for the sequence
    results.append((sequence_name, red_press_count))


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


# Main program running
display_message("Game I:\nTouch this RED color\nas quickly and precisely as possible", RED, BLACK, 5)
run_sequence("Sequence 1", reaction_time=1)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 2", reaction_time=0.5)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 3", reaction_time=1, num_squares=8)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 4", reaction_time=0.5, num_squares=8)
display_message("END GAME", RED, BLACK, 2)
display_results_table()

# Instead of quitting, go back to main-menu
return_to_main_menu()
