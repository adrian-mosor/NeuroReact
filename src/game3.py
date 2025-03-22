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

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 460
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game III - Speaker")

# Define colors (Removed TEAL and CYAN)
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

# Color list for random selection
COLOR_POOL = [RED, BLUE, GREEN, PURPLE, ORANGE, YELLOW, PINK, GRAY, BROWN]

# Map colors to their spoken names
COLOR_NAMES = {
    RED: "red",
    BLUE: "blue",
    GREEN: "green",
    PURPLE: "purple",
    ORANGE: "orange",
    YELLOW: "yellow",
    PINK: "pink",
    GRAY: "gray",
    BROWN: "brown"
}

# Define square positions (4 squares for first 2 sequences, 8 for last 2)
square_width_4 = SCREEN_WIDTH // 2
square_height_4 = SCREEN_HEIGHT // 2
squares_4 = [
    pygame.Rect(0, 0, square_width_4, square_height_4),
    pygame.Rect(square_width_4, 0, square_width_4, square_height_4),
    pygame.Rect(0, square_height_4, square_width_4, square_height_4),
    pygame.Rect(square_width_4, square_height_4, square_width_4, square_height_4)
]

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

# Store results
results = []

# Function to play color sound
def play_color(color):
    subprocess.run(["espeak", color.lower()], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Function to display text messages
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

# Function to run a sequence
def run_sequence(sequence_name, reaction_time, num_squares=4):
    # Choose squares based on sequence type
    squares = squares_4 if num_squares == 4 else squares_8
    square_count = len(squares)

    # Track correct presses
    correct_presses = 0

    # Select 4 out of 12 iterations where BLUE → YELLOW should appear
    blue_yellow_indices = random.sample(range(12), 4)  # Pick 4 random iterations

    for iteration in range(12):
        # Select colors ensuring enough unique entries
        available_colors = random.sample(COLOR_POOL, square_count)

        if iteration in blue_yellow_indices:
            spoken_color = BLUE
            target_color = YELLOW  # The correct response is pressing YELLOW
            if YELLOW not in available_colors:
                replace_index = random.randint(0, len(available_colors) - 1)
                available_colors[replace_index] = YELLOW  # Replace a random color with YELLOW
        else:
            spoken_color = random.choice(available_colors)  # Pick a random color from displayed ones
            target_color = spoken_color  # The correct response is pressing the spoken color itself

        random.shuffle(available_colors)  # Shuffle displayed colors
        spoken_color_name = COLOR_NAMES[spoken_color]  # Convert spoken color to string

        # Play the spoken color
        play_color(spoken_color_name)

        # Draw the colors on screen
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

                            # Get the actual color the user pressed
                            pressed_color = available_colors[i]
                            pressed_color_name = COLOR_NAMES.get(pressed_color, "unknown")

                            # Check if the correct square was pressed
                            if spoken_color == BLUE and pressed_color == YELLOW:
                                correct_presses += 1
                                print(f"{sequence_name} - Iteration {iteration + 1}: Correct! (Spoken: BLUE, Pressed: YELLOW)")
                            else:
                                print(f"{sequence_name} - Iteration {iteration + 1}: Incorrect! (Spoken: {spoken_color_name}, Pressed: {pressed_color_name})")

                            user_pressed = True
                            break
                if user_pressed:
                    break  # Exit waiting loop

        # Show black screen for 2 seconds between iterations
        screen.fill(BLACK)
        pygame.display.flip()
        time.sleep(2)

    # Store results
    results.append((sequence_name, correct_presses))

# Function to display results table
def display_results_table():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 40)

    # Display title
    title_text = font.render("Game III – Results", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    # Display results per sequence
    for idx, (sequence_name, correct_count) in enumerate(results):
        row_y = 150 + (idx * 50)

        seq_text = font.render(sequence_name, True, BLACK)
        screen.blit(seq_text, (100, row_y))

        nominal_text = font.render(f"{correct_count} from 10", True, BLACK)
        screen.blit(nominal_text, (300, row_y))

        percent_text = font.render(f"{(correct_count / 10) * 100:.1f}%", True, BLACK)
        screen.blit(percent_text, (500, row_y))

    pygame.display.flip()
    time.sleep(10)

# Main program running
display_message("Game III:\nListen and Click the Correct Color", RED, BLACK, 5)
run_sequence("Sequence 1", reaction_time=1, num_squares=4)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 2", reaction_time=0.5, num_squares=4)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 3", reaction_time=1, num_squares=8)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 4", reaction_time=0.5, num_squares=8)
display_results_table()

# Return to Main Menu
pygame.quit()

# Instead of quitting, go back to main-menu -- TO DO: when merging menu from game1 to develop
# return_to_main_menu()