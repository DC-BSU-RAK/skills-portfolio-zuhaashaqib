import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk 
import io
import pygame

# Global Quiz Parameters 
POINTS_FIRST_TRY = 10
POINTS_SECOND_TRY = 5
NUM_QUESTIONS = 10

# Color and Font Configuration for Design 
PRIMARY_COLOR = '#4285F4'   
SECONDARY_COLOR = '#34A853' 
ACCENT_COLOR = '#FBBC05'    
BACKGROUND_COLOR = '#F5F5F5' 
CARD_COLOR = '#F0F0FF'       
TEXT_COLOR = '#333333'      
HEADING_FONT = ('Cooper Black', 18, 'bold')
BODY_FONT = ('Comic Sans MS', 12)
BUTTON_FONT = ('Verdana', 12, 'bold')

# Initialize the mixer for sound effects and bg music
pygame.mixer.init()

# Load background music
pygame.mixer.music.load("bgsound.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # -1 = loop forever

# Load sound effects for correct and wrong answers
correct_sound = pygame.mixer.Sound("correct.wav")
wrong_sound = pygame.mixer.Sound("wrong.wav")

# Main application class for the math quiz.
# Manages  navigation ,state between screens and quiz logic.
class MathQuiz:
    def __init__(self, master):
        # Initialize the root window
        self.master = master
        master.title("Math Quiz!")
        master.geometry("500x450") 

        # Enforce minimum size for responsiveness
        MIN_WIDTH = 500
        MIN_HEIGHT = 450
        master.minsize(MIN_WIDTH, MIN_HEIGHT)
        
        # Set the default background color for the root window
        master.config(bg=BACKGROUND_COLOR) 
                
        # Initialize Quiz State Variables
        self.difficulty_level = None      # Easy, Moderate, or Advanced
        self.question_count = 0           # Current question number (1 to NUM_QUESTIONS)
        self.current_score = 0            # Total points collected
        self.current_problem = None       # Dictionary holding the current problem {num1, num2, op, answer}
        self.attempts = 0                 # Attempts made on the current question

        # Background/Image variables
        self.current_bg_image_tk = None   # Tkinter PhotoImage object for the background
        self.current_image_filename = ""  # Stores the name of the currently loaded background image
        
        # Background Label (fills the entire root window)
        self.bg_label = tk.Label(master)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Bind resize event to keep the background image scaled
        master.bind('<Configure>', self.on_resize)

        # Main Content Frame (The Card)
        # This frame holds all screen content (instructions, menu, quiz, results)
        self.main_frame = tk.Frame(master, 
            bg=CARD_COLOR, 
            padx=20, pady=20, 
            relief=tk.RIDGE, 
            bd=8 
        )
        
        # Center the main card frame and make it responsive (70% of root size)
        self.main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.7, relheight=0.7)

        # Start the application with the instructions screen
        self.displayInstructions()
        

    # Sets the background image for the main window. 
    # Only updates if the requested image is different from the current one.
    def set_background(self, image_filename):
        if self.current_image_filename == image_filename:
            return 
            
        self.current_image_filename = image_filename
        self.on_resize()   # Call resize to load and scale the new image

    # Handles window resizing by reloading and scaling the background image to fit the new dimensions of the root window.
    def on_resize(self, event=None):
        image_filename = self.current_image_filename
        if not image_filename:
            return

        new_width = self.master.winfo_width()
        new_height = self.master.winfo_height()
        
        # Prevent errors if the window is minimized or too small
        if new_width < 10 or new_height < 10:
            return
            
        try:
            # Open the image using PIL
            img_pil = Image.open(image_filename)
            # Resize the image using high-quality anti-aliasing
            img_pil = img_pil.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert PIL image to Tkinter PhotoImage and store the reference
            self.current_bg_image_tk = ImageTk.PhotoImage(img_pil)

            # Update the background label configuration
            self.bg_label.config(image=self.current_bg_image_tk)
            
        # Fallback if the image file is not found, sets a solid background
        except FileNotFoundError:
            self.bg_label.config(image=None, bg=BACKGROUND_COLOR) 
            print(f"Image file not found: '{image_filename}'")
        except Exception as e:
            # General error fallback
            self.bg_label.config(image=None, bg=BACKGROUND_COLOR)

    # Displays the instructions before starting the quiz.
    def displayInstructions(self):
        self.set_background("menu_bg.png")
        self.clearFrame()

        tk.Label(
            self.main_frame,
            text="Quiz Rules",
            font=HEADING_FONT,
            fg=PRIMARY_COLOR,
            bg=CARD_COLOR,
            pady=10
        ).pack(fill='x')

        # List of quiz rules to be displayed
        rules = [
            "1. Choose Difficulty Level: Easy, Moderate, or Advanced",
            "2. The quiz has 10 questions",
            "3. 2 attempts per question:",
            "   • First attempt correct: 10 points",
            "   • Second attempt correct: 5 points",
            "   • Incorrect after 2 attempts: 0 points",
            "4. Your score updates after each question",
            "5. At the end, view your final score and rank",
            "6. You can play again or exit after completing the quiz"
        ]

        # Create a label for each rule
        for rule in rules:
            tk.Label(
                self.main_frame,
                text=rule,
                font=BODY_FONT,
                fg=TEXT_COLOR,
                bg=CARD_COLOR,
                anchor="w",
                justify="left"
            ).pack(fill='x', padx=10, pady=2)
         
        # Button to move to the difficulty menu
        tk.Button(
            self.main_frame,
            text="Start Quiz",
            command=self.displayMenu, 
            font=BUTTON_FONT,
            bg='#FBBC05',
            fg='white',
            relief=tk.RAISED,
            bd=3
        ).pack(pady=20, fill='x')

    # Returns the (minimum, maximum) range for number generation based on difficulty.
    def randomInt(self, difficulty_level):
        if difficulty_level == 'Easy': return (1, 9)              # Single digits
        elif difficulty_level == 'Moderate': return (10, 99)      # Double digits
        elif difficulty_level == 'Advanced': return (1000, 9999)  # Four digits
        else: raise ValueError("Invalid difficulty level")

    # Randomly selects an operation: addition or subtraction.
    def decideOperation(self):
        return random.choice(['+', '-'])

    # Generates a new arithmetic problem based on the selected difficulty.
    def generateProblem(self):
        min_val, max_val = self.randomInt(self.difficulty_level)
        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)
        # Ensure the first number is larger than the second for non-negative subtraction
        operator = self.decideOperation()
        answer = num1 + num2 if operator == '+' else num1 - num2
        # Store the generated problem details
        self.current_problem = {
            'num1': num1, 'num2': num2, 'operator': operator, 'correct_answer': answer
        }

    # Checks if the user's input matches the correct answer.
    def isCorrect(self, user_answer):
        try:
            # Convert and check the stripped input against the stored answer
            return int(user_answer.strip()) == self.current_problem['correct_answer']
        # Returns False if the input is not a valid integer
        except ValueError:
            return False

    # Handles the user submitting answers, checks if it is correct or not, and updates the score.
    def submitAnswer(self):
        user_answer = self.answer_entry.get()
        if self.isCorrect(user_answer):
            correct_sound.play()      # Play correct sound
            points = POINTS_FIRST_TRY if self.attempts == 1 else POINTS_SECOND_TRY
            self.current_score += points
            messagebox.showinfo("Feedback", f"Correct! You earned {points} points.")
            self.nextQuestion()
        else:
            wrong_sound.play()        # Play wrong sound
            self.attempts += 1
            # First incorrect attempt, give second chance
            if self.attempts == 2:
                messagebox.showerror("Feedback", "Incorrect. You get one more try for 5 points.")
                self.feedback_label.config(text="Incorrect. Try again for 5 points.", fg='red')
            # Second incorrect attempt, show correct answer and move to next
            elif self.attempts == 3:
                correct_ans = self.current_problem['correct_answer']
                messagebox.showerror("Feedback", f"Failed. The correct answer was {correct_ans}.")
                self.nextQuestion()
        
         # Clear the entry box and refocus if attempts are available
        if self.answer_entry.winfo_exists(): 
            self.answer_entry.delete(0, tk.END)
            if self.attempts < 3:
                self.answer_entry.focus_set()

    # Increments question count and either displays the next problem or the results.
    def nextQuestion(self):
        self.question_count += 1
        self.attempts = 1
        if self.question_count > NUM_QUESTIONS:
            self.displayResults()    # End of quiz
        else:
            self.generateProblem()   # Generate and display new problem
            self.displayProblem()

    # Removes all widgets from the main content frame.
    def clearFrame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # Displays the difficulty selection menu.
    def displayMenu(self):
        self.set_background("menu_bg.png") 
        self.clearFrame()

        tk.Label(
            self.main_frame, text="🔢 Math Quiz! 🧠", 
            font=HEADING_FONT, bg=CARD_COLOR, fg=PRIMARY_COLOR, pady=15
        ).pack(fill='x')

        tk.Label(
            self.main_frame, text="Select your difficulty level:", 
            font=BODY_FONT, bg=CARD_COLOR, fg=TEXT_COLOR
        ).pack(pady=(10, 5))

        # Dictionary of difficulty options and their corresponding levels
        difficulties = {
            "Easy (Single Digit)": 'Easy',
            "Moderate (Double Digits)": 'Moderate',
            "Advanced (4-Digits)": 'Advanced'
        }

        # Create a button for each difficulty level
        for text, level in difficulties.items():
            # Uses lambda to pass the level argument to startQuiz when clicked
            tk.Button(
                self.main_frame, text=text, command=lambda l=level: self.startQuiz(l),
                font=BUTTON_FONT, width=None, bg=ACCENT_COLOR, fg='white',
                relief=tk.RAISED, bd=3
            ).pack(pady=8, fill='x')

    # Initializes quiz and begins the first question.
    def startQuiz(self, level):
        self.difficulty_level = level
        self.question_count = 0
        self.current_score = 0
        self.attempts = 1
        self.nextQuestion()

    # Displays the current arithmetic problem and input fields.
    def displayProblem(self):
        self.set_background("quiz_bg.png")
        self.clearFrame()
        p = self.current_problem  # Current problem dictionary

        # Status frame to show question number and current score
        status_frame = tk.Frame(self.main_frame, bg=BACKGROUND_COLOR, padx=10, pady=5)
        status_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(status_frame, text=f"Question {self.question_count}/{NUM_QUESTIONS}",
                 font=BODY_FONT, fg=TEXT_COLOR, bg=BACKGROUND_COLOR).pack(side=tk.LEFT)
        tk.Label(status_frame, text=f"Score: {self.current_score}",
                 font=BODY_FONT, fg=TEXT_COLOR, bg=BACKGROUND_COLOR).pack(side=tk.RIGHT)

        # Display the math problem prominently
        problem_text = f"❓ {p['num1']} {p['operator']} {p['num2']} = ?"
        tk.Label(self.main_frame, text=problem_text, font=('Consolas', 24, 'bold'), 
                 fg=PRIMARY_COLOR, bg=CARD_COLOR).pack(pady=20) 
        
        # Label to display feedback
        self.feedback_label = tk.Label(self.main_frame, text="Type your answer below:", 
                                       fg=TEXT_COLOR, font=BODY_FONT, bg=CARD_COLOR) 
        self.feedback_label.pack()

        # Entry widget for user input
        self.answer_entry = tk.Entry(self.main_frame, font=('Arial', 20), width=10, 
                                     justify='center', bd=4, relief=tk.GROOVE)
        self.answer_entry.pack(pady=10, ipady=5)
        # Bind the Enter key to the submitAnswer function
        self.answer_entry.bind('<Return>', lambda event=None: self.submitAnswer())
        self.answer_entry.focus_set()

        # Submit Button
        tk.Button(self.main_frame, text="Submit", command=self.submitAnswer,
                  font=BUTTON_FONT, bg=PRIMARY_COLOR, fg='white',
                  relief=tk.RAISED, bd=3, width=None).pack(pady=20, fill='x')
        
         # Quit Button to return to the difficulty menu
        tk.Button(self.main_frame, text="Quit", command=self.displayMenu,
          font=BUTTON_FONT, bg='#CC0000', fg='white',
          relief=tk.RAISED, bd=3, width=None).pack(side=tk.RIGHT, padx=5, fill='x', expand=True)

    # Determines a letter grade/rank based on the final percentage score.
    def rank(self, final_score):
        if final_score >= 90: return "A+ (Excellent!) "
        elif final_score >= 80: return "A (Great job!) "
        elif final_score >= 70: return "B (Solid effort!) "
        elif final_score >= 60: return "C (Keep practicing!) "
        else: return "D (Time to study up!) "

    # Displays the final score, percentage, and rank.
    def displayResults(self):
        self.set_background("results_bg.png")
        self.clearFrame()

        possible_score = NUM_QUESTIONS * POINTS_FIRST_TRY
        final_score_percentage = (self.current_score / possible_score) * 100
        rank = self.rank(final_score_percentage)
        
        tk.Label(self.main_frame, text="🏆 QUIZ COMPLETE! 🏆", 
                 font=HEADING_FONT, fg=SECONDARY_COLOR, bg=CARD_COLOR).pack(pady=10) 

        tk.Label(self.main_frame, text=f"Final Score: {self.current_score} / {possible_score}", 
                 font=('Arial', 14), bg=CARD_COLOR).pack(pady=5) 
        tk.Label(self.main_frame, text=f"Percentage: {final_score_percentage:.1f}%", 
                 font=('Arial', 14), bg=CARD_COLOR).pack(pady=5) 

        tk.Label(self.main_frame, text=f"Your Rank: {rank}", 
                 font=('Arial', 16, 'bold'), fg=ACCENT_COLOR, bg=CARD_COLOR).pack(pady=15) 

        tk.Label(self.main_frame, text="What's next?", font=BODY_FONT, bg=CARD_COLOR).pack(pady=10) 

        # Frame for placing "Play Again" and "Exit" 
        button_frame = tk.Frame(self.main_frame, bg=CARD_COLOR) 
        button_frame.pack(pady=10, fill='x')

        # Button to reset and return to the Menu
        tk.Button(button_frame, text="Play Again", command=self.displayMenu,
                  font=BUTTON_FONT, bg=SECONDARY_COLOR, fg='white', width=None
        ).pack(side=tk.LEFT, padx=10, fill='x', expand=True)

        # Button to exit and close the application
        tk.Button(button_frame, text="Exit", command=self.master.quit,
                  font=BUTTON_FONT, bg='#CC0000', fg='white', width=None
        ).pack(side=tk.RIGHT, padx=10, fill='x', expand=True)

if __name__ == "__main__":
     # Create the root Tkinter window
    root = tk.Tk()
    # Instantiate the application class
    app = MathQuiz(root)
    # Start the Tkinter event loop
    root.mainloop()
