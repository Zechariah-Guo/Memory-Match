# Memory Match Game

A simple memory-card matching game built with Python and Pygame. Flip cards to find matching pairs, choose different grid sizes, track your score and time, and try to beat the high scores.

![Menu Image](assets\Menu-Image.png)

## Features

- Classic memory match gameplay
- Multiple board sizes, including 3x4, 4x4, 4x5, 5x6, and 6x6
- Pause, restart, and mute controls
- High score tracking for each grid size
- Sound effects and background music when assets are available

![Gameplay Image](assets\all_flipped.png)

## Requirements

- Python 3.8+
- pip

## Installation

Clone the repository and create a virtual environment before installing anything:

```bash
git clone <repository-url>
cd MemoryMatchGame
python -m venv .venv
```

Activate the virtual environment:

- Windows (PowerShell):
  ```bash
  .\.venv\Scripts\Activate.ps1
  ```
- Windows (Command Prompt):
  ```bash
  .\.venv\Scripts\activate.bat
  ```

Then install the dependencies inside the virtual environment:

```bash
python -m pip install -r requirements.txt
```

## Running the Game

Start the game with:

```bash
python main.py
```

## Controls

- Click a card to flip it over
- Match two identical cards to clear them
- Use the on-screen buttons to:
  - Start a game
  - Open the How to Play screen
  - Change options
  - Pause or restart the round
  - Mute audio
- Use your mouse for all interactions

## Project Structure

- `main.py` - Main game entry point
- `assets/` - Game images, sounds, music, and high score files
- `requirements.txt` - Python dependencies
- `planning/` - Project planning notes

## Notes

1. If some audio or image assets are missing, the game will usually still launch and warn you in the terminal instead of crashing.
2. .msi coming soon
