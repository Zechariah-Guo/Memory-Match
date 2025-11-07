# Memory Match Game

A classic memory matching card game built with Pygame.

## Features

- 4×3 grid of cards (6 matching pairs)
- Visual feedback for matches
- Time-delayed card flipping
- Simple, clean interface

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Ensure Python 3.x is installed
2. Install Pygame: pip install pygame
3. Prepare 6 image files named `image1.jpg` through `image6.jpg` in the same directory

## How to Play

1. Run the script: python Match_Game.py
2. Click on cards to flip them
3. Find matching pairs of images
4. Match all pairs to win

## Controls

- Mouse: Click on cards to flip them
- Close window to exit game

## Customization

To modify the game:

- Change `WIDTH` and `HEIGHT` for different window sizes
- Adjust `COLS` and `ROWS` for different grid sizes
- Modify `CARD_WIDTH` and `CARD_HEIGHT` for different card sizes
- Change `delay` to adjust flip timing

## Troubleshooting

- If images don't load:
- Ensure image files are in the correct directory
- Verify filenames match exactly (`image1.jpg`, etc.)
- Check image file formats are supported by Pygame

##To-Do

Sound effects (click sound effect for pressing buttons (like minecraft button click sound?) and swoosh sound effect for when cards flip (they should play the click sound when pressed, just the whoosh sound))

Also add sound effect for when you win?

Clean up the code. Get rid of suspicious comments and fix formatting

Need up to image018. Currently up to image06.

