import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Memory Match Game")

# Game state variables
click_count = 0  # Number of clicks
start_time = pygame.time.get_ticks()  # Start time of the game
hi_score = 0  # Placeholder for Hi-score (can be updated with persistent storage if needed)
game_completed = False  # Track if the game is completed
total_time_taken = 0  # Store the total time taken when the game ends
last_flip_time = 0  # Stores time of last flip
delay = 500  # Delay in milliseconds between flips

# Colors
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Font for the banner
font = pygame.font.Font(None, 50)
banner_height = 60

# Card dimensions and layout
CARD_WIDTH = 100
CARD_HEIGHT = 150
MARGIN = 20
COLS = 4
ROWS = 3
TOTAL_CARDS = COLS * ROWS

# Load images
images = []
for i in range(1, TOTAL_CARDS // 2 + 1):
    try:
        image = pygame.image.load(f"image{i}.jpg")
        image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
        images.append(image)
    except pygame.error:
        print(f"Error loading image{i}.jpg. Make sure it exists in the same directory.")
        pygame.quit()
        exit()

# Duplicate images to create pairs
all_images = images * 2
random.shuffle(all_images)

# Create card rectangles
cards = []
flipped = [False] * TOTAL_CARDS
matched = [False] * TOTAL_CARDS
flipped_indices = []

# Functions
def draw_banner():
    """Draw the banner at the top of the screen."""
    pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, banner_height))
    text_surface = font.render("Memory Match Game", True, WHITE)
    text_x = (WIDTH - text_surface.get_width()) // 2
    text_y = (banner_height - text_surface.get_height()) // 2
    screen.blit(text_surface, (text_x, text_y))

def calculate_card_positions():
    """Calculate the positions of the image cards."""
    global cards
    cards = []
    card_area_width = int(WIDTH * 0.7)
    card_area_height = HEIGHT - banner_height
    card_width = (card_area_width - (COLS + 1) * MARGIN) // COLS
    card_height = (card_area_height - (ROWS + 1) * MARGIN) // ROWS
    x_margin = MARGIN
    y_margin = banner_height + MARGIN

    for row in range(ROWS):
        for col in range(COLS):
            x = col * (card_width + MARGIN) + x_margin
            y = row * (card_height + MARGIN) + y_margin
            cards.append(pygame.Rect(x, y, card_width, card_height))

