import pygame
import random
import os
import sys
import math
import time


def get_path(relative_path):
    """Finds assets in normal development and inside the PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Initialize Pygame
pygame.init()
pygame.font.init()

# Initialize background music playback
MUSIC_FILE = get_path("assets/Far-Away-Puzzle-Places.mp3")
try:
    pygame.mixer.init()
    if not os.path.exists(MUSIC_FILE):
        print(f"Warning: Music file not found: '{MUSIC_FILE}'. Music disabled.")
        MUSIC_FILE = None
    else:
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.3)  # Set volume (0.0 to 1.0)
except pygame.error as e:
    print(f"Warning: Pygame mixer could not be initialized: {e}. Music disabled.")
    MUSIC_FILE = None

# Card Sound Effects
FLIP_SOUND_FILE = get_path("assets/classic-click.wav")
flip_sound = None

try:
    if not os.path.exists(FLIP_SOUND_FILE):
        raise FileNotFoundError(f"Sound file not found: '{FLIP_SOUND_FILE}'")
    flip_sound = pygame.mixer.Sound(FLIP_SOUND_FILE)
except Exception as e:
    print(f"Error loading sound effect '{FLIP_SOUND_FILE}': {e}")

# button Sound Effects
SELECT_SOUND_FILE = get_path("assets/select-click.wav")
select_sound = None

try:
    if not os.path.exists(SELECT_SOUND_FILE):
        raise FileNotFoundError(f"Sound file not found: '{SELECT_SOUND_FILE}'")
    select_sound = pygame.mixer.Sound(SELECT_SOUND_FILE)
except Exception as e:
    print(f"Error loading button sound effect '{SELECT_SOUND_FILE}': {e}")

# Winning Sound Effect
WIN_SOUND_FILE = get_path("assets/cheering-crowd-loud-whistle.wav")
win_sound = None

try:
    if not os.path.exists(WIN_SOUND_FILE):
        raise FileNotFoundError(f"Sound file not found: '{WIN_SOUND_FILE}'")
    win_sound = pygame.mixer.Sound(WIN_SOUND_FILE)
except Exception as e:
    print(f"Error loading win sound effect '{WIN_SOUND_FILE}': {e}")

# --- Constants ---
WIDTH, HEIGHT = 900, 650
BLACK = (26, 26, 26)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
RED_DECOR = (190, 70, 70, 180)
GREEN_HIGHLIGHT = (0, 200, 0)
OUTLINE_COLOR = WHITE
TEXT_COLOR = WHITE
# Scaling factor for the RESTART symbol in the info bar circle
INFO_BAR_RESTART_SCALE = (
    0.7  # Adjust this if the restart symbol is too big/small in the circle
)

# --- Font Loading ---
SYMBOL_FONT_FILE = get_path("NotoSansSymbols2-Regular.ttf")
DEFAULT_FONT = None
try:
    TITLE_FONT = pygame.font.SysFont("Arial Black", 60)
    BUTTON_FONT = pygame.font.SysFont("Arial", 30)

    BOLD_BUTTON_FONT = pygame.font.SysFont("Arial", 30, bold=True)
    INFO_FONT = pygame.font.SysFont("Arial", 24)
    SMALL_FONT = pygame.font.SysFont("Arial", 20)
    OPTIONS_TITLE_FONT = pygame.font.SysFont("Arial", 36)
except pygame.error:
    print("Warn: Default fonts not found.")
    TITLE_FONT = pygame.font.Font(DEFAULT_FONT, 70)
    BUTTON_FONT = pygame.font.Font(DEFAULT_FONT, 40)

    BOLD_BUTTON_FONT = pygame.font.Font(DEFAULT_FONT, 40)
    INFO_FONT = pygame.font.Font(DEFAULT_FONT, 30)
    SMALL_FONT = pygame.font.Font(DEFAULT_FONT, 25)
    OPTIONS_TITLE_FONT = pygame.font.Font(DEFAULT_FONT, 46)
try:
    if not os.path.exists(SYMBOL_FONT_FILE):
        # Try a more common system font as a fallback for symbols if Noto is missing
        try:
            print(
                f"Warn: Symbol font file not found: '{SYMBOL_FONT_FILE}'. Trying 'Segoe UI Symbol'."
            )
            SYMBOL_FONT = pygame.font.SysFont("Segoe UI Symbol", 48)
            LARGE_SYMBOL_FONT = pygame.font.SysFont("Segoe UI Symbol", 150)
            print("Loaded fallback symbol font: Segoe UI Symbol")
        except pygame.error:
            print(
                f"FATAL: Failed to load primary symbol font '{SYMBOL_FONT_FILE}' and fallback 'Segoe UI Symbol'."
            )
            pygame.quit()
            sys.exit(1)
    else:
        SYMBOL_FONT = pygame.font.Font(SYMBOL_FONT_FILE, 48)
        LARGE_SYMBOL_FONT = pygame.font.Font(SYMBOL_FONT_FILE, 150)
        print(f"Loaded symbol font: {SYMBOL_FONT_FILE}")
except pygame.error as e:
    print(f"FATAL: Failed symbol font loading - {e}.")
    pygame.quit()
    sys.exit(1)


# Card image properties (used for loading)
CARD_IMG_WIDTH = 80
CARD_IMG_HEIGHT = 80

# Grid and Card Layout (will be updated based on selection)
MARGIN = 15
selected_rows = 3
selected_cols = 4
ROWS = selected_rows
COLS = selected_cols
TOTAL_CARDS = ROWS * COLS
CARD_BACK_COLOR = GRAY
CARD_OUTLINE_THICKNESS = 2

# Game Constants
FLIP_ANIMATION_DURATION = 0.25
HI_SCORE_FILE_BASE = get_path("assets/highscore")

# Define possible grid options
RECTANGULAR_GRIDS = [(3, 4), (4, 5), (5, 6)]
SQUARE_GRIDS = [(4, 4), (6, 6)]
ALL_GRID_OPTIONS = RECTANGULAR_GRIDS + SQUARE_GRIDS


# --- Global Game State Variables ---
screen = None
click_count = 0
start_time = 0
hi_scores = {}
current_hi_score = 0
game_completed = False
show_win_popup = False
total_time_taken = 0
paused = False
mute = False
time_at_pause = 0
total_paused_time = 0
pause_start_time = 0
last_displayed_time_sec = -1
potential_unique_images = []
unique_card_images = []
all_images = []
cards_rects = []
card_width = 0
card_height = 0
flipped = []
matched = []
flipped_indices = []
animating_cards = {}

# UI Element Rects (calculated in calculate_layouts)
info_panel_rect = score_rect = time_rect = hiscore_rect = mute_button_rect = (
    pause_button_rect
) = restart_button_rect = how_to_home_button_rect = options_home_button_rect = (
    pause_menu_pause_symbol_rect
) = pause_menu_home_symbol_rect = (  # Renamed home_button_rect -> restart_button_rect
    None  # Renamed pause_menu_restart_symbol_rect -> pause_menu_home_symbol_rect
)
how_to_box_rects = []
options_rects = {}
clear_scores_button_rect = None
show_clear_confirmation = False
clear_confirmation_start_time = 0.0
CLEAR_CONFIRMATION_DURATION = 1.0

# --- Game State Machine ---
STATE_MAIN_MENU = 0
STATE_HOW_TO_PLAY = 1
STATE_OPTIONS = 2
STATE_GAMEPLAY = 3


# --- Rotation Helper Functions ---
def rotate_point(center_x, center_y, x, y, angle_degrees):
    """Rotates a point (x,y) around a center (center_x, center_y) by an angle in degrees."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)
    x -= center_x
    y -= center_y
    new_x = x * cos_a - y * sin_a
    new_y = x * sin_a + y * cos_a
    return new_x + center_x, new_y + center_y


def get_rotated_rect_points(center_x, center_y, width, height, angle_degrees):
    """Calculates the four corner points of a rectangle rotated around its center."""
    half_w = width / 2
    half_h = height / 2
    points = [
        (-half_w, -half_h),
        (half_w, -half_h),
        (half_w, half_h),
        (-half_w, half_h),
    ]
    rotated_points = []
    for x, y in points:
        rotated_x, rotated_y = rotate_point(0, 0, x, y, angle_degrees)
        rotated_points.append((int(rotated_x + center_x), int(rotated_y + center_y)))
    return rotated_points


# --- Game Helper Functions ---
def initialize_screen(width=WIDTH, height=HEIGHT):
    """Initializes or reinitializes the game screen with given dimensions."""
    global screen, WIDTH, HEIGHT
    WIDTH, HEIGHT = width, height
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Memory Match!")


def load_and_play_music():
    """Loads and plays the background music if available and not already playing."""
    if MUSIC_FILE and pygame.mixer.get_init():
        try:
            if not pygame.mixer.music.get_busy() and not mute:
                pygame.mixer.music.play(-1)
                print(f"Playing music: {MUSIC_FILE}")
        except Exception as e:
            print(f"Error playing music: {e}")


def toggle_mute():
    """Toggles the mute state of the background music."""
    global mute
    if not pygame.mixer.get_init():
        return
    mute = not mute
    if mute:
        pygame.mixer.music.pause()
        print("Music Muted")
    else:
        pygame.mixer.music.unpause()
        print("Music Unmuted")


def clear_all_highscores():
    """Deletes all highscore files and resets in-memory scores."""
    global hi_scores, current_hi_score
    print("Attempting to clear all highscores...")
    deleted_count = 0
    error_count = 0

    # Iterate through all possible grid configurations defined
    for r, c in ALL_GRID_OPTIONS:
        filename = get_highscore_filename(r, c)
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Deleted: {filename}")
                deleted_count += 1
        except OSError as e:
            print(f"Error deleting {filename}: {e}")
            error_count += 1
        except Exception as e:
            print(f"Unexpected error deleting {filename}: {e}")
            error_count += 1

    # Reset the in-memory dictionary
    hi_scores = {}
    for r, c in ALL_GRID_OPTIONS:
        hi_scores[(r, c)] = 0

    # Update the current hi-score display variable based on selection
    current_hi_score = hi_scores.get((selected_rows, selected_cols), 0)


