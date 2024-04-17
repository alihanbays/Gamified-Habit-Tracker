import tkinter as tk
from tkinter import simpledialog, messagebox, font as tkfont, ttk
import json
from datetime import datetime

class Habit:
    def __init__(self, name, streak=0, xp=0, last_logged_day=None):
        self.name = name
        self.streak = streak
        self.xp = xp
        self.last_logged_day = last_logged_day

    def log_habit(self, current_day):
        if self.last_logged_day == current_day:
            return False
        if self.last_logged_day == current_day - 1:
            self.streak += 1
        else:
            self.streak = 1
        self.last_logged_day = current_day
        self.xp += 10 * self.streak  # Earn more XP for longer streaks
        return True

    def to_dict(self):
        return {
            "name": self.name,
            "streak": self.streak,
            "xp": self.xp,
            "last_logged_day": self.last_logged_day
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data['streak'], data['xp'], data['last_logged_day'])

class HabitTracker:
    def __init__(self):
        self.habits = {}
        self.level = 1
        self.total_xp = 0
        self.xp_for_next_level = 100  # Adjustable scale for XP needed for next level
        self.load_progress()

    def add_habit(self, habit_name):
        if habit_name in self.habits:
            messagebox.showerror("Error", f"Habit '{habit_name}' already exists.")
            return
        self.habits[habit_name] = Habit(habit_name)
        self.save_progress()
        messagebox.showinfo("Habit Tracker", f"Habit '{habit_name}' added.")

    def log_habit(self, habit_name):
        today = datetime.now().toordinal()
        if habit_name in self.habits:
            if self.habits[habit_name].log_habit(today):
                self.total_xp += 10
                if self.total_xp >= self.xp_for_next_level:
                    self.level_up()
                self.save_progress()
            else:
                messagebox.showinfo("Habit Tracker", f"Habit '{habit_name}' already logged today.")

    def level_up(self):
        self.level += 1
        self.xp_for_next_level += 100  # Increase the XP required for the next level
        messagebox.showinfo("Level Up!", f"Congratulations! You've reached level {self.level}!")

    def save_progress(self):
        data = {
            "habits": {name: habit.to_dict() for name, habit in self.habits.items()},
            "level": self.level,
            "total_xp": self.total_xp,
            "xp_for_next_level": self.xp_for_next_level
        }
        with open('habit_tracker_data.json', 'w') as file:
            json.dump(data, file, indent=4)

    def load_progress(self):
        try:
            with open('habit_tracker_data.json', 'r') as file:
                data = json.load(file)
                self.habits = {name: Habit.from_dict(habit) for name, habit in data['habits'].items()}
                self.level = data['level']
                self.total_xp = data['total_xp']
                self.xp_for_next_level = data['xp_for_next_level']
        except FileNotFoundError:
            print("No existing data found, starting a new tracker.")

    def get_progress_percentage(self):
        return (self.total_xp / self.xp_for_next_level) * 100

    def get_rank(self):
        if self.level < 15:
            return "Rookie"
        elif self.level < 30:
            return "Intermediate"
        else:
            return "Advanced"

class HabitTrackerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Alihan's Habit Tracker")
        self.tracker = HabitTracker()
        self.create_widgets()
        self.update_display()

    def create_widgets(self):
        self.title_font = tkfont.Font(family="Lucida Grande", size=16, weight="bold")
        self.text_font = tkfont.Font(family="Lucida Grande", size=12)

        self.title_label = tk.Label(self.master, text="Alihan's Habit Tracker", font=self.title_font)
        self.title_label.pack(pady=(10, 5))

        self.stats_frame = tk.Frame(self.master)
        self.stats_frame.pack(fill=tk.X, padx=10)

        self.xp_label = tk.Label(self.stats_frame, text="", font=self.text_font)
        self.xp_label.pack(side=tk.TOP)

        self.level_label = tk.Label(self.stats_frame, text="", font=self.text_font)
        self.level_label.pack(side=tk.TOP)

        self.rank_label = tk.Label(self.stats_frame, text="", font=self.text_font)
        self.rank_label.pack(side=tk.TOP)

        self.progress_bar = ttk.Progressbar(self.stats_frame, length=100, mode='determinate')
        self.progress_bar.pack(side=tk.TOP, fill=tk.X, expand=True, padx=(10, 0))

        self.habits_frame = tk.Frame(self.master)
        self.habits_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.add_habit_button = tk.Button(self.master, text="Add Habit", command=self.add_habit, font=self.text_font)
        self.add_habit_button.pack(pady=(0, 10))

    def add_habit(self):
        habit_name = simpledialog.askstring("Input", "Enter the name of the new habit:", parent=self.master)
        if habit_name:
            self.tracker.add_habit(habit_name)
            self.update_display()

    def update_display(self):
        for widget in self.habits_frame.winfo_children():
            widget.destroy()

        self.xp_label.config(text=f"Total XP: {self.tracker.total_xp}")
        self.level_label.config(text=f"Level: {self.tracker.level}")
        self.progress_bar['value'] = self.tracker.get_progress_percentage()
        self.rank_label.config(text=f"Rank: {self.tracker.get_rank()}")

        for name, habit in self.tracker.habits.items():
            row = tk.Frame(self.habits_frame)
            row.pack(fill=tk.X, pady=2)

            label = tk.Label(row, text=f"{habit.name}: {habit.streak} streak(s), {habit.xp} XP", font=self.text_font)
            label.pack(side=tk.LEFT, expand=True)

            today = datetime.now().toordinal()
            if habit.last_logged_day != today:
                button = tk.Button(row, text="+", command=lambda n=name: self.log_habit(n))
                button.pack(side=tk.RIGHT)

    def log_habit(self, habit_name):
        self.tracker.log_habit(habit_name)
        self.update_display()

def main():
    root = tk.Tk()
    root.geometry("800x600")
    app = HabitTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
