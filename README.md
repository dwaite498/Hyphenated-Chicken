# Hyphenated-Chicken
A real-time strategy game with 4X elements.

## Version: 0.6.0
- Mouse-based: Left-click selects (Shift for multi-select), right-click moves scouts.
- 'Build' button/menu (B shortcut) works when colony selected; builds Scout (5 metal), Constructor (25 metal).
- Sidebar UI (800x600): 600x600 board, 200px right panel for HUD/buttons.
- Startup page with guide; game waits until 'Start Game'.
- Combat: Adjacent units/buildings deal 1 damage/sec (Scout 5 HP, Enemy 10 HP, Colony 20 HP).
- Game over screen with 'Restart' if no colonies.
- Constructor: 2 HP, builds colony on minerals (30 sec, consumed, site vulnerable).
- 'Space' pauses, 'D' toggles debug, hover for tile info.

Run with: `python src/main.py`
