Project: Memory Match Game (Pygame)

Short goal for an AI editing this repo
- Keep the game's single-file design (`Match_Game.py`) working. Small, careful fixes only.
- Preserve runtime behavior: image loading from `assets/`, highscore files under `assets/` (named like `highscore_3x4.txt`), and sound/music handling.

Big-picture architecture (what to know quickly)
- Single-entrypoint: `Match_Game.py` (runs a Pygame loop). `old_program.py` is an older reference implementation.
- Assets: `assets/` contains card images `image01.png`..`image018.png` (various names supported), music (`.mp3`) and sounds (`.wav`), and highscore files. The game searches for image files using both `image{i}.png/jpg` and `image0{i}.png/jpg` patterns.
- UI/layout: layouts are computed at runtime by `calculate_layouts()` and stored in module-level Rects (e.g., `cards_rects`, `mute_button_rect`). Drawing functions rely on those rects and must call `calculate_layouts()` after any change to WIDTH/HEIGHT or grid selection.
- State machine: `STATE_MAIN_MENU`, `STATE_HOW_TO_PLAY`, `STATE_OPTIONS`, `STATE_GAMEPLAY` with central loop in `run_game()`.

Key files & responsibilities
- `Match_Game.py` — full game. Important functions to inspect when editing:
  - `run_game()` — initialization, main loop, event handling, state transitions.
  - `calculate_layouts()` — computes all clickable rects; call this after window resize or grid changes.
  - `load_potential_images()` / `setup_current_game_images()` — image discovery and deck creation. Keep file lookup patterns intact.
  - `start_flip_animation()` / `check_for_match()` / `check_win_condition()` — core game logic for flips and scoring.
  - `load_all_highscores()` / `save_highscore()` / `clear_all_highscores()` — persistence (plain-text per-mode files).
- `old_program.py` — legacy code safe to reference for intent, but do not wire into the main flow.
- `README.md` — run instructions; may be out-of-date for current asset naming but useful for intent.

Run / debug steps (Windows / PowerShell)
1) Ensure Python 3.x and Pygame are installed: pip install pygame
2) From repo root run:
   python Match_Game.py

If editing: run the script in a debugger or insert targeted print/logging. The program prints warnings when assets are missing (useful for diagnosing failures).

Project-specific conventions and gotchas for code edits
- Single-file game: keep changes localized. Avoid splitting logic into many new modules unless you update imports and run the game.
- Assets lookup:
  - Images: code tries `assets/image{i}.png`, `assets/image{i}.jpg`, `assets/image0{i}.png`, `assets/image0{i}.jpg` for i=1..36. Add new images into `assets/` with one of those patterns.
  - Highscores: filenames are `assets/highscore_{rows}x{cols}.txt` (HI_SCORE_FILE_BASE = "assets/highscore"). Do not change that base unless updating `get_highscore_filename()`.
- Fonts & symbols: the repo bundles `NotoSansSymbols2-Regular.ttf` — code falls back to system fonts (Segoe UI Symbol) if missing. When changing UI symbol strings (emoji), respect font fallbacks and scale used in `draw_*` functions.
- Layout calculations: many UI rects are computed and stored globally. After any state or window size change ensure `calculate_layouts()` is invoked to avoid None/zero sized rects and click-miss issues.
- Error handling: the code prints warnings/fatals and exits on missing critical assets (no card images, missing symbol font fallback). When modifying startup, mirror these checks to keep behavior consistent.

Examples from code (use these patterns when editing)
- To read highscores for 4x4: use load_highscore(4,4) or read `assets/highscore_4x4.txt`.
- To add a new grid option: update `RECTANGULAR_GRIDS` / `SQUARE_GRIDS` and ensure UI layout accounts for it (buttons created in `calculate_layouts()`).
- To force a layout recalculation after changing `selected_rows/cols`:
  selected_rows, selected_cols = r, c
  calculate_layouts()

Testing changes quickly
- Run `python Match_Game.py` and look at stdout for debug prints about missing assets, highscore reads, or font loading issues.
- Use a small set of images in `assets/` (image01..image06) to let `load_potential_images()` populate `potential_unique_images`.

What not to change without tests
- The flip animation timing/math (FLIP_ANIMATION_DURATION) and the way `animating_cards` toggles `flipped[]` at animation end — subtle bugs here break gameplay.
- Global state names (many functions reference globals). If you refactor into classes, do it in a single, isolated change and test manually.

Next steps for me
- I can merge or refine this guidance with any existing `.github/copilot-instructions.md` you have or expand sections (run/debug commands, quick tests). Tell me which sections you'd like expanded.
