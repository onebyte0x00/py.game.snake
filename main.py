import tkinter as tk
from tkinter import messagebox, ttk
import random
import sqlite3
import os
from datetime import datetime

class SnakeGame:
    def __init__(self, master):
        """Initialize the game with main window"""
        self.master = master
        self.master.title("Snake Game")
        self.master.resizable(False, False)
        
        # Initialize database connection
        self.init_db()
        
        # Show the start page with game options
        self.show_start_page()
    
    def init_db(self):
        """Initialize the SQLite database for storing high scores"""
        # Create data directory if it doesn't exist
        if not os.path.exists('data'):
            os.makedirs('data')
        
        # Connect to SQLite database (creates if doesn't exist)
        self.conn = sqlite3.connect('data/snake_scores.db')
        self.cursor = self.conn.cursor()
        
        # Create scores table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT,
                score INTEGER,
                level TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def show_start_page(self):
        """Display the start page with game options"""
        # Clear any existing widgets
        for widget in self.master.winfo_children():
            widget.destroy()
        
        # Create main frame for start page
        self.start_frame = tk.Frame(self.master)
        self.start_frame.pack(pady=50)
        
        # Game title
        tk.Label(
            self.start_frame, 
            text="Snake Game", 
            font=('Arial', 24, 'bold')
        ).pack(pady=20)
        
        # Player name entry
        tk.Label(
            self.start_frame, 
            text="Enter your name:", 
            font=('Arial', 12)
        ).pack()
        self.player_name = tk.StringVar()
        tk.Entry(
            self.start_frame, 
            textvariable=self.player_name, 
            font=('Arial', 12)
        ).pack(pady=5)
        
        # Difficulty level selection
        tk.Label(
            self.start_frame, 
            text="Select difficulty:", 
            font=('Arial', 12)
        ).pack()
        self.difficulty = tk.StringVar(value="Medium")
        difficulties = ["Easy", "Medium", "Hard"]
        for level in difficulties:
            tk.Radiobutton(
                self.start_frame, 
                text=level, 
                variable=self.difficulty, 
                value=level,
                font=('Arial', 10)
            ).pack(anchor='w')
        
        # Start game button
        tk.Button(
            self.start_frame, 
            text="Start Game", 
            command=self.start_game,
            font=('Arial', 12, 'bold'),
            bg='green',
            fg='white'
        ).pack(pady=20)
        
        # View high scores button
        tk.Button(
            self.start_frame, 
            text="View High Scores", 
            command=self.show_high_scores,
            font=('Arial', 10),
            bg='blue',
            fg='white'
        ).pack()
    
    def show_high_scores(self):
        """Display a window with the top 10 high scores"""
        # Create new window for high scores
        scores_window = tk.Toplevel(self.master)
        scores_window.title("High Scores")
        scores_window.resizable(False, False)
        
        # Get top 10 scores from database
        self.cursor.execute('''
            SELECT player_name, score, level, date 
            FROM scores 
            ORDER BY score DESC 
            LIMIT 10
        ''')
        high_scores = self.cursor.fetchall()
        
        # Create table columns
        columns = ("Rank", "Player", "Score", "Level", "Date")
        tree = ttk.Treeview(scores_window, columns=columns, show="headings")
        
        # Configure column headings
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        
        # Adjust column widths
        tree.column("Player", width=120)
        tree.column("Date", width=150)
        
        # Insert score data into the table
        for i, score in enumerate(high_scores, 1):
            # Format date for better readability
            date_str = datetime.strptime(score[3], "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y %H:%M")
            tree.insert("", "end", values=(i, score[0], score[1], score[2], date_str))
        
        tree.pack(padx=10, pady=10)
        
        # Close button
        tk.Button(
            scores_window, 
            text="Close", 
            command=scores_window.destroy
        ).pack(pady=10)
    
    def show_game_results(self):
        """Display the player's score and recent high scores after game over"""
        # Create new window for results
        results_window = tk.Toplevel(self.master)
        results_window.title("Game Results")
        results_window.resizable(False, False)
        
        # Player's score frame
        player_frame = tk.Frame(results_window)
        player_frame.pack(pady=10)
        
        # Display player's score
        tk.Label(
            player_frame,
            text=f"Your Score: {self.score}",
            font=('Arial', 14, 'bold')
        ).pack()
        
        tk.Label(
            player_frame,
            text=f"Difficulty: {self.difficulty}",
            font=('Arial', 12)
        ).pack()
        
        # Recent high scores frame
        scores_frame = tk.Frame(results_window)
        scores_frame.pack(pady=10, padx=10)
        
        tk.Label(
            scores_frame,
            text="Recent High Scores",
            font=('Arial', 12, 'underline')
        ).pack()
        
        # Get top 5 scores for the current difficulty level
        self.cursor.execute('''
            SELECT player_name, score, date 
            FROM scores 
            WHERE level = ?
            ORDER BY score DESC 
            LIMIT 5
        ''', (self.difficulty,))
        high_scores = self.cursor.fetchall()
        
        # Create a simple text display for scores
        for i, score in enumerate(high_scores, 1):
            date_str = datetime.strptime(score[2], "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y")
            score_text = f"{i}. {score[0]}: {score[1]} ({date_str})"
            tk.Label(
                scores_frame,
                text=score_text,
                font=('Arial', 10)
            ).pack(anchor='w')
        
        # Buttons frame
        buttons_frame = tk.Frame(results_window)
        buttons_frame.pack(pady=10)
        
        # Play again button
        tk.Button(
            buttons_frame,
            text="Play Again",
            command=lambda: [results_window.destroy(), self.show_start_page()],
            bg='green',
            fg='white'
        ).pack(side='left', padx=5)
        
        # Quit button
        tk.Button(
            buttons_frame,
            text="Quit",
            command=self.master.destroy,
            bg='red',
            fg='white'
        ).pack(side='left', padx=5)
    
    def start_game(self):
        """Start a new game with selected options"""
        # Validate player name
        player_name = self.player_name.get().strip()
        if not player_name:
            messagebox.showwarning("Warning", "Please enter your name!")
            return
        
        # Set game speed based on difficulty
        difficulty = self.difficulty.get()
        if difficulty == "Easy":
            speed = 200
        elif difficulty == "Medium":
            speed = 150
        else:  # Hard
            speed = 100
        
        # Clear start page
        self.start_frame.destroy()
        
        # Game configuration
        self.cell_size = 20
        self.width = 20
        self.height = 20
        self.speed = speed
        self.player_name = player_name
        self.difficulty = difficulty
        
        # Initialize game state
        self.snake = [(5, 5), (5, 4), (5, 3)]  # Initial snake position
        self.direction = "Right"  # Starting direction
        self.food = self.create_food()  # First food item
        self.score = 0  # Starting score
        self.game_over = False  # Game state flag
        
        # Create game canvas
        self.canvas = tk.Canvas(
            self.master, 
            width=self.width * self.cell_size, 
            height=self.height * self.cell_size,
            bg="black"
        )
        self.canvas.pack()
        
        # Score display label
        self.score_label = tk.Label(
            self.master, 
            text=f"Player: {player_name} | Score: {self.score} | Level: {difficulty}", 
            font=('Arial', 12)
        )
        self.score_label.pack()
        
        # Draw initial game elements
        self.draw_snake()
        self.draw_food()
        
        # Bind keyboard controls
        self.master.bind("<KeyPress>", self.change_direction)
        
        # Start the game loop
        self.update()
    
    def create_food(self):
        """Generate food at random position not occupied by snake"""
        while True:
            food = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1)
            )
            if food not in self.snake:
                return food
    
    def draw_snake(self):
        """Draw the snake on the canvas"""
        self.canvas.delete("snake")
        # Draw each segment of the snake
        for segment in self.snake:
            x, y = segment
            self.canvas.create_rectangle(
                x * self.cell_size, y * self.cell_size,
                (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                fill="green", tag="snake"
            )
        # Draw head with different color
        head = self.snake[0]
        self.canvas.create_rectangle(
            head[0] * self.cell_size, head[1] * self.cell_size,
            (head[0] + 1) * self.cell_size, (head[1] + 1) * self.cell_size,
            fill="dark green", tag="snake"
        )
    
    def draw_food(self):
        """Draw the food on the canvas"""
        self.canvas.delete("food")
        x, y = self.food
        self.canvas.create_oval(
            x * self.cell_size, y * self.cell_size,
            (x + 1) * self.cell_size, (y + 1) * self.cell_size,
            fill="red", tag="food"
        )
    
    def change_direction(self, event):
        """Handle keyboard input to change snake direction"""
        key = event.keysym
        if key in ["Up", "Down", "Left", "Right"]:
            # Prevent reversing direction (can't go right if currently going left)
            if (key == "Up" and self.direction != "Down" or
                key == "Down" and self.direction != "Up" or
                key == "Left" and self.direction != "Right" or
                key == "Right" and self.direction != "Left"):
                self.direction = key
    
    def move_snake(self):
        """Move the snake and check for collisions"""
        if self.game_over:
            return
        
        # Calculate new head position based on direction
        head = self.snake[0]
        if self.direction == "Up":
            new_head = (head[0], head[1] - 1)
        elif self.direction == "Down":
            new_head = (head[0], head[1] + 1)
        elif self.direction == "Left":
            new_head = (head[0] - 1, head[1])
        elif self.direction == "Right":
            new_head = (head[0] + 1, head[1])
        
        # Check for collisions with walls or self
        if (new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height):
            self.game_over = True
            self.save_score()
            self.show_game_results()  # Show results table
            return
        
        # Move snake by adding new head
        self.snake.insert(0, new_head)
        
        # Check if snake ate food
        if new_head == self.food:
            self.score += 1
            self.score_label.config(
                text=f"Player: {self.player_name} | Score: {self.score} | Level: {self.difficulty}"
            )
            self.food = self.create_food()
            self.draw_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def save_score(self):
        """Save the player's score to the database"""
        self.cursor.execute('''
            INSERT INTO scores (player_name, score, level)
            VALUES (?, ?, ?)
        ''', (self.player_name, self.score, self.difficulty))
        self.conn.commit()
    
    def update(self):
        """Main game loop"""
        self.move_snake()
        self.draw_snake()
        if not self.game_over:
            self.master.after(self.speed, self.update)

if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
