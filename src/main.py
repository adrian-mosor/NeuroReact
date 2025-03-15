import os
import pygame
import subprocess
import sys
import time
import signal

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
GRAY = (169, 169, 169)

# Define button dimensions
button_width = 400
button_height = 100
button_x = (SCREEN_WIDTH - button_width) // 2
button_y_start = (SCREEN_HEIGHT // 2) - 60  # Adjusted for two buttons
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

# Allow CTRL+C to work
def handle_exit(sig, frame):
    print("\nExiting application...")
    pygame.quit()
    os._exit(0)  # Ensures the process fully terminates

signal.signal(signal.SIGINT, handle_exit)  # Enable CTRL+C exit

# Main loop
running = True
while running:
    screen.fill(WHITE)  # Background color

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
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if start_button_rect.collidepoint(x, y):
                print("Launching Game 1...")
                
                # Show loading screen
                show_loading_screen()
                pygame.display.update()
                
                # Launch game asynchronously and keep loading screen until it starts
                game_process = subprocess.Popen(["python3", "game1.py"])
                
                # Wait until the game process is running
                while game_process.poll() is None:  # While the game is running
                    time.sleep(0.5)  # Wait before checking again

                # Quit only after game1.py has fully launched
                running = False

            elif exit_button_rect.collidepoint(x, y):
                handle_exit(None, None)

pygame.quit()
