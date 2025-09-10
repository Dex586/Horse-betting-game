import tkinter as tk
import random
import os
import time
import base64


# --- Use hidden, encoded file for balance ---
if os.name == "nt":
    BALANCE_FILE = "balance.dat"
else:
    BALANCE_FILE = ".balance.dat"

def save_balance(self):
    try:
        encoded = base64.b64encode(str(self.balance).encode())
        with open(BALANCE_FILE, "wb") as f:
            f.write(encoded)
        # Hide on Windows
        if os.name == "nt":
            os.system(f'attrib +h {BALANCE_FILE}')
    except Exception as e:
        print("Error saving balance:", e)

def load_balance(self):
    if os.path.exists(BALANCE_FILE):
        try:
            with open(BALANCE_FILE, "rb") as f:
                data = f.read()
                bal = int(base64.b64decode(data).decode())
                return bal if bal > 0 else 100
        except:
            return 100
    return 100


# --- Horse Data (name, weight, colour) ---
HORSES = [
    ("Silence Suzuka", 0.35, "#228B22"),
    ("Special Week", 0.25, "#9370DB"),
    ("Tokai Teio", 0.20, "#1E90FF"),
    ("Gold Ship", 0.18, "#FFFFFF"),
    ("Haru Urara", 0.05, "#FF69B4"),
    ("Seabiscuit", 0.15, "#000080"),
    ("War Admiral", 0.12, "#800000"),
    ("Secretariat", 0.10, "#4169E1"),
    ("Phar Lap", 0.08, "#B22222"),
    ("Manhattan Cafe", 0.07, "#000000"),
    ("Narita Brian", 0.06, "#191970"),
    ("Symboli Rudolf", 0.09, "#8B4513"),
    ("Grass Wonder", 0.08, "#2E8B57"),
    ("Taiki Shuttle", 0.07, "#FF8C00"),
    ("Deep Impact", 0.20, "#0000CD"),
    ("Vodka", 0.12, "#2F4F4F"),
    ("Daiwa Scarlet", 0.10, "#DC143C"),
    ("El Condor Pasa", 0.11, "#333333"),
]

TRACK_PIXELS = 3000
LEFT_MARGIN = 60
STEP_MIN, STEP_MAX = 1, 3
BALANCE_FILE = "balance.txt"

class HorseRaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Horse Racing Simulator")
        self.balance = self.load_balance()
        self.bet_horse = None
        self.bet_amount = 0

        self._build_ui()
        self.show_betting_screen()

    # --- Balance Persistence ---
    def load_balance(self):
        if os.path.exists(BALANCE_FILE):
            try:
                with open(BALANCE_FILE, "r") as f:
                    bal = int(f.read().strip())
                    return bal if bal > 0 else 100
            except:
                return 100
        return 100

    def save_balance(self):
        with open(BALANCE_FILE, "w") as f:
            f.write(str(self.balance))

    # --- UI ---
    def _build_ui(self):
        self.top = tk.Frame(self.root, bg="green")
        self.top.pack(fill="x")

        self.balance_label = tk.Label(self.top, text=f"Balance: ${self.balance}", font=("Arial", 14), bg="green", fg="white")
        self.balance_label.pack(side="left", padx=10, pady=5)

        self.comment_text = tk.Text(self.root, height=5, state="disabled", bg="black", fg="white", font=("Arial", 11))
        self.comment_text.pack(fill="x")

        self.canvas = tk.Canvas(self.root, width=1200, height=700, bg="green")
        self.canvas.pack(fill="both", expand=True)

        self.skip_btn = tk.Button(self.root, text="Skip", command=self.skip)
        self.skip_btn.pack(side="top", anchor="ne", padx=5, pady=5)

    def show_betting_screen(self):
        self.canvas.delete("all")
        self.comment_text.config(state="normal")
        self.comment_text.delete("1.0", "end")
        self.comment_text.insert("end", "Place your bets!\n")
        self.comment_text.config(state="disabled")

        self.bet_frame = tk.Frame(self.canvas, bg="white")
        self.bet_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.bet_frame, text="Choose your horse:", font=("Arial", 14)).grid(row=0, column=0, columnspan=2)

        self.odds = self.calculate_odds()

        for i, (name, weight, color) in enumerate(HORSES):
            odds = self.odds[name]
            tk.Button(self.bet_frame, text=f"{i+1}. {name} ({odds})", command=lambda n=name: self.choose_horse(n), width=30).grid(row=(i//2)+1, column=i%2, padx=5, pady=2)

        tk.Label(self.bet_frame, text="Bet amount:").grid(row=11, column=0)
        self.bet_entry = tk.Entry(self.bet_frame)
        self.bet_entry.grid(row=11, column=1)

        for idx, amt in enumerate([50, 100, 200]):
            tk.Button(self.bet_frame, text=f"${amt}", command=lambda a=amt: self.set_bet(a)).grid(row=12, column=idx)

        tk.Button(self.bet_frame, text="Start Race", command=self.start_race).grid(row=13, column=0, columnspan=2, pady=10)

    def choose_horse(self, name):
        self.bet_horse = name
        self._log_comment(f"Selected horse: {name}")

    def set_bet(self, amt):
        self.bet_entry.delete(0, "end")
        self.bet_entry.insert(0, str(amt))

    # --- Odds ---
    def calculate_odds(self):
        total_weight = sum(w for _, w, _ in HORSES)
        odds = {}
        for name, weight, _ in HORSES:
            prob = weight / total_weight
            frac = (1 - prob) / prob
            odds[name] = self.to_fraction(frac)
        return odds

    def to_fraction(self, x):
        if abs(x - 1) < 0.1:
            return "Evs"
        num = round(x * 2)
        den = 2
        while num % 2 == 0 and den % 2 == 0:
            num //= 2
            den //= 2
        return f"{num}/{den}"

    # --- Race Logic ---
    def start_race(self):
        if not self.bet_horse:
            self._log_comment("No horse selected!")
            return
        try:
            self.bet_amount = int(self.bet_entry.get())
        except:
            self.bet_amount = 100
        if self.bet_amount > self.balance:
            self._log_comment("Not enough balance!")
            return

        self.balance -= self.bet_amount
        self.balance_label.config(text=f"Balance: ${self.balance}")

        self.bet_frame.destroy()
        self.reset_race()
        self.running = True
        self.start_time = time.time()
        self._tick()

    def reset_race(self):
        self.canvas.delete("all")
        self.positions = {name: 0 for name, _, _ in HORSES}
        self.rects, self.labels, self.nums = {}, {}, {}
        self.finish_times, self.finish_order, self.margins = {}, [], {}
        self.finish_overshoot = {}

        spacing = 30
        for i, (name, weight, color) in enumerate(HORSES):
            y = 50 + i * spacing
            rect = self.canvas.create_rectangle(LEFT_MARGIN, y, LEFT_MARGIN + 20, y + 15, fill=color)
            num_color = "black" if color.lower() in ("#ffffff", "#dddddd", "#ffffcc") else "white"
            num = self.canvas.create_text(LEFT_MARGIN + 10, y + 7, text=str(i + 1), fill=num_color, font=("Arial", 8, "bold"))
            label = self.canvas.create_text(LEFT_MARGIN - 40, y + 7, text=name, fill="white", font=("Arial", 9), anchor="e")

            self.rects[name] = rect
            self.labels[name] = label
            self.nums[name] = num

    def _tick(self):
        if not self.running:
            return

        for h, w, c in HORSES:
            if h not in self.finish_times:
                if random.random() < w:
                    step = random.randint(STEP_MIN, STEP_MAX)
                    self.positions[h] += step
                if self.positions[h] >= TRACK_PIXELS:
                    finish_time = time.time() - self.start_time
                    self.finish_times[h] = finish_time
                    self.finish_order.append(h)
                    self._check_finish(h)
                    self.finish_overshoot[h] = TRACK_PIXELS + random.randint(15, 30)
            else:
                target = self.finish_overshoot[h]
                if self.positions[h] < target:
                    self.positions[h] += 1

            stop_at = self.finish_overshoot.get(h, self.positions[h])
            draw_pos = min(self.positions[h], stop_at)
            dx = LEFT_MARGIN + draw_pos - self.canvas.coords(self.rects[h])[0]
            self.canvas.move(self.rects[h], dx, 0)
            self.canvas.move(self.nums[h], dx, 0)
            self.canvas.move(self.labels[h], dx, 0)

        if len(self.finish_order) == len(HORSES):
            self.running = False
            self._show_leaderboard()
        else:
            self.root.after(35, self._tick)

    def skip(self):
        if not getattr(self, 'running', False):
            return
        now = time.time() - self.start_time
        for h, w, c in HORSES:
            if h not in self.finish_times:
                self.finish_times[h] = now + random.uniform(0.01, 0.2)
                self.finish_order.append(h)
                self._check_finish(h)
                self.finish_overshoot[h] = TRACK_PIXELS + random.randint(15, 30)
            self.positions[h] = self.finish_overshoot[h]
        self.running = False
        self._show_leaderboard()

    def _check_finish(self, horse_name):
        idx = len(self.finish_order) - 1
        if idx == 0:
            self.margins[horse_name] = "–"
        else:
            prev = self.finish_order[idx - 1]
            gap = self.finish_times[horse_name] - self.finish_times[prev]
            lengths = gap / 0.2  # 0.2 seconds ≈ 1 length

            if lengths < 0.05:
                margin = "Photo Finish"
            elif lengths < 0.25:
                margin = "Nose"
            elif lengths < 0.5:
                margin = "Head"
            elif lengths < 1.0:
                margin = "Neck"
            else:
                margin = f"{round(lengths)} lengths"
            self.margins[horse_name] = margin

    def _show_leaderboard(self):
        board = tk.Toplevel(self.root)
        board.title("Results")
        text = tk.Text(board, width=60, height=22)
        text.pack()
        for i, h in enumerate(self.finish_order, start=1):
            time_s = self.finish_times[h]
            text.insert("end", f"{i}. {h}  -  {time_s:.2f}s  ({self.margins[h]})\n")
        text.config(state="disabled")

        winner = self.finish_order[0]
        if winner == self.bet_horse:
            payout_frac = self.odds[winner]
            payout = self.calculate_payout(self.bet_amount, payout_frac)
            self.balance += payout
            self._log_comment(f"You won! Payout: ${payout}")
        else:
            self._log_comment("You lost the bet.")

        if self.balance <= 0:
            self.balance = 100
            self._log_comment("Balance reset to $100.")

        self.balance_label.config(text=f"Balance: ${self.balance}")
        self.save_balance()
        board.after(5000, lambda: (board.destroy(), self.show_betting_screen()))

    def calculate_payout(self, stake, odds_str):
        if odds_str == "Evs":
            return stake * 2
        num, den = map(int, odds_str.split("/"))
        return stake + (stake * num // den)

    def _log_comment(self, msg):
        self.comment_text.config(state="normal")
        self.comment_text.insert("end", msg + "\n")
        self.comment_text.see("end")
        self.comment_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = HorseRaceApp(root)
    root.mainloop()
