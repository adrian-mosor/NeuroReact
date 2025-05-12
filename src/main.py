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

# Define button dimensions and positions
button_width = 400
button_height = 70
button_x = (SCREEN_WIDTH - button_width) // 2

# Vertical spacing between buttons
spacing = 20
start_y = (SCREEN_HEIGHT - (5 * button_height + 4 * spacing)) // 2

button_y_game1 = start_y
button_y_game2 = button_y_game1 + button_height + spacing
button_y_game3 = button_y_game2 + button_height + spacing
button_y_game4 = button_y_game3 + button_height + spacing
button_y_exit  = button_y_game4 + button_height + spacing

# Define buttons
rect_game1 = pygame.Rect(button_x, button_y_game1, button_width, button_height)
rect_game2 = pygame.Rect(button_x, button_y_game2, button_width, button_height)
rect_game3 = pygame.Rect(button_x, button_y_game3, button_width, button_height)
rect_game4 = pygame.Rect(button_x, button_y_game4, button_width, button_height)
rect_exit  = pygame.Rect(button_x, button_y_exit,  button_width, button_height)

# Font setup
font = pygame.font.Font(None, 50)

# Function to draw text
def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to show loading screen
def show_loading_screen():
    screen.fill(WHITE)
    draw_text("Loading...", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, BLACK)
    pygame.display.flip()

# Track subprocess
game_process = None

# Handle Ctrl+C
def handle_exit(sig, frame):
    global game_process
    print("\nExiting application...")
    if game_process and game_process.poll() is None:
        game_process.terminate()
        game_process.wait()
    pygame.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

# Launch game
def launch_game(game_script):
    global game_process
    print(f"Launching {game_script}...")
    game_process = subprocess.Popen(["python3", game_script], stdin=None, stdout=None, stderr=None, close_fds=True)

# Main loop
running = True
while running:
    screen.fill(WHITE)

    # Draw buttons
    pygame.draw.rect(screen, RED, rect_game1)
    pygame.draw.rect(screen, RED, rect_game2)
    pygame.draw.rect(screen, RED, rect_game3)
    pygame.draw.rect(screen, RED, rect_game4)
    pygame.draw.rect(screen, DARK_RED, rect_exit)

    # Button labels
    draw_text("Start Game 1", SCREEN_WIDTH // 2, rect_game1.centery, BLACK)
    draw_text("Start Game 2", SCREEN_WIDTH // 2, rect_game2.centery, BLACK)
    draw_text("Start Game 3", SCREEN_WIDTH // 2, rect_game3.centery, BLACK)
    draw_text("Start Game 4", SCREEN_WIDTH // 2, rect_game4.centery, BLACK)
    draw_text("Exit",         SCREEN_WIDTH // 2, rect_exit.centery, WHITE)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            handle_exit(None, None)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if rect_game1.collidepoint(x, y):
                launch_game("game1.py")
            elif rect_game2.collidepoint(x, y):
                launch_game("game2_leopard.py")
            elif rect_game3.collidepoint(x, y):
                launch_game("game3.py")
            elif rect_game4.collidepoint(x, y):
                launch_game("game4.py")
            elif rect_exit.collidepoint(x, y):
                handle_exit(None, None)

pygame.quit()