def load_potential_images():
    """Loads all available unique card images from files at the start."""
    global potential_unique_images
    images_loaded = []
    max_possible_unique_images = 36

    found_count = 0
    for i in range(1, max_possible_unique_images + 1):
        img_path = None

        possible_paths = [
            get_path(f"assets/image{i}.png"),
            get_path(f"assets/image{i}.jpg"),
            get_path(f"assets/image0{i}.png"),
            get_path(f"assets/image0{i}.jpg"),
        ]
        for p in possible_paths:
            if os.path.exists(p):
                img_path = p
                break

        if img_path:
            try:
                print(f"Loading: {img_path}")
                image = pygame.image.load(img_path).convert_alpha()

                img_rect = image.get_rect()
                if img_rect.width == 0 or img_rect.height == 0:
                    print(f"Warning: Image {img_path} has zero dimension.")
                    continue  # Skip invalid images

                scale = min(
                    CARD_IMG_WIDTH / img_rect.width, CARD_IMG_HEIGHT / img_rect.height
                )
                new_width = max(1, int(img_rect.width * scale))
                new_height = max(1, int(img_rect.height * scale))
                image = pygame.transform.smoothscale(image, (new_width, new_height))
                images_loaded.append(image)
                found_count += 1
            except (FileNotFoundError, pygame.error) as e:
                print(f"Error loading image {img_path}: {e}")
            except Exception as e:
                print(f"Unexpected error loading image {img_path}: {e}")

    if not images_loaded:
        print(
            f"FATAL: No unique images found (e.g., image1.png, image01.png). Exiting."
        )
        pygame.quit()
        sys.exit()

    potential_unique_images = images_loaded[:]


def setup_current_game_images():
    """Prepares the specific set of images needed for the currently selected grid size."""
    global all_images, unique_card_images, ROWS, COLS, TOTAL_CARDS

    # Update game parameters based on selection
    ROWS = selected_rows
    COLS = selected_cols
    TOTAL_CARDS = ROWS * COLS

    needed_unique = TOTAL_CARDS // 2
    current_unique_set = []

    if not potential_unique_images:
        print("FATAL Error: No potential unique images were loaded.")
        pygame.quit()
        sys.exit(1)

    num_available_unique = len(potential_unique_images)

    if needed_unique <= num_available_unique:
        current_unique_set = potential_unique_images[:needed_unique]
    else:
        current_unique_set = potential_unique_images[:]
        for i in range(needed_unique - num_available_unique):
            reuse_index = i % num_available_unique
            current_unique_set.append(potential_unique_images[reuse_index])

    unique_card_images = current_unique_set[:]
    all_images = unique_card_images * 2
    random.shuffle(all_images)


def get_highscore_filename(rows, cols):
    """Generates the filename for the high score based on grid size."""
    return f"{HI_SCORE_FILE_BASE}_{rows}x{cols}.txt"


def load_highscore(rows, cols):
    """Loads the high score for a specific grid size."""
    global hi_scores
    filename = get_highscore_filename(rows, cols)
    score = 0
    try:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                content = f.read().strip()
                if content.isdigit():
                    score = int(content)
                else:
                    print(
                        f"Warn: Invalid content in {filename}. Resetting score for {rows}x{cols}."
                    )
    except (IOError, ValueError) as e:
        print(f"Error reading {filename}: {e}. Using 0.")
    except Exception as e:
        print(f"Unexpected error reading {filename}: {e}. Using 0.")
    hi_scores[(rows, cols)] = score
    return score


def load_all_highscores():
    """Loads high scores for all defined grid sizes."""
    global hi_scores, current_hi_score
    print("Loading all high scores...")
    hi_scores = {}
    for r, c in ALL_GRID_OPTIONS:
        load_highscore(r, c)
    current_hi_score = hi_scores.get((selected_rows, selected_cols), 0)


def save_highscore(rows, cols):
    """Saves the current high score for the specified grid size."""
    filename = get_highscore_filename(rows, cols)
    score_to_save = hi_scores.get((rows, cols), 0)
    try:
        with open(filename, "w") as f:
            f.write(str(score_to_save))
            print(f"High score {score_to_save} for {rows}x{cols} saved to {filename}.")
    except IOError:
        print(f"Error writing {filename}.")


def reset_game_state():
    """Resets all game variables to their initial states for a new game, using the selected grid size."""
    global click_count, start_time, game_completed, total_time_taken, flipped, matched, flipped_indices, paused, all_images, unique_card_images, show_win_popup, total_paused_time, time_at_pause, pause_start_time, last_displayed_time_sec, animating_cards, ROWS, COLS, TOTAL_CARDS, current_hi_score

    setup_current_game_images()

    # Reset game variables
    click_count = 0
    start_time = 0  # Timer reset will happen when first card clicked or restart pressed
    game_completed = False
    show_win_popup = False
    total_time_taken = 0
    paused = False  # Unpause if restarting
    total_paused_time = 0
    time_at_pause = 0
    pause_start_time = 0
    last_displayed_time_sec = -1
    flipped = [False] * TOTAL_CARDS
    matched = [False] * TOTAL_CARDS
    flipped_indices = []
    animating_cards = {}  # Reset animations

    # Update the current high score display variable
    current_hi_score = hi_scores.get((selected_rows, selected_cols), 0)


def draw_grid_background():
    """Draws a subtle grid pattern on the background."""
    grid_color = (60, 60, 60)
    for x in range(0, WIDTH, 20):
        pygame.draw.line(screen, grid_color, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 20):
        pygame.draw.line(screen, grid_color, (0, y), (WIDTH, y))


