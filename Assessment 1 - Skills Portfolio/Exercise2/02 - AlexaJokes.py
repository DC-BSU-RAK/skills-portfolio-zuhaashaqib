import tkinter as tk
from tkinter import messagebox
import random
import os
from PIL import Image, ImageTk
import pygame   

# File names for jokes, background GIF, and music
JOKES_FILE = "Assessment 1 - Skills Portfolio/Exercise2/Jokes.txt"
GIF_FILE = "Assessment 1 - Skills Portfolio/Exercise2/jokesbg.gif"
MUSIC_FILE = "Assessment 1 - Skills Portfolio/Exercise2/jokesbg.mp3"   

class randomJokes(tk.Tk):
    def __init__(self, jokes_file):
        super().__init__()
        # Set the window icon using a custom .ico file
        self.iconbitmap("Assessment 1 - Skills Portfolio/Exercise2/laugh.ico")
        # Basic window settings
        self.title("Alexa! Tell Me a Joke")
        self.geometry("600x300")
        self.resizable(False, False)

        # Initialize Pygame and start the background music
        pygame.mixer.init()                    
        self.play_background_music()           

        # For animated GIF frames
        self.frames = []
        self.current_frame = 0

        # Load GIF background frames and place the label
        # I used online resources which helped me to understand how to load GIF frames
        # and animate them using Tkinter 
        self.load_gif_frames(GIF_FILE)
        self.bg_label = tk.Label(self, bg="black")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
         # Start GIF animation
        self.animate()

        # UI colors
        self.fg_color = "#ffffff"
        self.button_color = "#ffde59"   

        # Joke storage
        self.jokes = []
        self.current_index = None

        # Load jokes and build interface
        self.load_jokes(JOKES_FILE)
        self.create_widgets()

    # Play looping background music
    # I took help from some online resources to add audio in the code
    def play_background_music(self):
        try:
            pygame.mixer.music.load(MUSIC_FILE)   # Load MP3 file
            pygame.mixer.music.play(-1)           # -1 = loop forever
        except:
            print("Could not load background music.")

    # Load all GIF frames into memory so the animation works properly
    def load_gif_frames(self, path):
        # Go through each GIF frame until EOF
        try:
            gif = Image.open(path)                   
        except:
            print("Could not load GIF background.")
            return

        self.frames = []

        try:
            while True:
                frame = gif.copy().resize((600, 300))          # Resize to window
                self.frames.append(ImageTk.PhotoImage(frame))
                gif.seek(len(self.frames))                     # Move to next frame
        except EOFError:
            pass

    # Loop the GIF animation by switching frames every 80 ms
    def animate(self):
        if self.frames:
            frame = self.frames[self.current_frame]
            self.bg_label.config(image=frame)
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.after(80, self.animate)

    # Read jokes from text file
    def load_jokes(self, filepath):
        if not os.path.exists(filepath):
            messagebox.showerror("File not found", f"Could not find '{filepath}'.")
            self.destroy()
            return

         # Read lines without blank ones
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]

        parsed = []
        # Split jokes into setup and punchline
        for ln in lines:
            if "?" in ln:
                setup, _, punch = ln.partition("?")
                parsed.append((setup.strip() + "?", punch.strip()))
            else:
                parsed.append((ln.strip(), ""))

        if not parsed:
            messagebox.showerror("No jokes", "No jokes found.")
            self.destroy()
            return

        self.jokes = parsed

    # Create all the labels and buttons
    def create_widgets(self):
        fun_font = ("Comic Sans MS", 16, "bold")
        normal_font = ("Comic Sans MS", 14)
        italic_font = ("Comic Sans MS", 13, "italic")

        # Title label
        header = tk.Label(self, text="Alexa! Tell Me a Joke",
                          font=("Comic Sans MS", 20, "bold"),
                          fg=self.fg_color, bg="black")
        header.pack(pady=(12, 6))

        # Frame for setup & punchline text
        display_frame = tk.Frame(self, bg="black")
        display_frame.pack(fill="both", expand=True)

        # Setup joke text label
        self.setup_label = tk.Label(
            display_frame,
            text="Press 'Alexa tell me a Joke' to begin.",
            font=normal_font,
            wraplength=560,
            justify="center",
            fg=self.fg_color, bg="black"
        )
        self.setup_label.pack(pady=(10, 6))

        # Punchline label
        self.punchline_label = tk.Label(
            display_frame,
            text="",
            font=italic_font,
            wraplength=560,
            justify="center",
            fg="#ffd700",
            bg="black"
        )
        self.punchline_label.pack(pady=(6, 10))

        # Button part
        btn_frame = tk.Frame(self, bg="black")
        btn_frame.pack(pady=(6, 16))

        # Button: tell a new joke
        self.tell_btn = tk.Button(btn_frame, text="Alexa tell me a Joke",
                                  width=18, font=("Comic Sans MS", 12),
                                  command=self.tell_joke, bg=self.button_color)
        self.tell_btn.grid(row=0, column=0, padx=6, pady=4)

        # Button: show punchline
        self.punch_btn = tk.Button(btn_frame, text="Show Punchline",
                                   width=14, font=("Comic Sans MS", 12),
                                   command=self.show_punchline,
                                   state="disabled", bg=self.button_color)
        self.punch_btn.grid(row=0, column=1, padx=6, pady=4)

        # Button: next joke
        self.next_btn = tk.Button(btn_frame, text="Next Joke",
                                  width=12, font=("Comic Sans MS", 12),
                                  command=self.next_joke,
                                  state="disabled", bg=self.button_color)
        self.next_btn.grid(row=0, column=2, padx=6, pady=4)

        # Quit button
        self.quit_btn = tk.Button(btn_frame, text="Quit",
                                  width=8, font=("Comic Sans MS", 12),
                                  command=self.quit, bg=self.button_color)
        self.quit_btn.grid(row=0, column=3, padx=6, pady=4)

   # Pick a random joke and show the setup
    def tell_joke(self):
        if not self.jokes:
            return

         # To avoid repeating the same joke twice in a row
        if len(self.jokes) == 1:
            idx = 0
        else:
            idx = random.randrange(len(self.jokes))
            if self.current_index is not None and idx == self.current_index:
                idx = random.randrange(len(self.jokes))

        self.current_index = idx
        setup, _ = self.jokes[idx]
        self.setup_label.config(text=setup)
        self.punchline_label.config(text="")
        # Enable the other buttons
        self.punch_btn.config(state="normal")
        self.next_btn.config(state="normal")

    # Display punchline of current joke
    def show_punchline(self):
        if self.current_index is None:
            return
        _, punch = self.jokes[self.current_index]
        self.punchline_label.config(text=punch or "(No punchline provided.)")

    # Move to another joke
    def next_joke(self):
        self.tell_joke()

# Start program
if __name__ == "__main__":
    app = randomJokes(JOKES_FILE)
    try:
        app.mainloop()
    except tk.TclError:
        pass
