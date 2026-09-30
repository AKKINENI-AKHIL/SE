# Real-Time Fruit Slice Game - Completed Tasks

This is the completed Pygame Fruit Ninja-style assignment.

## Tasks completed

### Task 1 - Refine Collision Detection
`game/fruit.py`

Fast swipes are handled by checking the whole line segment between the
previous mouse position and the current mouse position against the fruit
circle. This prevents a swipe from jumping over a fruit without registering.

### Task 2 - Implement Game Over Condition
`game/game_engine.py`

The game now displays a full-screen Game Over overlay containing the final
score and waits for keyboard input instead of only printing to the console.

Game Over occurs when:
- a bomb is sliced, or
- all three lives are lost.

### Task 3 - Add Replay Option
`game/game_engine.py`

After Game Over:
- `1` = Easy
- `2` = Medium
- `3` = Hard
- `E`, `Q`, or `Esc` = Exit

Each difficulty changes spawn rate, bomb probability, and fruit launch speed.

### Task 4 - Add Sound Feedback
`game/game_engine.py`

Three sound effects are generated at runtime:
- fruit slice
- bomb hit
- game over

No external audio files are required. If the machine has no usable audio
device, the game continues silently rather than crashing.

## Run

```bash
pip install -r requirements.txt
python main.py
```
