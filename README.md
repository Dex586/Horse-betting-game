# Horse-betting-game

## Description
A basic horse racing simulation game with a betting system. Players can place bets on various horses, each with different odds, and watch the race unfold. The game includes features for managing player balance and provides a realistic race simulation, even when skipping.

## Features
*   **Interactive Betting:** Place bets on your favorite horses with dynamic odds.
*   **Realistic Race Simulation:** Watch horses race across the track with animated movement.
*   **Persistent Balance:** Your game balance is saved between sessions in `balance.txt`.
*   **Realistic Skip Functionality:** Skip ongoing races with results based on simulated horse performance.
*   **Leaderboard:** View race results and see how your chosen horse performed.

## How to Run
1.  Ensure you have Python installed (Python 3.x recommended).
    *   **Tkinter Requirement:** Tkinter is usually bundled with Python. If you encounter issues, you might need to install it separately. For example, on Debian/Ubuntu: `sudo apt-get install python3-tk`
2.  Navigate to the project directory in your terminal.
3.  Run the main game file:
    ```bash
    python main.py
    ```

## How to Play
1.  **Start the Game:** Run `Main.py`.
2.  **Place Your Bet:**
    *   Choose a horse from the list.
    *   Enter your desired bet amount or select a quick bet option.
    *   Click "Start Race".
3.  **Watch the Race:** Observe the horses as they race. You can click "Skip" to fast-forward to the results.
4.  **View Results:** After the race, a leaderboard will display the results. Your balance will be updated based on your bet.
5.  **Continue Playing:** The game will return to the betting screen for a new race.

## Technologies Used
*   Python
*   Tkinter (for the graphical user interface)

## License
This project is licensed under the **GNU Lesser General Public License v3.0** - see the [LICENSE](LICENSE) file for details.