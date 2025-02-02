import pygame
import random
import time
import sys
import subprocess

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
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
PINK = (255, 105, 180)
WHITE = (255, 255, 255)
GRAY = (169, 169, 169)
BROWN = (165, 42, 42)
TEAL = (0, 128, 128)

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
    # Randomly select 10 out of 12 rounds to have red
    rounds_with_red = random.sample(range(iterations_per_sequence), 10)

    COLOR_POOL = [BLUE, GREEN, PURPLE, ORANGE, CYAN, YELLOW, PINK, WHITE, GRAY, BROWN, TEAL]

    # Choose squares based on sequence type
    squares = squares_4 if num_squares == 4 else squares_8
    square_count = len(squares)

    for iteration in range(iterations_per_sequence):
        if iteration in rounds_with_red:
            # Ensure RED appears in this round
            available_colors = [RED]
            remaining_colors = random.sample(COLOR_POOL, square_count - 1)

            # Fill remaining squares
            available_colors.extend(remaining_colors)
        else:
            # This round has no RED
            available_colors = random.sample(COLOR_POOL, square_count)

        # Randomize order for sequence
        random.shuffle(available_colors)

        # Randomize order
        screen.fill(BLACK)
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
                            print(f"{sequence_name} - Iteration {iteration + 1}: Reaction Time: {reaction_time_taken:.3f} sec (Red: {iteration in rounds_with_red})")
                            user_pressed = True
                            break
                if user_pressed:
                    # Exit waiting loop immediately
                    break

        # Display "Next Level" after each iteration
        display_message("Next Level", RED, BLACK, 2)

    display_message("[DEBUG] Next Sequence", RED, BLACK, 1)

display_message("Game I:\nTouch this RED color\nas quickly and precisely as possible", RED, BLACK, 5)

run_sequence("Sequence 1", reaction_time=1)
run_sequence("Sequence 2", reaction_time=0.5)
run_sequence("Sequence 3", reaction_time=1, num_squares=8)
run_sequence("Sequence 4", reaction_time=0.5, num_squares=8)

# Instead of quitting, go back to main-menu
return_to_main_menu()
