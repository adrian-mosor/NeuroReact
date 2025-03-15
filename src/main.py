import os
import signal
import pygame
import subprocess
import sys
import time

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 460
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Neurokinetic Reaction Test - Main Menu")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)

# Define button dimensions
button_width = 400
button_height = 100
button_x = (SCREEN_WIDTH - button_width) // 2
button_y_start = (SCREEN_HEIGHT // 2) - 60
button_y_exit = (SCREEN_HEIGHT // 2) + 60

# Define buttons
start_button_rect = pygame.Rect(button_x, button_y_start, button_width, button_height)
exit_button_rect = pygame.Rect(button_x, button_y_exit, button_width, button_height)

# Font setup
font = pygame.font.Font(None, 50)

# Function to draw text
def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to show loading screen before launching the game
def show_loading_screen():
    screen.fill(WHITE)
    draw_text("Loading...", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BLACK)
    pygame.display.flip()

# Track the subprocess
game_process = None

# Function to handle Ctrl+C and cleanly exit both processes
def handle_exit(sig, frame):
    global game_process
    print("\nExiting application...")
    
    if game_process and game_process.poll() is None:
        game_process.terminate()  # Kill game1.py if it's running
        game_process.wait()  # Ensure it fully stops
    
    pygame.quit()
    sys.exit(0)  # Fully terminate

# Allow Ctrl+C to work
signal.signal(signal.SIGINT, handle_exit)

# Main loop
running = True
while running:
    screen.fill(WHITE)

    # Draw buttons
    pygame.draw.rect(screen, RED, start_button_rect)
    pygame.draw.rect(screen, DARK_RED, exit_button_rect)

    # Draw text
    draw_text("Start Game 1", SCREEN_WIDTH // 2, button_y_start + button_height // 2, BLACK)
    draw_text("Exit", SCREEN_WIDTH // 2, button_y_exit + button_height // 2, WHITE)

    pygame.display.flip()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            handle_exit(None, None)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if start_button_rect.collidepoint(x, y):
                print("Launching Game 1...")

                # Show loading screen
                show_loading_screen()
                pygame.display.update()

                # Launch game1.py as a separate process in the background
                game_process = subprocess.Popen(["python3", "game1.py"])

            elif exit_button_rect.collidepoint(x, y):
                handle_exit(None, None)

pygame.quit()
