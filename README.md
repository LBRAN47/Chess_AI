# Chess AI (Python + Pygame)

This is a small chess engine I built in Python. It includes full move generation, a minimax opponent with alpha-beta pruning, and a simple Pygame interface to play against it. The goal of the project was to learn more about search algorithms, game trees, and how to structure a larger Python program.

---

## Features

- Full legal move generation (including castling, en passant, promotion)
- Turn handling, check/checkmate detection, stalemates
- Minimax search with alpha-beta pruning
- Basic evaluation based on Michniewski's Simplified Evaluation Function
- Pygame GUI for playing against the engine or a human opponent

---

## How to Run

Follow these steps to run the chess engine locally.

## 1. Check your Python version
Make sure you have Python 3.10 or newer installed.

```bash
python --version
```
or:
```
python3 --version
```
## 2. Create a Virutal Environment (Optional)

### MacOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```
### Windows
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Game
```bash
python main.py --GUI
```
or:
```bash
python3 main.py --GUI
```




