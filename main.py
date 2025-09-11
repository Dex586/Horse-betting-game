import tkinter as tk
import random
import os
import time

from constants import TRACK_PIXELS, LEFT_MARGIN, STEP_MIN, STEP_MAX, BALANCE_FILE
from horse_data import HORSES


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
            self.bet_amount = 0

        if self.bet_amount <= 0:
            self._log_comment("Bet amount must be a positive number.") # Negative number fix
            return
            
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
        
        remaining_horses = []
        for h, w, c in HORSES:
            if h not in self.finish_times:
                pos = self.positions[h]
                if pos > 0:
                    distance_left = TRACK_PIXELS - pos
                    # Extrapolate finish time based on current average speed
                    estimated_remaining_time = (now * distance_left / pos)
                    final_time = now + estimated_remaining_time
                else:
                    # If horse hasn't moved, put it at the back
                    final_time = now + 999 # A large number to signify last
                remaining_horses.append((h, final_time))

        # Sort the remaining horses by their estimated finish time
        remaining_horses.sort(key=lambda x: x[1])

        # Add the sorted remaining horses to the finish order
        for h, finish_time in remaining_horses:
            self.finish_times[h] = finish_time
            self.finish_order.append(h)
            self._check_finish(h) # This calculates the margin based on the new order
            self.finish_overshoot[h] = TRACK_PIXELS + random.randint(15, 30)

        # Move all horses to their final positions
        for h, w, c in HORSES:
            if h in self.finish_overshoot:
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
        
        # Check for a dead heat
        winners = [winner]
        if len(self.finish_order) > 1:
            winner_time = self.finish_times[winner]
            for i in range(1, len(self.finish_order)):
                horse = self.finish_order[i]
                if abs(self.finish_times[horse] - winner_time) < 0.01:
                    winners.append(horse)

        if self.bet_horse in winners:
            payout_frac = self.odds[self.bet_horse]
            payout = self.calculate_payout(self.bet_amount, payout_frac)
            
            if len(winners) > 1:
                payout = payout // len(winners)
                self._log_comment(f"Dead heat! You won a split pot! Payout: ${payout}")
            else:
                self._log_comment(f"You won! Payout: ${payout}")

            self.balance += payout
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
