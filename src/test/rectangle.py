import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions (adjust to your LCD size)
screen_width = 800
screen_height = 480  # Adjust based on your screen dimensions

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Simple Geometric Shape Display")

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Rectangle properties
rect_width = 150
rect_height = 100

# Center the rectangle
rect_x = (screen_width - rect_width) // 2

 # Center the rectangles
rect_y = (screen_height - rect_height) // 2 

# Main loop flag
running = True

# Main loop
while running:
    screen.fill(WHITE)  # Clear screen with white background

    # Draw a rectangle
    pygame.draw.rect(screen, BLUE, (rect_x, rect_y, rect_width, rect_height))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the rectangle was clicked
            mouse_x, mouse_y = event.pos
            if rect_x <= mouse_x <= rect_x + rect_width and rect_y <= mouse_y <= rect_y + rect_height:
                print("Rectangle pressed!")

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()

