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
DATA_FILE = "/home/amosor/data/scores/results_storage_game_2.json"

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
        elif GREEN not in available_colors:
            print(f"{sequence_name} - Iteration {iteration + 1}: Green was not in iteration")

        # Black screen for 2 seconds between iterations
        screen.fill(BLACK)
        pygame.display.flip()
        time.sleep(2)

    # Store results
    results.append((sequence_name, correct_calls))

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