def calculate_scoring_cards():
    """Calculate the positions of the scoring cards."""
    global scoring_cards
    scoring_cards = []
    scoring_card_width = int(WIDTH * 0.25)
    scoring_card_height = int((HEIGHT - banner_height) // 4)
    x_margin = int(WIDTH * 0.7) + MARGIN
    y_start = banner_height + MARGIN

    for i in range(3):
        y = y_start + i * (scoring_card_height + MARGIN)
        scoring_cards.append(pygame.Rect(x_margin, y, scoring_card_width, scoring_card_height))

def draw_cards():
    """Draw the image cards."""
    for i, card in enumerate(cards):
        if flipped[i] or matched[i]:
            screen.blit(all_images[i], card.topleft)
        else:
            pygame.draw.rect(screen, WHITE, card)
            pygame.draw.rect(screen, RED, card, 2)

def draw_scoring_cards():
    """Draw the scoring cards."""
    scoring_labels = ["Hi-score", "Score", "Time taken"]
    scoring_values = [
        str(hi_score),
        str(click_count),
        f"{total_time_taken}s" if game_completed else f"{(pygame.time.get_ticks() - start_time) // 1000}s"
    ]

    for i, scoring_card in enumerate(scoring_cards):
        pygame.draw.rect(screen, WHITE, scoring_card)
        pygame.draw.rect(screen, RED, scoring_card, 2)
        label_surface = font.render(scoring_labels[i], True, BLACK)
        label_x = scoring_card.x + (scoring_card.width - label_surface.get_width()) // 2
        label_y = scoring_card.y + MARGIN
        screen.blit(label_surface, (label_x, label_y))
        value_surface = font.render(scoring_values[i], True, BLACK)
        value_x = scoring_card.x + (scoring_card.width - value_surface.get_width()) // 2
        value_y = scoring_card.y + scoring_card.height // 2
        screen.blit(value_surface, (value_x, value_y))

def main_menu():
    """Display the main menu and handle user interactions."""
    menu_running = True
    mute = False  # Track mute state

    # Button dimensions
    button_width = 300
    button_height = 60
    button_margin = 20

    # Button positions
    center_x = WIDTH // 2 - button_width // 2
    start_y = HEIGHT // 3

    buttons = [
        {"label": "Play", "rect": pygame.Rect(center_x, start_y, button_width, button_height)},
        {"label": "How to Play", "rect": pygame.Rect(center_x, start_y + button_height + button_margin, button_width, button_height)},
        {"label": "Quit", "rect": pygame.Rect(center_x, start_y + 2 * (button_height + button_margin), button_width, button_height)},
        {"label": "Mute", "rect": pygame.Rect(center_x + button_width + 20, start_y + 2 * (button_height + button_margin), 60, 60)},  # Mute button
    ]

    while menu_running:
        screen.fill(GRAY)

        # Draw title
        title_surface = font.render("Memory Match!", True, WHITE)
        title_x = (WIDTH - title_surface.get_width()) // 2
        title_y = HEIGHT // 6
        screen.blit(title_surface, (title_x, title_y))

        # Draw buttons
        for button in buttons:
            pygame.draw.rect(screen, BLACK, button["rect"])
            pygame.draw.rect(screen, WHITE, button["rect"], 3)
            label_surface = font.render(button["label"], True, WHITE)
            label_x = button["rect"].x + (button["rect"].width - label_surface.get_width()) // 2
            label_y = button["rect"].y + (button["rect"].height - label_surface.get_height()) // 2
            screen.blit(label_surface, (label_x, label_y))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        if button["label"] == "Play":
                            menu_running = False  # Exit menu and start the game
                        elif button["label"] == "How to Play":
                            show_instructions()
                        elif button["label"] == "Quit":
                            pygame.quit()
                            exit()
                        elif button["label"] == "Mute":
                            mute = not mute  # Toggle mute state

        pygame.display.flip()

def show_instructions():
    """Display the instructions screen."""
    instructions_running = True

    while instructions_running:
        screen.fill(GRAY)

        # Draw instructions
        instructions = [
            "How to Play:",
            "1. Click on two cards to flip them.",
            "2. Match pairs of cards to win.",
            "3. Complete the game in the fewest clicks and shortest time!",
        ]
        for i, line in enumerate(instructions):
            text_surface = font.render(line, True, WHITE)
            text_x = (WIDTH - text_surface.get_width()) // 2
            text_y = HEIGHT // 4 + i * 40
            screen.blit(text_surface, (text_x, text_y))

        # Draw "Back" button
        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
        pygame.draw.rect(screen, BLACK, back_button)
        pygame.draw.rect(screen, WHITE, back_button, 3)
        back_label = font.render("Back", True, WHITE)
        back_x = back_button.x + (back_button.width - back_label.get_width()) // 2
        back_y = back_button.y + (back_button.height - back_label.get_height()) // 2
        screen.blit(back_label, (back_x, back_y))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    instructions_running = False  # Exit instructions screen

        pygame.display.flip()

# Show the main menu
main_menu()

# Initialize positions
calculate_card_positions()
calculate_scoring_cards()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            calculate_card_positions()
            calculate_scoring_cards()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            current_time = pygame.time.get_ticks()

            if current_time - last_flip_time > delay:
                for i, card in enumerate(cards):
                    if card.collidepoint(mouse_pos) and not matched[i] and not flipped[i]:
                        flipped[i] = True
                        flipped_indices.append(i)
                        click_count += 1

                        if len(flipped_indices) == 2:
                            last_flip_time = current_time
                            if all_images[flipped_indices[0]] == all_images[flipped_indices[1]]:
                                matched[flipped_indices[0]] = True
                                matched[flipped_indices[1]] = True
                            else:
                                pygame.time.set_timer(pygame.USEREVENT, delay)
                            flipped_indices = []

        if event.type == pygame.USEREVENT:
            for i in range(TOTAL_CARDS):
                if not matched[i]:
                    flipped[i] = False
            pygame.time.set_timer(pygame.USEREVENT, 0)

    if not game_completed and all(matched):
        game_completed = True
        total_time_taken = (pygame.time.get_ticks() - start_time) // 1000

    screen.fill(GRAY)
    draw_banner()
    draw_cards()
    draw_scoring_cards()
    pygame.display.flip()

pygame.quit()