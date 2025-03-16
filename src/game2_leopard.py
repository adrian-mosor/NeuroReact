import pygame
import random
import time
import subprocess
import pvleopard

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 460
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game II - Microphone")

# Define colors
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

COLOR_POOL = [BLACK, RED, BLUE, PURPLE, ORANGE, YELLOW, PINK, WHITE, GRAY, BROWN]  # GREEN added separately

# Square positions for 4 and 8 squares
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
    pygame.Rect(0, 0, square_width_8, square_height_8),
    pygame.Rect(square_width_8, 0, square_width_8, square_height_8),
    pygame.Rect(square_width_8 * 2, 0, square_width_8, square_height_8),
    pygame.Rect(square_width_8 * 3, 0, square_width_8, square_height_8),
    pygame.Rect(0, square_height_8, square_width_8, square_height_8),
    pygame.Rect(square_width_8, square_height_8, square_width_8, square_height_8),
    pygame.Rect(square_width_8 * 2, square_height_8, square_width_8, square_height_8),
    pygame.Rect(square_width_8 * 3, square_height_8, square_width_8, square_height_8)
]

# Setup Picovoice Leopard
ACCESS_KEY = "+m8fc6ADaXGrBFjP2UEOpS9HZ+YxwEf80KobBbRfSytCwNELN6iOIw=="
leopard = pvleopard.create(access_key=ACCESS_KEY)

# Store results
results = []

# Function to display messages
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
def run_sequence(sequence_name, reaction_time, num_squares):
    squares = squares_4 if num_squares == 4 else squares_8
    correct_calls = 0

    # Select 6 iterations for GREEN
    green_positions = random.sample(range(12), 6)

    for iteration in range(12):
        available_colors = random.sample(COLOR_POOL, num_squares)

        # Ensure GREEN appears in 6 iterations
        if iteration in green_positions:
            replace_index = random.randint(0, num_squares - 1)
            available_colors[replace_index] = GREEN
            random.shuffle(available_colors)

        # Draw squares
        screen.fill(BLACK)
        for i, square in enumerate(squares):
            pygame.draw.rect(screen, available_colors[i], square)
        pygame.display.flip()

        # Record speech
        audio_path = "/tmp/speech.wav"
        subprocess.run(["arecord", "-D", "hw:4,0", "-f", "S16_LE", "-r", "16000", "-c", "2", "-d", "3", audio_path])

        # Transcribe speech
        transcribed_text, _ = leopard.process_file(audio_path)
        print(f"You said: {transcribed_text}")

        # Check if the user correctly said "RED" when GREEN was shown
        if GREEN in available_colors and "red" in transcribed_text.lower():
            correct_calls += 1
            print(f"{sequence_name} - Iteration {iteration + 1}: Correct!")
        elif GREEN in available_colors:
            print(f"{sequence_name} - Iteration {iteration + 1}: Incorrect!")

        # Black screen for 2 seconds between iterations
        screen.fill(BLACK)
        pygame.display.flip()
        time.sleep(2)

    # Store results
    results.append((sequence_name, correct_calls))

# Function to display results table
def display_results_table():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 40)

    title_text = font.render("Game II – Results", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

    for idx, (sequence_name, correct_count) in enumerate(results):
        row_y = 150 + (idx * 50)
        seq_text = font.render(sequence_name, True, BLACK)
        screen.blit(seq_text, (100, row_y))

        nominal_text = font.render(f"{correct_count} from 6", True, BLACK)
        screen.blit(nominal_text, (300, row_y))

        percent_text = font.render(f"{(correct_count / 6) * 100:.1f}%", True, BLACK)
        screen.blit(percent_text, (500, row_y))

    pygame.display.flip()
    time.sleep(10)

# Run the game
display_message("Game II:\nSay RED when you see GREEN", RED, BLACK, 5)
run_sequence("Sequence 1", reaction_time=1, num_squares=4)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 2", reaction_time=0.5, num_squares=4)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 3", reaction_time=1, num_squares=8)
display_message("Next Level", RED, BLACK, 2)
run_sequence("Sequence 4", reaction_time=0.5, num_squares=8)
display_results_table()

# Quit Pygame
pygame.quit()