# --- calculate_layouts Function with Fixes ---
def calculate_layouts():
    """Calculates positions and sizes for cards and UI elements based on current screen size and selected grid."""
    global cards_rects, card_width, card_height, info_panel_rect, score_rect, time_rect, hiscore_rect, mute_button_rect, pause_button_rect, restart_button_rect, how_to_home_button_rect, options_home_button_rect, how_to_box_rects, pause_menu_pause_symbol_rect, pause_menu_home_symbol_rect, options_rects, clear_scores_button_rect

    # --- Gameplay Layout ---
    card_area_width = int(WIDTH * 0.68)
    card_area_height = HEIGHT - MARGIN * 2
    grid_width = card_area_width - MARGIN * 2
    grid_height = card_area_height - MARGIN * 2
    if COLS > 0:
        card_width = max(10, (grid_width - (COLS - 1) * MARGIN) // COLS)
    else:
        card_width = 10
    if ROWS > 0:
        card_height = max(10, (grid_height - (ROWS - 1) * MARGIN) // ROWS)
    else:
        card_height = 10
    total_grid_width = COLS * card_width + (COLS - 1) * MARGIN
    total_grid_height = ROWS * card_height + (ROWS - 1) * MARGIN
    start_x = MARGIN + max(0, (grid_width - total_grid_width) // 2)
    start_y = MARGIN + max(0, (grid_height - total_grid_height) // 2)
    cards_rects = []
    for row in range(ROWS):
        for col in range(COLS):
            x = start_x + col * (card_width + MARGIN)
            y = start_y + row * (card_height + MARGIN)
            cards_rects.append(pygame.Rect(x, y, card_width, card_height))
    info_panel_x = card_area_width + MARGIN
    info_panel_width = max(150, WIDTH - info_panel_x - MARGIN)
    info_panel_rect = pygame.Rect(
        info_panel_x, MARGIN, info_panel_width, HEIGHT - MARGIN * 2
    )
    button_area_height = 90
    info_box_total_height = max(
        1, info_panel_rect.height - button_area_height - MARGIN * 4
    )
    info_box_height = max(50, info_box_total_height // 3)
    hiscore_y = info_panel_rect.y + MARGIN
    hiscore_rect = pygame.Rect(
        info_panel_x + MARGIN, hiscore_y, info_panel_width - MARGIN * 2, info_box_height
    )
    score_y = hiscore_y + info_box_height + MARGIN
    score_rect = pygame.Rect(
        info_panel_x + MARGIN, score_y, info_panel_width - MARGIN * 2, info_box_height
    )
    time_y = score_y + info_box_height + MARGIN
    time_rect = pygame.Rect(
        info_panel_x + MARGIN, time_y, info_panel_width - MARGIN * 2, info_box_height
    )
    button_radius = 34
    button_spacing = 20
    buttons_y = info_panel_rect.bottom - button_radius - MARGIN
    total_buttons_width = 3 * (2 * button_radius) + 2 * button_spacing
    buttons_start_x = info_panel_x + max(
        0, (info_panel_width - total_buttons_width) // 2
    )
    mute_button_rect = pygame.Rect(
        buttons_start_x, buttons_y - button_radius, 2 * button_radius, 2 * button_radius
    )
    pause_button_rect = pygame.Rect(
        buttons_start_x + (2 * button_radius + button_spacing),
        buttons_y - button_radius,
        2 * button_radius,
        2 * button_radius,
    )
    # The third button is now the RESTART button, but its position calculation remains the same
    restart_button_rect = pygame.Rect(
        buttons_start_x + 2 * (2 * button_radius + button_spacing),
        buttons_y - button_radius,
        2 * button_radius,
        2 * button_radius,
    )

    # --- How to Play Layout ---
    how_to_home_button_radius = button_radius
    how_to_home_button_rect = pygame.Rect(
        MARGIN * 2,
        MARGIN * 2,
        how_to_home_button_radius * 2,
        how_to_home_button_radius * 2,
    )
    box_margin = 40
    content_area_x_ht = how_to_home_button_rect.right + box_margin
    content_area_y_ht = MARGIN * 2
    content_area_width_ht = max(1, WIDTH - content_area_x_ht - MARGIN * 2)
    content_area_height_ht = max(1, HEIGHT - content_area_y_ht - MARGIN * 2)
    box_width = max(50, (content_area_width_ht - box_margin) // 2)
    box_height = max(50, (content_area_height_ht - box_margin) // 2)
    how_to_box_rects = [
        pygame.Rect(content_area_x_ht, content_area_y_ht, box_width, box_height),
        pygame.Rect(
            content_area_x_ht + box_width + box_margin,
            content_area_y_ht,
            box_width,
            box_height,
        ),
        pygame.Rect(
            content_area_x_ht,
            content_area_y_ht + box_height + box_margin,
            box_width,
            box_height,
        ),
        pygame.Rect(
            content_area_x_ht + box_width + box_margin,
            content_area_y_ht + box_height + box_margin,
            box_width,
            box_height,
        ),
    ]

    # --- Options Layout ---
    options_rects = {}
    option_btn_width = 100
    option_btn_height = 50
    option_h_margin = 20
    option_v_margin = 15
    section_v_spacing = 40
    label_font_h = INFO_FONT.get_height()

    # Home Button (top-left)
    options_home_button_radius = button_radius
    options_home_button_rect = pygame.Rect(
        MARGIN * 2,
        MARGIN * 2,
        options_home_button_radius * 2,
        options_home_button_radius * 2,
    )

    # --- Content Layout Flow ---
    content_start_x = options_home_button_rect.right + MARGIN * 3
    current_y = options_home_button_rect.bottom + MARGIN
    content_area_width = WIDTH - content_start_x - MARGIN * 2

    # Section 1: Rectangle Grids
    rect_title_surf = OPTIONS_TITLE_FONT.render("Rectangle Grids", True, TEXT_COLOR)
    rect_title_rect = rect_title_surf.get_rect(left=content_start_x, top=current_y)
    current_y = rect_title_rect.bottom + option_v_margin

    # Layout Rect Buttons Left-aligned
    if len(RECTANGULAR_GRIDS) > 0:
        current_btn_x = content_start_x
        for r, c in RECTANGULAR_GRIDS:
            btn_rect = pygame.Rect(
                current_btn_x, current_y, option_btn_width, option_btn_height
            )
            options_rects[(r, c)] = btn_rect
            current_btn_x += option_btn_width + option_h_margin
        current_y += option_btn_height

    current_y += section_v_spacing

    # Section 2: Square Grids
    square_title_surf = OPTIONS_TITLE_FONT.render("Square Grids", True, TEXT_COLOR)
    square_title_rect = square_title_surf.get_rect(left=content_start_x, top=current_y)
    current_y = square_title_rect.bottom + option_v_margin

    # Layout Square Buttons Left-aligned
    if len(SQUARE_GRIDS) > 0:
        current_btn_x = content_start_x
        for r, c in SQUARE_GRIDS:
            btn_rect = pygame.Rect(
                current_btn_x, current_y, option_btn_width, option_btn_height
            )
            options_rects[(r, c)] = btn_rect
            current_btn_x += option_btn_width + option_h_margin
        current_y += option_btn_height

    current_y += section_v_spacing

    # Section 3: Clear Highscores
    clear_label_text = "Clear Highscores (WARNING! CANNOT BE UNDONE)"
    clear_label_surf = INFO_FONT.render(clear_label_text, True, TEXT_COLOR)
    clear_label_rect = clear_label_surf.get_rect(left=content_start_x, top=current_y)
    current_y = clear_label_rect.bottom + option_v_margin

    # Clear Button
    clear_btn_width = 100
    clear_btn_height = 60
    clear_btn_x = content_start_x
    clear_scores_button_rect = pygame.Rect(
        clear_btn_x, current_y, clear_btn_width, clear_btn_height
    )

    # --- Pause Menu Layout (Centered Pause and HOME) ---
    pause_menu_pause_symbol_rect = None
    pause_menu_home_symbol_rect = None  # Renamed variable conceptually
    try:
        pause_sym_str = "⏸️"
        home_sym_str = "🏠"  # Home symbol for pause screen

        symbol_spacing = 50  # Pixels between the two symbols

        pause_sym_surf = LARGE_SYMBOL_FONT.render(pause_sym_str, True, WHITE)
        home_sym_surf = LARGE_SYMBOL_FONT.render(
            home_sym_str, True, WHITE
        )  # Use LARGE font for pause screen Home

        # Get original sizes (No scaling needed for Home on pause screen)
        pause_w, pause_h = pause_sym_surf.get_size()
        home_w, home_h = home_sym_surf.get_size()

        # Calculate total width using the unscaled home width
        total_width = pause_w + symbol_spacing + home_w
        start_x_symbols = (WIDTH - total_width) // 2
        center_y_symbols = HEIGHT // 2

        # Position the pause symbol
        pause_menu_pause_symbol_rect = pause_sym_surf.get_rect(
            left=start_x_symbols, centery=center_y_symbols
        )

        # Position the home symbol relative to the pause symbol
        # Use its own dimensions (home_w, home_h)
        pause_menu_home_symbol_rect = pygame.Rect(
            pause_menu_pause_symbol_rect.right + symbol_spacing,  # Left edge
            0,  # Top (will be set by centery)
            home_w,  # Home width
            home_h,  # Home height
        )
        pause_menu_home_symbol_rect.centery = center_y_symbols  # Align vertically

        # Check if home symbol rendered correctly
        if home_w == 0:
            print(
                f"Warning: Home symbol '{home_sym_str}' did not render with the current font during layout calculation. Fallback rect used."
            )
            # Use fallback rect dimensions if rendering failed
            fallback_size = 100  # Standard fallback size for pause menu
            pause_menu_home_symbol_rect.width = fallback_size
            pause_menu_home_symbol_rect.height = fallback_size
            pause_menu_home_symbol_rect.left = (
                pause_menu_pause_symbol_rect.right + symbol_spacing
            )
            pause_menu_home_symbol_rect.centery = center_y_symbols

    except Exception as e:
        print(f"Error creating large pause menu symbols during layout: {e}")
        # Fallback rects if font rendering fails during layout
        fallback_size = 100
        fallback_spacing = 20
        total_fallback_width = 2 * fallback_size + fallback_spacing
        fallback_start_x = (WIDTH - total_fallback_width) // 2
        fallback_y = HEIGHT // 2 - fallback_size // 2

        pause_menu_pause_symbol_rect = pygame.Rect(
            fallback_start_x, fallback_y, fallback_size, fallback_size
        )
        pause_menu_home_symbol_rect = pygame.Rect(  # Still represents Home conceptually
            fallback_start_x + fallback_size + fallback_spacing,
            fallback_y,
            fallback_size,
            fallback_size,
        )


# --- Drawing Functions ---
def draw_main_menu():
    """Draws the main menu screen with title, buttons, and decorative images."""
    screen.fill(BLACK)
    draw_grid_background()

    # --- Decorative Images ---
    image_paths = [
        (
            get_path(f"assets/image0{i}.png")
            if os.path.exists(get_path(f"assets/image0{i}.png"))
            else (
                get_path(f"assets/image{i}.png")
                if os.path.exists(get_path(f"assets/image{i}.png"))
                else (
                    get_path(f"assets/image0{i}.jpg")
                    if os.path.exists(get_path(f"assets/image0{i}.jpg"))
                    else (
                        get_path(f"assets/image{i}.jpg")
                        if os.path.exists(get_path(f"assets/image{i}.jpg"))
                        else None
                    )
                )
            )
        )
        for i in range(1, 7)  # Try to load first 6 images for decoration
    ]
    images = []
    for path in image_paths:
        if path:
            try:
                image = pygame.image.load(path).convert_alpha()
                images.append(image)
            except Exception as e:
                print(f"Error loading decorative image {path}: {e}")
        else:
            pass

    title_rect_calc = TITLE_FONT.render("Memory Match!", True, TEXT_COLOR).get_rect(
        center=(WIDTH // 2, HEIGHT // 5)
    )
    btn_w = 300
    btn_h = 55
    btn_m = 25

    # --- Calculate Button Positions ---
    total_button_height = 4 * btn_h + 3 * btn_m
    start_y = title_rect_calc.bottom + max(
        40, (HEIGHT - title_rect_calc.bottom - total_button_height) // 2
    )

    play_rect_calc = pygame.Rect(WIDTH // 2 - btn_w // 2, start_y, btn_w, btn_h)
    howto_rect_calc = pygame.Rect(
        WIDTH // 2 - btn_w // 2, start_y + (btn_h + btn_m), btn_w, btn_h
    )
    options_rect_calc = pygame.Rect(
        WIDTH // 2 - btn_w // 2, start_y + 2 * (btn_h + btn_m), btn_w, btn_h
    )
    quit_rect_calc = pygame.Rect(
        WIDTH // 2 - btn_w // 2, start_y + 3 * (btn_h + btn_m), btn_w, btn_h
    )
    avoid_areas = [
        title_rect_calc.inflate(20, 20),
        play_rect_calc.inflate(20, 20),
        howto_rect_calc.inflate(20, 20),
        options_rect_calc.inflate(20, 20),
        quit_rect_calc.inflate(20, 20),
    ]

    # --- Place Decorative Images ---
    margin_deco = 20
    image_width_deco = 100
    image_height_deco = 100
    placed_positions = []
    rotation_angle = 15

    for image in images:
        if image:
            # Scale image first
            try:
                img_rect_orig = image.get_rect()
                scale_deco = min(
                    (
                        image_width_deco / img_rect_orig.width
                        if img_rect_orig.width > 0
                        else 1
                    ),
                    (
                        image_height_deco / img_rect_orig.height
                        if img_rect_orig.height > 0
                        else 1
                    ),
                )
                scaled_w = max(1, int(img_rect_orig.width * scale_deco))
                scaled_h = max(1, int(img_rect_orig.height * scale_deco))
                scaled_image = pygame.transform.smoothscale(image, (scaled_w, scaled_h))
            except Exception as e:
                print(f"Error scaling decorative image: {e}")
                continue  # Skip this image if scaling fails

            for _ in range(100):  # Try placing randomly
                x = random.randint(margin_deco, WIDTH - scaled_w - margin_deco)
                y = random.randint(margin_deco, HEIGHT - scaled_h - margin_deco)
                rotation = random.uniform(-rotation_angle, rotation_angle)
                try:
                    rotated_image = pygame.transform.rotate(scaled_image, rotation)
                    image_rect = rotated_image.get_rect(
                        center=(x + scaled_w // 2, y + scaled_h // 2)
                    )
                except Exception as e:
                    print(f"Error rotating decorative image: {e}")
                    image_rect = scaled_image.get_rect(
                        center=(x + scaled_w // 2, y + scaled_h // 2)
                    )  # Use unrotated if rotate fails
                    rotated_image = scaled_image

                # Check for collisions
                collision = False
                if any(image_rect.colliderect(area) for area in avoid_areas):
                    collision = True
                if not collision:
                    for _, _, p_rect in placed_positions:
                        if image_rect.colliderect(p_rect):
                            collision = True
                            break
                if not collision:
                    screen.blit(rotated_image, image_rect.topleft)
                    placed_positions.append((x, y, image_rect))
                    break  # Placed successfully

    # --- Draw Title (Same as before) ---
    title_surface = TITLE_FONT.render("Memory Match!", True, TEXT_COLOR)
    title_rect = title_surface.get_rect(
        center=title_rect_calc.center
    )  # Use calculated center
    title_bg_rect = title_rect.inflate(20, 10)
    title_bg_surf = pygame.Surface(title_bg_rect.size, pygame.SRCALPHA)
    title_bg_surf.fill((0, 0, 0, 150))
    pygame.draw.rect(title_bg_surf, WHITE, title_bg_surf.get_rect(), 2, border_radius=5)
    screen.blit(title_bg_surf, title_bg_rect.topleft)
    screen.blit(title_surface, title_rect)

    # --- Draw Buttons ---
    buttons = [
        {"label": "Play", "rect": play_rect_calc, "action": "play"},
        {"label": "How to play", "rect": howto_rect_calc, "action": "how_to"},
        {"label": "Options", "rect": options_rect_calc, "action": "options"},
        {"label": "Quit", "rect": quit_rect_calc, "action": "quit"},
    ]
    for btn in buttons:
        pygame.draw.rect(screen, BLACK, btn["rect"], border_radius=5)
        pygame.draw.rect(
            screen,
            OUTLINE_COLOR,
            btn["rect"],
            CARD_OUTLINE_THICKNESS * 2,
            border_radius=5,
        )

        lbl_surf = BOLD_BUTTON_FONT.render(btn["label"], True, TEXT_COLOR)
        lbl_rect = lbl_surf.get_rect(center=btn["rect"].center)
        screen.blit(lbl_surf, lbl_rect)

    # --- Draw Mute Button ---
    mute_radius = 32
    mute_center_x = quit_rect_calc.right + btn_m + mute_radius
    mute_center_y = quit_rect_calc.centery
    mute_btn_rect = pygame.Rect(0, 0, mute_radius * 2, mute_radius * 2)
    mute_btn_rect.center = (mute_center_x, mute_center_y)
    if mute_btn_rect.right > WIDTH - MARGIN:  # Adjust if off-screen
        mute_center_x = quit_rect_calc.left - btn_m - mute_radius
        mute_btn_rect.center = (mute_center_x, mute_center_y)

    pygame.draw.circle(screen, BLACK, mute_btn_rect.center, mute_radius)
    pygame.draw.circle(
        screen,
        OUTLINE_COLOR,
        mute_btn_rect.center,
        mute_radius,
        CARD_OUTLINE_THICKNESS * 2,
    )
    mute_sym = "🔇" if mute else "🔊"
    mute_lbl_surf = SYMBOL_FONT.render(mute_sym, True, TEXT_COLOR)
    mute_lbl_rect = mute_lbl_surf.get_rect(center=mute_btn_rect.center)
    mute_v_offset = 7 if mute else 5
    mute_lbl_rect.centery += mute_v_offset
    screen.blit(mute_lbl_surf, mute_lbl_rect)

    return buttons, mute_btn_rect


def draw_how_to_play():
    """Draws the instructions screen with text boxes, images, and a home button."""
    screen.fill(BLACK)
    draw_grid_background()

    # Draw Home Button (uses how_to_home_button_rect calculated in calculate_layouts)
    home_sym = "🏠"
    if how_to_home_button_rect:
        pygame.draw.circle(
            screen,
            BLACK,
            how_to_home_button_rect.center,
            how_to_home_button_rect.width // 2,
        )
        pygame.draw.circle(
            screen,
            OUTLINE_COLOR,
            how_to_home_button_rect.center,
            how_to_home_button_rect.width // 2,
            CARD_OUTLINE_THICKNESS * 2,
        )
        home_lbl_surf = SYMBOL_FONT.render(home_sym, True, TEXT_COLOR)
        home_lbl_rect = home_lbl_surf.get_rect(center=how_to_home_button_rect.center)
        home_lbl_rect.centery += 3
        screen.blit(home_lbl_surf, home_lbl_rect)
    else:
        print("Warning: how_to_home_button_rect not calculated.")
        return None

    # Draw Instruction Boxes (uses how_to_box_rects from calculate_layouts)
    instructions = [
        "Click two cards.",
        "If they match, they stay face up.",
        "If not, they flip back down.",
        "Match all pairs to win!",
        "Lower score (clicks) & time is better.",
    ]
    groups = [instructions[:3], instructions[3:]]
    text_box_indices = [0, 2]
    image_box_indices = [1, 3]
    image_paths = [get_path("assets/2_flipped.png"), get_path("assets/all_flipped.png")]

    line_spacing = 5
    font_linesize = INFO_FONT.get_linesize()

    for i, box_rect in enumerate(how_to_box_rects):
        if box_rect.width <= 0 or box_rect.height <= 0:
            continue

        pygame.draw.rect(screen, BLACK, box_rect, border_radius=5)
        pygame.draw.rect(
            screen,
            WHITE,
            box_rect,
            CARD_OUTLINE_THICKNESS,
            border_radius=5,
        )

        # Draw Text
        if i in text_box_indices:
            group_index = text_box_indices.index(i)
            if group_index < len(groups):
                lines = groups[group_index]

                num_lines = len(lines)
                total_h = (
                    num_lines * font_linesize + max(0, num_lines - 1) * line_spacing
                )
                start_y = box_rect.centery - (total_h / 2)

                current_y = start_y
                for line in lines:
                    words = line.split(" ")
                    lines_to_draw = []
                    current_line = ""
                    for word in words:
                        test_line = current_line + word + " "
                        test_surf = INFO_FONT.render(test_line, True, TEXT_COLOR)
                        if test_surf.get_width() < box_rect.width - 20:
                            current_line = test_line
                        else:
                            lines_to_draw.append(current_line.strip())
                            current_line = word + " "
                    lines_to_draw.append(current_line.strip())

                    # Recalculate vertical centering if wrapping occurs across multiple original lines
                    num_wrapped = len(lines_to_draw)
                    block_h = (
                        num_wrapped * font_linesize
                        + max(0, num_wrapped - 1) * line_spacing
                    )
                    block_start_y = current_y

                    if len(lines_to_draw) > 1:
                        block_start_y = box_rect.centery - block_h / 2

                    inner_y = block_start_y
                    for wrapped_line in lines_to_draw:
                        line_surf = INFO_FONT.render(wrapped_line, True, TEXT_COLOR)
                        line_rect = line_surf.get_rect(
                            centerx=box_rect.centerx, top=inner_y
                        )
                        screen.blit(line_surf, line_rect)
                        inner_y += font_linesize + line_spacing
                    current_y = inner_y

        # Draw Images
        elif i in image_box_indices:
            image_index = image_box_indices.index(i)
            if image_index < len(image_paths):
                try:
                    image_path = image_paths[image_index]
                    if not os.path.exists(image_path):
                        print(f"Warning: Instruction image not found: {image_path}")
                        raise FileNotFoundError()  # Skip drawing if not found

                    image = pygame.image.load(image_path).convert_alpha()

                    img_margin = 15
                    max_img_width = max(1, box_rect.width - 2 * img_margin)
                    max_img_height = max(1, box_rect.height - 2 * img_margin)
                    img_orig_w, img_orig_h = image.get_size()
                    if img_orig_w > 0 and img_orig_h > 0:
                        scale = min(
                            max_img_width / img_orig_w, max_img_height / img_orig_h
                        )
                        img_new_w = max(1, int(img_orig_w * scale))
                        img_new_h = max(1, int(img_orig_h * scale))
                        scaled_image = pygame.transform.smoothscale(
                            image, (img_new_w, img_new_h)
                        )
                        image_rect = scaled_image.get_rect(center=box_rect.center)
                        screen.blit(scaled_image, image_rect.topleft)
                    else:
                        print(
                            f"Warning: Cannot scale instruction image {image_path} due to zero dimension."
                        )

                except Exception as e:
                    print(
                        f"Error loading/placing instruction image '{image_paths[image_index]}': {e}"
                    )

                    pygame.draw.line(
                        screen, RED_DECOR, box_rect.topleft, box_rect.bottomright, 2
                    )
                    pygame.draw.line(
                        screen, RED_DECOR, box_rect.topright, box_rect.bottomleft, 2
                    )

    return how_to_home_button_rect  # Return the home button rect for click detection


# --- draw_options_menu Function with Fixes ---
def draw_options_menu():
    """Draws the options screen using calculated layouts."""
    global options_rects, clear_scores_button_rect, show_clear_confirmation
    screen.fill(BLACK)
    draw_grid_background()
    option_v_margin = 15
    content_start_x = MARGIN * 2

    # --- Draw Home Button ---
    home_sym = "🏠"
    if options_home_button_rect:
        pygame.draw.circle(
            screen,
            BLACK,
            options_home_button_rect.center,
            options_home_button_rect.width // 2,
        )
        pygame.draw.circle(
            screen,
            OUTLINE_COLOR,
            options_home_button_rect.center,
            options_home_button_rect.width // 2,
            CARD_OUTLINE_THICKNESS * 2,
        )
        try:
            home_lbl_surf = SYMBOL_FONT.render(home_sym, True, TEXT_COLOR)
            home_lbl_rect = home_lbl_surf.get_rect(
                center=options_home_button_rect.center
            )
            home_lbl_rect.centery += 3
            screen.blit(home_lbl_surf, home_lbl_rect)
        except Exception as e:
            print(f"Error rendering home symbol: {e}")
    else:
        print("Warning: options_home_button_rect not calculated for drawing.")

    # --- Draw Sections based on calculated rects ---
    if options_home_button_rect:
        content_start_x = options_home_button_rect.right + MARGIN * 3
    else:  # Fallback if home button rect isn't ready
        content_start_x = MARGIN * 4

    # Infer Title Positions based on button rects (more robust than recalculating full flow)
    # Rectangle Grids
    rect_buttons_y = HEIGHT
    rect_buttons_x = WIDTH
    for r, c in RECTANGULAR_GRIDS:
        if (r, c) in options_rects:
            rect_buttons_y = min(rect_buttons_y, options_rects[(r, c)].top)
            rect_buttons_x = min(rect_buttons_x, options_rects[(r, c)].left)
    if rect_buttons_y < HEIGHT:
        rect_title_surf = OPTIONS_TITLE_FONT.render("Rectangle Grids", True, TEXT_COLOR)
        rect_title_y = (
            rect_buttons_y - OPTIONS_TITLE_FONT.get_height() - option_v_margin
        )
        rect_title_rect = rect_title_surf.get_rect(
            left=rect_buttons_x, top=rect_title_y
        )
        screen.blit(rect_title_surf, rect_title_rect)

    # Square Grids
    sq_buttons_y = HEIGHT
    sq_buttons_x = WIDTH
    for r, c in SQUARE_GRIDS:
        if (r, c) in options_rects:
            sq_buttons_y = min(sq_buttons_y, options_rects[(r, c)].top)
            sq_buttons_x = min(sq_buttons_x, options_rects[(r, c)].left)
    if sq_buttons_y < HEIGHT:
        square_title_surf = OPTIONS_TITLE_FONT.render("Square Grids", True, TEXT_COLOR)
        sq_title_y = sq_buttons_y - OPTIONS_TITLE_FONT.get_height() - option_v_margin
        sq_title_rect = square_title_surf.get_rect(left=sq_buttons_x, top=sq_title_y)
        screen.blit(square_title_surf, sq_title_rect)

    # Clear Highscores Label (Position relative to the actual clear button rect)
    if clear_scores_button_rect:
        clear_label_text = "Clear Highscores (WARNING! CANNOT BE UNDONE)"
        clear_label_surf = INFO_FONT.render(clear_label_text, True, TEXT_COLOR)
        label_y = (
            clear_scores_button_rect.top - INFO_FONT.get_height() - option_v_margin
        )
        clear_label_rect = clear_label_surf.get_rect(
            left=clear_scores_button_rect.left, top=label_y
        )
        screen.blit(clear_label_surf, clear_label_rect)

    # Draw Option Buttons (Grid Selection)
    for (r, c), rect in options_rects.items():
        is_selected = r == selected_rows and c == selected_cols
        button_label = f"{r}x{c}"
        pygame.draw.rect(screen, BLACK, rect, border_radius=5)
        border_color = GREEN_HIGHLIGHT if is_selected else OUTLINE_COLOR
        border_thickness = (
            CARD_OUTLINE_THICKNESS * 2 if is_selected else CARD_OUTLINE_THICKNESS
        )
        pygame.draw.rect(screen, border_color, rect, border_thickness, border_radius=5)
        lbl_surf = BUTTON_FONT.render(button_label, True, TEXT_COLOR)
        lbl_rect = lbl_surf.get_rect(center=rect.center)
        screen.blit(lbl_surf, lbl_rect)

    # Draw Clear Highscores Button and Icon
    if clear_scores_button_rect:
        pygame.draw.rect(screen, BLACK, clear_scores_button_rect, border_radius=5)
        pygame.draw.rect(
            screen,
            OUTLINE_COLOR,
            clear_scores_button_rect,
            CARD_OUTLINE_THICKNESS,
            border_radius=5,
        )

        # Draw Icon (Bin or Tick)
        display_symbol = "🗑️"
        symbol_v_offset = 5
        if show_clear_confirmation:
            display_symbol = "✔️"
            symbol_v_offset = 3

        try:
            symbol_surf = SYMBOL_FONT.render(display_symbol, True, TEXT_COLOR)
            symbol_rect = symbol_surf.get_rect(center=clear_scores_button_rect.center)
            symbol_rect.centery += symbol_v_offset
            screen.blit(symbol_surf, symbol_rect)
        except Exception as e:
            print(f"Error rendering options button symbol '{display_symbol}': {e}")
            # Fallback text
            fb_text = "Cleared" if show_clear_confirmation else "Clear"
            fb_surf = SMALL_FONT.render(fb_text, True, TEXT_COLOR)
            fb_rect = fb_surf.get_rect(center=clear_scores_button_rect.center)
            screen.blit(fb_surf, fb_rect)

    # Return clickable rects
    return options_home_button_rect, options_rects, clear_scores_button_rect


# --- draw_game_screen Function Modified ---
def draw_game_screen():
    """Draws the main gameplay area including cards (with animations) and the info panel."""
    global animating_cards, flipped, current_hi_score
    screen.fill(BLACK)
    draw_grid_background()
    current_timestamp = time.time()

    # --- Card Drawing Logic ---
    # (No changes needed in card drawing logic itself)
    if (
        cards_rects
        and len(cards_rects) == TOTAL_CARDS
        and len(all_images) == TOTAL_CARDS
    ):
        indices_to_remove_from_animation = []

        for i, card_rect in enumerate(cards_rects):
            if card_rect.width <= 0 or card_rect.height <= 0:
                continue

            is_animating = i in animating_cards
            draw_outline = True

            if is_animating and not paused:
                anim_data = animating_cards[i]
                elapsed = current_timestamp - anim_data["start_time"]
                progress = min(1.0, elapsed / FLIP_ANIMATION_DURATION)
                scale_x = abs(1.0 - 2 * progress)
                animated_width = max(1, int(card_rect.width * scale_x))
                show_front = (
                    anim_data["direction"] == "to_front" and progress >= 0.5
                ) or (anim_data["direction"] == "to_back" and progress < 0.5)
                center_x, center_y = card_rect.center

                if show_front:
                    try:
                        img_surf = all_images[i]
                        img_orig_w, img_orig_h = img_surf.get_size()

                        card_inner_w = card_rect.width - 4
                        card_inner_h = card_rect.height - 4
                        if card_inner_w <= 0 or card_inner_h <= 0:
                            raise ValueError("Card inner size invalid")

                        scale_factor = 1.0
                        if img_orig_w > 0 and img_orig_h > 0:
                            scale_factor = min(
                                card_inner_w / img_orig_w, card_inner_h / img_orig_h
                            )
                        base_img_w = max(1, int(img_orig_w * scale_factor))
                        base_img_h = max(1, int(img_orig_h * scale_factor))

                        final_img_w = max(1, int(base_img_w * scale_x))
                        final_img_h = base_img_h

                        if final_img_w > 0 and final_img_h > 0:
                            scaled_img = pygame.transform.smoothscale(
                                img_surf, (final_img_w, final_img_h)
                            )
                            img_rect = scaled_img.get_rect(center=(center_x, center_y))
                            screen.blit(scaled_img, img_rect)
                        else:
                            raise ValueError("Scaled image size zero")

                    except Exception as e:
                        print(f"Err draw animated img {i}: {e}")
                        temp_rect = pygame.Rect(
                            0, 0, max(1, animated_width), card_rect.height
                        )
                        temp_rect.center = card_rect.center
                        pygame.draw.rect(screen, RED_DECOR, temp_rect, border_radius=3)
                else:
                    back_rect = pygame.Rect(
                        0, 0, max(1, animated_width), card_rect.height
                    )
                    back_rect.center = card_rect.center
                    pygame.draw.rect(
                        screen, CARD_BACK_COLOR, back_rect, border_radius=3
                    )

                pygame.draw.rect(
                    screen,
                    OUTLINE_COLOR,
                    card_rect,
                    CARD_OUTLINE_THICKNESS,
                    border_radius=3,
                )
                draw_outline = False

                if progress >= 1.0:
                    indices_to_remove_from_animation.append(i)
                    if i < len(flipped):
                        flipped[i] = anim_data["target_state"]
                    else:
                        print(
                            f"Error: Index {i} out of bounds for flipped list (size {len(flipped)}) during animation end."
                        )

            elif (i < len(matched) and matched[i]) or (i < len(flipped) and flipped[i]):
                try:
                    img_surf = all_images[i]
                    img_orig_w, img_orig_h = img_surf.get_size()
                    card_inner_w = card_rect.width - 4
                    card_inner_h = card_rect.height - 4
                    if card_inner_w <= 0 or card_inner_h <= 0:
                        raise ValueError("Card inner size invalid")

                    scale = 1.0
                    if img_orig_w > 0 and img_orig_h > 0:
                        scale = min(
                            card_inner_w / img_orig_w, card_inner_h / img_orig_h
                        )
                    img_new_w = max(1, int(img_orig_w * scale))
                    img_new_h = max(1, int(img_orig_h * scale))

                    if img_new_w > 0 and img_new_h > 0:
                        scaled_img = pygame.transform.smoothscale(
                            img_surf, (img_new_w, img_new_h)
                        )
                        img_rect = scaled_img.get_rect(center=card_rect.center)
                        screen.blit(scaled_img, img_rect)
                    else:
                        raise ValueError("Static scaled image size zero")

                except IndexError:
                    print(
                        f"Error: Index {i} out of bounds for all_images (size {len(all_images)})"
                    )
                    pygame.draw.rect(
                        screen, RED_DECOR, card_rect.inflate(-4, -4), border_radius=3
                    )
                except Exception as e:
                    print(f"Err draw static img {i}: {e}")
                    pygame.draw.rect(
                        screen, RED_DECOR, card_rect.inflate(-4, -4), border_radius=3
                    )
            else:
                pygame.draw.rect(screen, CARD_BACK_COLOR, card_rect, border_radius=3)

            if draw_outline:
                pygame.draw.rect(
                    screen,
                    OUTLINE_COLOR,
                    card_rect,
                    CARD_OUTLINE_THICKNESS,
                    border_radius=3,
                )

        if indices_to_remove_from_animation:
            for index in indices_to_remove_from_animation:
                if index in animating_cards:
                    del animating_cards[index]
            if len(flipped_indices) == 2:
                idx1, idx2 = flipped_indices
                if idx1 not in animating_cards and idx2 not in animating_cards:
                    check_for_match()

    # Draw Info Panel
    # (No changes needed in info text drawing logic)
    if hiscore_rect and score_rect and time_rect:
        game_time_str = "0s"
        if start_time > 0 and not game_completed:
            if paused:
                elapsed_seconds = time_at_pause // 1000
            else:
                current_ticks_ingame = pygame.time.get_ticks()
                elapsed_ticks = current_ticks_ingame - start_time - total_paused_time
                elapsed_seconds = max(0, elapsed_ticks // 1000)
            game_time_str = f"{elapsed_seconds}s"
        elif game_completed:
            game_time_str = f"{total_time_taken}s"

        hiscore_label_text = f"Hi-score ({ROWS}x{COLS})"
        score_label_text = f"Score ({ROWS}x{COLS})"
        time_label_text = "Time"
        current_hi_score_display = (
            str(current_hi_score) if current_hi_score > 0 else "-"
        )

        sections = [
            {
                "lbl": hiscore_label_text,
                "val": current_hi_score_display,
                "r": hiscore_rect,
            },
            {"lbl": score_label_text, "val": str(click_count), "r": score_rect},
            {"lbl": time_label_text, "val": game_time_str, "r": time_rect},
        ]
        for s in sections:
            if s["r"].width <= 0 or s["r"].height <= 0:
                continue
            pygame.draw.rect(screen, BLACK, s["r"], border_radius=3)
            lbl_h = max(1, min(30, s["r"].height // 3))
            val_h = max(1, s["r"].height - lbl_h - 2)
            lbl_r = pygame.Rect(s["r"].left, s["r"].top, s["r"].width, lbl_h)
            lbl_s = SMALL_FONT.render(s["lbl"], True, TEXT_COLOR)
            lbl_sr = lbl_s.get_rect(center=lbl_r.center)
            screen.blit(lbl_s, lbl_sr)
            if val_h > 0:
                val_y = lbl_r.bottom + 2
                val_r = pygame.Rect(s["r"].left, val_y, s["r"].width, val_h)
                val_s = BUTTON_FONT.render(s["val"], True, TEXT_COLOR)
                val_sr = val_s.get_rect(center=val_r.center)
                screen.blit(val_s, val_sr)
            pygame.draw.rect(
                screen, OUTLINE_COLOR, s["r"], CARD_OUTLINE_THICKNESS, border_radius=3
            )

    # --- Control Button Drawing (Info Panel) ---
    if (
        mute_button_rect and pause_button_rect and restart_button_rect
    ):  # Use restart_button_rect now
        mute_sym = "🔇" if mute else "🔊"
        pause_sym_small = "▶️" if paused else "⏸️"
        restart_sym = "🔃"  # Restart symbol for info bar
        mute_offset = 6 if mute else 4
        pause_offset = 3
        restart_offset = 3  # Adjust vertical offset if needed for restart symbol

        # Define buttons with their respective symbols and rects
        buttons_info = [
            {
                "symbol": mute_sym,
                "rect": mute_button_rect,
                "offset": mute_offset,
                "scale": 1.0,
            },  # No scaling for mute/pause
            {
                "symbol": pause_sym_small,
                "rect": pause_button_rect,
                "offset": pause_offset,
                "scale": 1.0,
            },
            {
                "symbol": restart_sym,
                "rect": restart_button_rect,
                "offset": restart_offset,
                "scale": INFO_BAR_RESTART_SCALE,
            },  # Apply scaling to restart
        ]

        for btn in buttons_info:
            if btn["rect"].width <= 0 or btn["rect"].height <= 0:
                continue
            radius = btn["rect"].width // 2
            if radius <= 0:
                continue

            # Draw button circle background and outline
            pygame.draw.circle(screen, BLACK, btn["rect"].center, radius)
            pygame.draw.circle(
                screen,
                OUTLINE_COLOR,
                btn["rect"].center,
                radius,
                CARD_OUTLINE_THICKNESS * 2,
            )

            try:
                # Render the symbol using the standard (smaller) SYMBOL_FONT
                label_surf = SYMBOL_FONT.render(btn["symbol"], True, TEXT_COLOR)

                if label_surf.get_width() > 0:
                    # Apply scaling if needed (only for restart button)
                    if btn["scale"] != 1.0:
                        orig_w, orig_h = label_surf.get_size()
                        scaled_w = max(1, int(orig_w * btn["scale"]))
                        scaled_h = max(1, int(orig_h * btn["scale"]))
                        final_surf = pygame.transform.smoothscale(
                            label_surf, (scaled_w, scaled_h)
                        )
                    else:
                        final_surf = label_surf  # Use original surface if no scaling

                    # Get rect and position the potentially scaled symbol
                    label_rect = final_surf.get_rect(center=btn["rect"].center)
                    label_rect.centery += btn["offset"]  # Apply vertical offset
                    screen.blit(final_surf, label_rect.topleft)
                else:
                    print(
                        f"Warning: Info bar symbol '{btn['symbol']}' did not render. Drawing fallback '?'"
                    )
                    fb_surf = SYMBOL_FONT.render("?", True, WHITE)
                    fb_rect = fb_surf.get_rect(center=btn["rect"].center)
                    screen.blit(fb_surf, fb_rect)

            except Exception as e:
                print(f"Error rendering info bar button symbol '{btn['symbol']}': {e}")
                # Draw fallback '?' if rendering fails
                fb_surf = SYMBOL_FONT.render("?", True, WHITE)
                fb_rect = fb_surf.get_rect(center=btn["rect"].center)
                screen.blit(fb_surf, fb_rect)

    # Draw Pause Overlay and Menu if paused
    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 216))
        screen.blit(overlay, (0, 0))
        try:
            # Ensure layout has been calculated
            if (
                pause_menu_pause_symbol_rect is None
                or pause_menu_home_symbol_rect is None
            ):
                calculate_layouts()

            # Draw Pause Symbol
            if pause_menu_pause_symbol_rect:
                pause_s_str = "⏸️"
                pause_s_surf = LARGE_SYMBOL_FONT.render(pause_s_str, True, WHITE)
                if pause_s_surf.get_width() > 0:
                    screen.blit(pause_s_surf, pause_menu_pause_symbol_rect)
                else:
                    print(
                        f"Warning: Pause symbol '{pause_s_str}' did not render. Drawing fallback."
                    )
                    pygame.draw.rect(
                        screen, WHITE, pause_menu_pause_symbol_rect.inflate(-20, -20), 5
                    )
            else:
                pygame.draw.rect(
                    screen,
                    WHITE,
                    pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 50, 100, 100).inflate(
                        -20, -20
                    ),
                    5,
                )

            # Draw Home Symbol (on pause screen, using LARGE font, no scaling)
            if (
                pause_menu_home_symbol_rect
            ):  # This rect now represents the Home button's position
                try:
                    home_s_str = "🏠"
                    home_s_surf = LARGE_SYMBOL_FONT.render(
                        home_s_str, True, WHITE
                    )  # Render large

                    if home_s_surf.get_width() > 0:
                        # Blit the large home symbol at its calculated position
                        screen.blit(home_s_surf, pause_menu_home_symbol_rect)
                    else:
                        # Fallback if large home symbol fails
                        print(
                            f"Warning: Pause screen Home symbol '{home_s_str}' did not render. Drawing fallback."
                        )
                        fb_surf = LARGE_SYMBOL_FONT.render(
                            "H", True, WHITE
                        )  # Fallback 'H'
                        fb_rect = fb_surf.get_rect(
                            center=pause_menu_home_symbol_rect.center
                        )
                        if fb_surf.get_width() > 0:
                            screen.blit(fb_surf, fb_rect)
                        else:
                            pygame.draw.rect(
                                screen,
                                WHITE,
                                pause_menu_home_symbol_rect.inflate(-20, -20),
                                5,
                            )
                except Exception as e:
                    print(f"Error rendering/drawing pause screen home symbol: {e}")
                    pygame.draw.rect(
                        screen, WHITE, pause_menu_home_symbol_rect.inflate(-20, -20), 5
                    )
            else:  # Fallback drawing if rect calculation failed entirely
                pygame.draw.rect(
                    screen,
                    WHITE,
                    pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2 - 50, 100, 100).inflate(
                        -20, -20
                    ),
                    5,
                )

        except Exception as e:
            print(f"Error drawing large pause menu symbols: {e}")
            if pause_menu_pause_symbol_rect:
                pygame.draw.rect(
                    screen, WHITE, pause_menu_pause_symbol_rect.inflate(-20, -20), 5
                )
            if pause_menu_home_symbol_rect:  # Check the correct rect name here
                pygame.draw.rect(
                    screen, WHITE, pause_menu_home_symbol_rect.inflate(-20, -20), 5
                )


# --- draw_win_screen Function ---
# (No changes needed)
def draw_win_screen():
    """Draws the win screen overlay with stats and action buttons."""

    overlay_color = (0, 0, 0, 210)
    overlay_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surf.fill(overlay_color)
    screen.blit(overlay_surf, (0, 0))

    # Popup Box
    popup_w = max(350, WIDTH * 0.6)
    popup_h = max(300, HEIGHT * 0.6)
    popup_r = pygame.Rect(
        (WIDTH - popup_w) // 2, (HEIGHT - popup_h) // 2, popup_w, popup_h
    )
    pygame.draw.rect(screen, BLACK, popup_r, border_radius=10)
    pygame.draw.rect(
        screen, OUTLINE_COLOR, popup_r, CARD_OUTLINE_THICKNESS * 2, border_radius=10
    )

    # Title
    win_t_surf = BUTTON_FONT.render("Congrats! You win!", True, TEXT_COLOR)
    win_t_r = win_t_surf.get_rect(center=(popup_r.centerx, popup_r.top + 45))
    screen.blit(win_t_surf, win_t_r)

    # Close Button
    close_s = 35
    close_r = pygame.Rect(
        popup_r.right - close_s - 15, popup_r.top + 15, close_s, close_s
    )
    pygame.draw.rect(screen, BLACK, close_r, border_radius=5)
    pygame.draw.rect(
        screen, OUTLINE_COLOR, close_r, CARD_OUTLINE_THICKNESS, border_radius=5
    )
    close_t_surf = BUTTON_FONT.render("X", True, TEXT_COLOR)
    close_t_r = close_t_surf.get_rect(center=close_r.center)
    screen.blit(close_t_surf, close_t_r)

    # Stats Area
    stats_w = popup_w * 0.8
    stats_h = 130
    stats_r = pygame.Rect(
        popup_r.centerx - stats_w // 2, win_t_r.bottom + 30, stats_w, stats_h
    )
    pygame.draw.rect(screen, BLACK, stats_r, border_radius=5)
    pygame.draw.rect(
        screen, OUTLINE_COLOR, stats_r, CARD_OUTLINE_THICKNESS, border_radius=5
    )

    # Get the correct high score for the mode just played
    mode_hi_score = hi_scores.get((ROWS, COLS), 0)
    is_new_highscore = mode_hi_score == 0 or click_count < mode_hi_score

    # Display stats including grid size
    score_text = f"Your Score ({ROWS}x{COLS}): {click_count}"
    hi_score_text = (
        f"New Hi-Score ({ROWS}x{COLS}): {click_count}"
        if is_new_highscore
        else f"Hi-Score ({ROWS}x{COLS}): {mode_hi_score}"
    )
    time_text = f"Time Taken: {total_time_taken}s"

    stats_lines = [score_text, hi_score_text, time_text]
    line_spacing = 10
    line_height = INFO_FONT.get_linesize()
    total_text_height = (
        len(stats_lines) * line_height + (len(stats_lines) - 1) * line_spacing
    )
    start_draw_y = stats_r.centery - total_text_height // 2

    for i, line in enumerate(stats_lines):
        stats_surf = INFO_FONT.render(line, True, TEXT_COLOR)
        stats_rect = stats_surf.get_rect(
            centerx=stats_r.centerx, top=start_draw_y + i * (line_height + line_spacing)
        )
        screen.blit(stats_surf, stats_rect)

    btn_w = 120
    btn_h = 60
    btn_m = 40
    btns_y = popup_r.bottom - btn_h - 30
    total_btns_width = 2 * btn_w + btn_m
    btns_start_x = popup_r.centerx - total_btns_width // 2

    replay_r = pygame.Rect(btns_start_x, btns_y, btn_w, btn_h)
    home_r = pygame.Rect(btns_start_x + btn_w + btn_m, btns_y, btn_w, btn_h)

    # Replay Button
    replay_sym = "▶️"
    pygame.draw.rect(screen, BLACK, replay_r, border_radius=5)
    pygame.draw.rect(
        screen, OUTLINE_COLOR, replay_r, CARD_OUTLINE_THICKNESS * 2, border_radius=5
    )
    replay_surf = SYMBOL_FONT.render(replay_sym, True, TEXT_COLOR)
    replay_rect = replay_surf.get_rect(center=replay_r.center)
    replay_rect.centery += 3
    screen.blit(replay_surf, replay_rect)

    # Home Button
    home_sym = "🏠"
    pygame.draw.rect(screen, BLACK, home_r, border_radius=5)
    pygame.draw.rect(
        screen, OUTLINE_COLOR, home_r, CARD_OUTLINE_THICKNESS * 2, border_radius=5
    )
    home_surf = SYMBOL_FONT.render(home_sym, True, TEXT_COLOR)
    home_rect = home_surf.get_rect(center=home_r.center)
    home_rect.centery += 3
    screen.blit(home_surf, home_rect)

    return close_r, replay_r, home_r


# --- Animation/Logic Helper ---
# (No changes needed)
def start_flip_animation(index, direction):
    """Starts a flip animation for the card at the given index."""
    global animating_cards
    if 0 <= index < TOTAL_CARDS and index not in animating_cards:
        target_state = direction == "to_front"
        animating_cards[index] = {
            "start_time": time.time(),
            "direction": direction,
            "target_state": target_state,
        }
        if flip_sound:
            flip_sound.play()
    elif index in animating_cards:
        print(f"Warning: Tried to start animation for already animating card {index}.")
    else:
        print(
            f"Error: Invalid index {index} for start_flip_animation (Total cards: {TOTAL_CARDS})."
        )


def check_for_match():
    """Checks if the two currently selected cards match or mismatch, after animations finish."""
    global flipped_indices, matched, animating_cards, hi_scores
    if len(flipped_indices) == 2:
        idx1, idx2 = flipped_indices

        if not (0 <= idx1 < TOTAL_CARDS and 0 <= idx2 < TOTAL_CARDS):
            print(
                f"Error: Invalid indices in flipped_indices during match check: {idx1}, {idx2}. Total cards: {TOTAL_CARDS}"
            )
            flipped_indices = []
            return

        if idx1 not in animating_cards and idx2 not in animating_cards:
            try:
                if idx1 < len(all_images) and idx2 < len(all_images):
                    if all_images[idx1] == all_images[idx2]:
                        if idx1 < len(matched) and idx2 < len(matched):
                            matched[idx1] = True
                            matched[idx2] = True
                            print(f"Match found: Card {idx1} and {idx2}")
                            flipped_indices = []
                            check_win_condition()
                        else:
                            print(
                                f"Error: Indices {idx1}, {idx2} out of bounds for matched list (size {len(matched)})"
                            )
                            flipped_indices = []
                    else:
                        print(f"Mismatch: Card {idx1} and {idx2}")
                        if idx1 < len(flipped) and idx2 < len(flipped):
                            if flipped[idx1]:
                                start_flip_animation(idx1, "to_back")
                            if flipped[idx2]:
                                start_flip_animation(idx2, "to_back")
                            flipped_indices = []
                        else:
                            print(
                                f"Error: Indices {idx1}, {idx2} out of bounds for flipped list (size {len(flipped)}) on mismatch"
                            )
                            flipped_indices = []
                else:
                    print(
                        f"Error: Invalid image indices in flipped_indices after animation check: {idx1}, {idx2}. Image list size: {len(all_images)}"
                    )
                    flipped_indices = []
            except IndexError:
                print(
                    f"Error: IndexError checking match for indices {idx1}, {idx2}. Lists lengths - all_images: {len(all_images)}, matched: {len(matched)}, flipped: {len(flipped)}"
                )
                flipped_indices = []
            except Exception as e:
                print(f"Error during match check: {e}")
                import traceback

                traceback.print_exc()
                flipped_indices = []


def check_win_condition():
    """Checks if all cards are matched and updates game state if won."""
    global game_completed, show_win_popup, total_time_taken, hi_scores, current_hi_score
    if not matched or len(matched) != TOTAL_CARDS:
        print(
            f"Warning: Win condition check failed. Matched list invalid (size {len(matched)}, expected {TOTAL_CARDS})."
        )
        return

    if all(matched) and not game_completed:
        game_completed = True
        show_win_popup = True
        current_ticks = pygame.time.get_ticks()
        if start_time > 0:
            total_time_taken = max(
                0, (current_ticks - start_time - total_paused_time) // 1000
            )
        else:
            total_time_taken = 0
            print("Warning: Game completed but start_time was 0.")
        print(
            f"--- Game Won! ({ROWS}x{COLS}) Score: {click_count}, Time: {total_time_taken}s ---"
        )
        if win_sound:
            win_sound.play()
        mode_key = (ROWS, COLS)
        previous_hi_score = hi_scores.get(mode_key, 0)
        if previous_hi_score == 0 or click_count < previous_hi_score:
            print(
                f"New High Score for {ROWS}x{COLS}: {click_count} (Previous: {previous_hi_score})"
            )
            hi_scores[mode_key] = click_count
            current_hi_score = click_count
            save_highscore(ROWS, COLS)


# --- Main Execution ---


def run_game():
    """Initializes and runs the main game loop."""
    global WIDTH, HEIGHT, screen, game_state, click_count, start_time, game_completed, show_win_popup, total_time_taken, paused, mute, hi_scores, current_hi_score, flipped, matched, flipped_indices, time_at_pause, pause_start_time, total_paused_time, pause_menu_pause_symbol_rect, pause_menu_home_symbol_rect, last_displayed_time_sec, animating_cards, selected_rows, selected_cols, ROWS, COLS, TOTAL_CARDS, show_clear_confirmation, restart_button_rect  # Added restart_button_rect

    try:
        initialize_screen()
        load_potential_images()
        load_all_highscores()
        setup_current_game_images()
        calculate_layouts()
        load_and_play_music()
    except SystemExit:
        print("Exiting during initialization.")
        return
    except Exception as e:
        print(f"Initialization Error: {e}")
        import traceback

        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

    game_state = STATE_MAIN_MENU
    running = True
    clock = pygame.time.Clock()
    needs_redraw = True

    while running:
        current_time_ticks = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()
        current_time_sec = time.time()

        if game_state == STATE_OPTIONS and show_clear_confirmation:
            if (
                current_time_sec - clear_confirmation_start_time
                >= CLEAR_CONFIRMATION_DURATION
            ):
                show_clear_confirmation = False
                needs_redraw = True

        # Determine if redraw is needed
        animation_ongoing = bool(animating_cards)
        time_changed = False
        if (
            game_state == STATE_GAMEPLAY
            and not paused
            and not game_completed
            and start_time > 0
        ):
            current_display_sec = max(
                0, (current_time_ticks - start_time - total_paused_time) // 1000
            )
            if current_display_sec != last_displayed_time_sec:
                needs_redraw = True
                last_displayed_time_sec = current_display_sec
                time_changed = True

        if animation_ongoing or time_changed or paused:
            needs_redraw = True

        # Handle Events
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                initialize_screen(event.w, event.h)
                calculate_layouts()
                needs_redraw = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    needs_redraw = True

                    # --- Main Menu Click Handling ---
                    # (No changes needed)
                    if game_state == STATE_MAIN_MENU:
                        try:
                            title_rect_calc = TITLE_FONT.render(
                                "Memory Match!", True, TEXT_COLOR
                            ).get_rect(center=(WIDTH // 2, HEIGHT // 5))
                            btn_w, btn_h, btn_m = 300, 55, 25
                            total_button_height = 4 * btn_h + 3 * btn_m
                            start_y = title_rect_calc.bottom + max(
                                40,
                                (HEIGHT - title_rect_calc.bottom - total_button_height)
                                // 2,
                            )
                            play_rect_calc = pygame.Rect(
                                WIDTH // 2 - btn_w // 2, start_y, btn_w, btn_h
                            )
                            howto_rect_calc = pygame.Rect(
                                WIDTH // 2 - btn_w // 2,
                                start_y + (btn_h + btn_m),
                                btn_w,
                                btn_h,
                            )
                            options_rect_calc = pygame.Rect(
                                WIDTH // 2 - btn_w // 2,
                                start_y + 2 * (btn_h + btn_m),
                                btn_w,
                                btn_h,
                            )
                            quit_rect_calc = pygame.Rect(
                                WIDTH // 2 - btn_w // 2,
                                start_y + 3 * (btn_h + btn_m),
                                btn_w,
                                btn_h,
                            )
                            mute_radius = 32
                            mute_center_x = quit_rect_calc.right + btn_m + mute_radius
                            mute_center_y = quit_rect_calc.centery
                            mute_btn_rect_calc = pygame.Rect(
                                0, 0, mute_radius * 2, mute_radius * 2
                            )
                            mute_btn_rect_calc.center = (mute_center_x, mute_center_y)
                            if mute_btn_rect_calc.right > WIDTH - MARGIN:
                                mute_center_x = (
                                    quit_rect_calc.left - btn_m - mute_radius
                                )
                                mute_btn_rect_calc.center = (
                                    mute_center_x,
                                    mute_center_y,
                                )
                            menu_buttons = [
                                {"rect": play_rect_calc, "action": "play"},
                                {"rect": howto_rect_calc, "action": "how_to"},
                                {"rect": options_rect_calc, "action": "options"},
                                {"rect": quit_rect_calc, "action": "quit"},
                            ]
                            clicked_on_button = False
                            for btn_data in menu_buttons:
                                if btn_data["rect"].collidepoint(mouse_pos):
                                    print(
                                        f"Clicked on Main Menu Button: {btn_data['action']}"
                                    )
                                    if select_sound:
                                        select_sound.play()
                                    if btn_data["action"] == "play":
                                        reset_game_state()
                                        calculate_layouts()
                                        game_state = STATE_GAMEPLAY
                                        start_time = pygame.time.get_ticks()
                                        load_and_play_music()
                                    elif btn_data["action"] == "how_to":
                                        game_state = STATE_HOW_TO_PLAY
                                        calculate_layouts()
                                    elif btn_data["action"] == "options":
                                        game_state = STATE_OPTIONS
                                        calculate_layouts()
                                    elif btn_data["action"] == "quit":
                                        running = False
                                    clicked_on_button = True
                                    break
                            if (
                                not clicked_on_button
                                and mute_btn_rect_calc.collidepoint(mouse_pos)
                            ):
                                toggle_mute()
                        except Exception as e:
                            print(f"Err main menu click handling: {e}")
                            import traceback

                            traceback.print_exc()

                    # --- How To Play Click Handling ---
                    # (No changes needed)
                    elif game_state == STATE_HOW_TO_PLAY:
                        try:
                            if (
                                how_to_home_button_rect
                                and how_to_home_button_rect.collidepoint(mouse_pos)
                            ):
                                game_state = STATE_MAIN_MENU
                                show_clear_confirmation = False
                        except Exception as e:
                            print(f"Err how-to click handling: {e}")

                    # --- Options Click Handling ---
                    # (No changes needed)
                    elif game_state == STATE_OPTIONS:
                        try:
                            home_clicked = (
                                options_home_button_rect
                                and options_home_button_rect.collidepoint(mouse_pos)
                            )
                            clear_clicked = (
                                clear_scores_button_rect
                                and clear_scores_button_rect.collidepoint(mouse_pos)
                            )
                            option_clicked = False
                            if home_clicked:
                                game_state = STATE_MAIN_MENU
                                show_clear_confirmation = False
                            elif clear_clicked:
                                print("Clear Highscores button clicked!")
                                clear_all_highscores()
                                show_clear_confirmation = True
                                clear_confirmation_start_time = time.time()
                            else:
                                for (r, c), rect in options_rects.items():
                                    if rect.collidepoint(mouse_pos):
                                        if selected_rows != r or selected_cols != c:
                                            print(f"Selected new grid size: {r}x{c}")
                                            selected_rows = r
                                            selected_cols = c
                                            current_hi_score = hi_scores.get(
                                                (selected_rows, selected_cols), 0
                                            )
                                        option_clicked = True
                                        break
                        except Exception as e:
                            print(f"Err options click handling: {e}")
                            import traceback

                            traceback.print_exc()

                    # --- Gameplay Click Handling ---
                    elif game_state == STATE_GAMEPLAY:
                        # --- Pause Screen Click Handling ---
                        if paused:
                            clicked_on_gui_button = False
                            # Check small corner buttons first (Mute and Pause - Restart is NOT clickable when paused)
                            if mute_button_rect and mute_button_rect.collidepoint(
                                mouse_pos
                            ):
                                if select_sound:
                                    select_sound.play()
                                toggle_mute()
                                clicked_on_gui_button = True
                            elif pause_button_rect and pause_button_rect.collidepoint(
                                mouse_pos
                            ):
                                # Clicking the small pause button again *unpauses*
                                if select_sound:
                                    select_sound.play()
                                if pause_start_time > 0:
                                    total_paused_time += (
                                        pygame.time.get_ticks() - pause_start_time
                                    )
                                paused = False
                                pause_start_time = 0
                                print("Game Resumed (via small button)")
                                clicked_on_gui_button = True

                            # If no corner button was clicked, check the central pause menu buttons
                            if not clicked_on_gui_button:
                                # Click Pause Symbol -> Unpause
                                if (
                                    pause_menu_pause_symbol_rect
                                    and pause_menu_pause_symbol_rect.collidepoint(
                                        mouse_pos
                                    )
                                ):
                                    if select_sound:
                                        select_sound.play()
                                    if pause_start_time > 0:
                                        total_paused_time += (
                                            pygame.time.get_ticks() - pause_start_time
                                        )
                                    paused = False
                                    pause_start_time = 0
                                    print("Game Resumed (via large button)")
                                # Click Home Symbol -> Go to Main Menu
                                elif (
                                    pause_menu_home_symbol_rect
                                    and pause_menu_home_symbol_rect.collidepoint(
                                        mouse_pos
                                    )
                                ):  # Check the renamed rect
                                    if select_sound:
                                        select_sound.play()
                                    print("Going Home (Pause Menu)...")
                                    reset_game_state()  # Reset score etc.
                                    paused = False  # Ensure unpaused
                                    game_state = STATE_MAIN_MENU  # Go to menu

                        # --- Win Popup Click Handling ---
                        # (No changes needed)
                        elif game_completed and show_win_popup:
                            try:
                                popup_w = max(350, WIDTH * 0.6)
                                popup_h = max(300, HEIGHT * 0.6)
                                popup_r = pygame.Rect(
                                    (WIDTH - popup_w) // 2,
                                    (HEIGHT - popup_h) // 2,
                                    popup_w,
                                    popup_h,
                                )
                                close_s = 35
                                close_r_calc = pygame.Rect(
                                    popup_r.right - close_s - 15,
                                    popup_r.top + 15,
                                    close_s,
                                    close_s,
                                )
                                btn_w, btn_h, btn_m = 120, 60, 40
                                btns_y = popup_r.bottom - btn_h - 30
                                total_btns_width = 2 * btn_w + btn_m
                                btns_start_x = popup_r.centerx - total_btns_width // 2
                                replay_r_calc = pygame.Rect(
                                    btns_start_x, btns_y, btn_w, btn_h
                                )
                                home_r_calc = pygame.Rect(
                                    btns_start_x + btn_w + btn_m, btns_y, btn_w, btn_h
                                )

                                if close_r_calc.collidepoint(mouse_pos):
                                    if select_sound:
                                        select_sound.play()
                                    show_win_popup = False
                                elif replay_r_calc.collidepoint(mouse_pos):
                                    if select_sound:
                                        select_sound.play()
                                    reset_game_state()
                                    calculate_layouts()
                                    start_time = pygame.time.get_ticks()
                                elif home_r_calc.collidepoint(mouse_pos):
                                    if select_sound:
                                        select_sound.play()
                                    reset_game_state()
                                    game_state = STATE_MAIN_MENU
                            except Exception as e:
                                print(f"Err win popup click: {e}")

                        # --- Post-Win Screen Click Handling --- (Popup Closed)
                        # (Restart button should function here too)
                        elif game_completed and not show_win_popup:
                            try:
                                if mute_button_rect and mute_button_rect.collidepoint(
                                    mouse_pos
                                ):
                                    if select_sound:
                                        select_sound.play()
                                    toggle_mute()
                                # Check RESTART button click after win
                                elif (
                                    restart_button_rect
                                    and restart_button_rect.collidepoint(mouse_pos)
                                ):
                                    if select_sound:
                                        select_sound.play()
                                    print("Restarting Level (Post-Win)...")
                                    reset_game_state()
                                    calculate_layouts()
                                    start_time = pygame.time.get_ticks()
                            except Exception as e:
                                print(f"Err post-win click: {e}")

                        # --- Active Gameplay Clicks --- (Not Paused, Not Won)
                        elif not game_completed:
                            try:
                                button_clicked = False
                                # Control Button Clicks (Mute, Pause, RESTART)
                                if mute_button_rect and mute_button_rect.collidepoint(
                                    mouse_pos
                                ):
                                    if select_sound:
                                        select_sound.play()
                                    toggle_mute()
                                    button_clicked = True
                                elif (
                                    pause_button_rect
                                    and pause_button_rect.collidepoint(mouse_pos)
                                ):
                                    if select_sound:
                                        select_sound.play()
                                    if (
                                        not paused
                                    ):  # Can only pause if not already paused
                                        time_at_pause = 0
                                        if start_time > 0:
                                            time_at_pause = max(
                                                0,
                                                current_time_ticks
                                                - start_time
                                                - total_paused_time,
                                            )
                                        pause_start_time = current_time_ticks
                                        paused = True
                                        # Clear half-selected pair logic (same as before)
                                        if len(flipped_indices) == 1:
                                            idx_to_clear = flipped_indices[0]
                                            if idx_to_clear in animating_cards:
                                                del animating_cards[idx_to_clear]
                                            if 0 <= idx_to_clear < len(flipped):
                                                flipped[idx_to_clear] = False
                                            flipped_indices = []
                                        elif len(flipped_indices) == 2:
                                            idx1, idx2 = flipped_indices
                                            if (
                                                idx1 not in animating_cards
                                                and idx2 not in animating_cards
                                            ):
                                                if 0 <= idx1 < len(flipped):
                                                    flipped[idx1] = False
                                                if 0 <= idx2 < len(flipped):
                                                    flipped[idx2] = False
                                            elif idx1 in animating_cards:
                                                del animating_cards[idx1]
                                                if 0 <= idx1 < len(flipped):
                                                    flipped[idx1] = False
                                            elif idx2 in animating_cards:
                                                del animating_cards[idx2]
                                                if 0 <= idx2 < len(flipped):
                                                    flipped[idx2] = False
                                            flipped_indices = []
                                        print(
                                            f"Game Paused at {time_at_pause / 1000:.1f}s elapsed"
                                        )
                                    button_clicked = True
                                # Check RESTART button click
                                elif (
                                    restart_button_rect
                                    and restart_button_rect.collidepoint(mouse_pos)
                                ):
                                    if select_sound:
                                        select_sound.play()
                                    print("Restarting Level (Info Bar)...")
                                    reset_game_state()
                                    calculate_layouts()
                                    start_time = (
                                        pygame.time.get_ticks()
                                    )  # Start timer immediately
                                    button_clicked = True

                                # Card Clicks (only if no button clicked)
                                if not button_clicked:
                                    if len(flipped_indices) < 2:
                                        if (
                                            cards_rects
                                            and 0 <= len(matched) == TOTAL_CARDS
                                            and 0 <= len(flipped) == TOTAL_CARDS
                                        ):
                                            clicked_card_index = -1
                                            for i, card_rect in enumerate(cards_rects):
                                                if card_rect.collidepoint(mouse_pos):
                                                    clicked_card_index = i
                                                    break
                                            if clicked_card_index != -1:
                                                i = clicked_card_index
                                                is_card_matched = matched[i]
                                                is_card_already_flipped = (
                                                    i in flipped_indices
                                                )
                                                is_card_animating = i in animating_cards
                                                if (
                                                    not is_card_matched
                                                    and not is_card_already_flipped
                                                    and not is_card_animating
                                                ):
                                                    flipped_indices.append(i)
                                                    start_flip_animation(i, "to_front")
                                                    if not start_time:
                                                        start_time = (
                                                            pygame.time.get_ticks()
                                                        )
                                                    click_count += 1
                                                    print(
                                                        f"Card {i} flipped. Score: {click_count}. Flipped indices: {flipped_indices}"
                                                    )
                                        else:
                                            print(
                                                "Warning: Card interaction attempt while lists invalid."
                                            )
                            except Exception as e:
                                print(f"Err gameplay click/card logic: {e}")
                                import traceback

                                traceback.print_exc()

        # Game Logic
        # (No changes needed)
        if game_state == STATE_GAMEPLAY and not paused and not game_completed:
            if len(flipped_indices) == 2:
                idx1, idx2 = flipped_indices
                if idx1 not in animating_cards and idx2 not in animating_cards:
                    check_for_match()

        # Drawing based on current game state
        if needs_redraw:
            try:
                screen.fill(BLACK)
                if game_state == STATE_MAIN_MENU:
                    draw_main_menu()
                elif game_state == STATE_HOW_TO_PLAY:
                    draw_how_to_play()
                elif game_state == STATE_OPTIONS:
                    draw_options_menu()
                elif game_state == STATE_GAMEPLAY:
                    draw_game_screen()  # Draws cards, info panel, buttons, and pause overlay if needed
                    if game_completed and show_win_popup:
                        draw_win_screen()  # Draw win screen overlay

                pygame.display.flip()
                needs_redraw = False
            except Exception as e:
                print(f"--- ERROR DURING DRAWING ---")
                print(f"Game State: {game_state}, Error: {e}")
                import traceback

                traceback.print_exc()
                needs_redraw = True

        # Frame Limiting
        clock.tick(60)

    # Clean exit
    pygame.quit()
    print("Game exited.")
    sys.exit()


# Start the Game
if __name__ == "__main__":
    try:
        run_game()
    except SystemExit:
        print("Exiting program normally.")
    except Exception as e:
        print(f"\n--- UNEXPECTED ERROR IN MAIN ---")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Details: {e}")
        import traceback

        print("\n--- Traceback ---")
        traceback.print_exc()
        print("-----------------\n")
        try:
            pygame.quit()
        except:
            pass
        sys.exit(1)
