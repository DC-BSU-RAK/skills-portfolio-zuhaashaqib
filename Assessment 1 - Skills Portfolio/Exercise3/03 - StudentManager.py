import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import os

# File paths for background images, data storage, and the application icon.
MENU_BG = "Assessment 1 - Skills Portfolio/Exercise3/smbackground2.png"      # Background image for the menu
MAIN_BG = "Assessment 1 - Skills Portfolio/Exercise3/smbackground.png"       # Background image for other windows
STUDENT_FILE = "Assessment 1 - Skills Portfolio/Exercise3/studentmarks.txt"  # File storing the student data
ICON_IMG = "Assessment 1 - Skills Portfolio/Exercise3/student.png"           # Application icon

# Sets a background image for a Tkinter window that resizes to cover the window area while maintaining aspect ratio
def add_responsive_background(win, image_path):
    try:
        # Load the original image only if it hasn't been loaded before for this path
        if not hasattr(win, "_bg_original") or win._bg_original_path != image_path:
            win._bg_original = Image.open(image_path).convert("RGBA")
            win._bg_original_path = image_path

        def _update_bg(event=None):
            # Get current window dimensions
            w = max(1, win.winfo_width())
            h = max(1, win.winfo_height())
            orig = win._bg_original
            ow, oh = orig.size
            # Calculate the scale factor
            scale = max(w / ow, h / oh)
            new_size = (int(ow * scale), int(oh * scale))
            # Resize and crop the image
            resized = orig.resize(new_size, Image.LANCZOS)
            left = (resized.width - w) // 2
            top = (resized.height - h) // 2
            cropped = resized.crop((left, top, left + w, top + h))
            # Create the PhotoImage object for Tkinter
            photo = ImageTk.PhotoImage(cropped)
            # Update or create the background label
            if hasattr(win, "_bg_label"):
                win._bg_label.config(image=photo)
                win._bg_label.image = photo
            else:
                win._bg_label = tk.Label(win, image=photo, bd=0)
                win._bg_label.image = photo
                win._bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                win._bg_label.lower()    # Place the label behind other widgets
        _update_bg()     # Initial call to set the background
        win.bind("<Configure>", _update_bg)     # Bind to resize events
    except Exception as e:
        print("Background image failed to load or process:", e)

# Creates a central white card with a subtle shadow effect using two overlapping Tkinter Frames
def create_center_card(parent, relwidth=0.78, relheight=0.78, shadow_offset=(0.015,0.02), relx=0.5, rely=0.5):
    # Calculate shadow size and position
    s_relw = min(0.99, relwidth + abs(shadow_offset[0]))
    s_relh = min(0.99, relheight + abs(shadow_offset[1]))
    s_relx = relx + shadow_offset[0] / 2
    s_rely = rely + shadow_offset[1] / 2

    # Shadow frame
    shadow = tk.Frame(parent, bg="#bfc8d6", bd=0, highlightthickness=0)
    shadow.place(relx=s_relx, rely=s_rely, anchor="center", relwidth=s_relw, relheight=s_relh)

    # Main card frame
    card = tk.Frame(parent, bg="white", bd=0, highlightthickness=0)
    card.place(relx=relx, rely=rely, anchor="center", relwidth=relwidth, relheight=relheight)
    card.configure(highlightbackground="#d7dbe0", highlightthickness=0)   # subtle border

    return shadow, card

# Loads student records from the specified file, calculates totals, percentages,
# and grades for each student, and stores them in a list of dictionaries.
def load_student_data(filename=STUDENT_FILE):
    students = []
    # Check if the first line is the student count
    try:
        with open(filename, "r", encoding="utf-8") as file:
            first = file.readline().strip()
            try:
                count = int(first)
            except:
                # If first line is not an integer, assume old format and reload all lines excluding the first read line
                file.seek(0)
                lines = [line.strip() for line in file if line.strip()]
            else:
                lines = []
                for _ in range(count):
                    line = file.readline().strip()
                    if line:
                        lines.append(line)

           # Process each line of student data
            for ln in lines:
                parts = [p.strip() for p in ln.split(",")]
                if len(parts) < 6:
                    continue
                code = parts[0]
                name = parts[1]
                # Convert marks to integers
                try:
                    c1, c2, c3 = int(parts[2]), int(parts[3]), int(parts[4])
                    exam = int(parts[5])
                except:
                    continue     # Skip record if marks are not valid integers

                # Calculate marks and percentages
                coursework_total = c1 + c2 + c3
                overall = coursework_total + exam
                percentage = (overall / 160) * 100

                # Determine the grade based on percentage using elif statement
                if percentage >= 70:
                    grade = "A"
                elif percentage >= 60:
                    grade = "B"
                elif percentage >= 50:
                    grade = "C"
                elif percentage >= 40:
                    grade = "D"
                else:
                    grade = "F"

                students.append({
                    "code": code,
                    "name": name,
                    "c1": c1,
                    "c2": c2,
                    "c3": c3,
                    "coursework": coursework_total,
                    "exam": exam,
                    "percentage": percentage,
                    "grade": grade
                })
    except FileNotFoundError:
        messagebox.showerror("Error", f"Student file not found:\n{filename}")
    return students

# Writes the list of student dictionaries back to the file
# Uses the new format (count on the first line)
# Only saves the raw input fields (code, name, c1, c2, c3, exam)
def save_students_to_file(students, filename=STUDENT_FILE):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{len(students)}\n")     # Write the count first
            for s in students:
                # Write only the fields needed for loading later
                line = f"{s['code']},{s['name']},{s['c1']},{s['c2']},{s['c3']},{s['exam']}\n"
                f.write(line)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save file: {e}")

# Load initial data when the script starts
students = load_student_data()

# Recalculates the coursework total, overall percentage, and final grade for a single student dictionary 's'.
# This is called after adding or updating marks
def recalc_student(s):
    # Use .get() with default 0 in case a key is missing
    s['coursework'] = s.get('c1', 0) + s.get('c2', 0) + s.get('c3', 0)
    overall = s['coursework'] + s.get('exam', 0)
    # Recalculate percentage
    s['percentage'] = (overall / 160) * 100 if overall >= 0 else 0
    pct = s['percentage']
    # Recalculate grade
    s['grade'] = "F"
    if pct >= 70:
        s['grade'] = "A"
    elif pct >= 60:
        s['grade'] = "B"
    elif pct >= 50:
        s['grade'] = "C"
    elif pct >= 40:
        s['grade'] = "D"

# Window to display individual student details in a simple format
class ShowStudentWindow(tk.Toplevel):
    def __init__(self, parent, title, student):
        super().__init__(parent)
        self.title(title)
        self.geometry("760x520")
        add_responsive_background(self, MAIN_BG)   # Use other/main background

        shadow, card = create_center_card(self, relwidth=0.72, relheight=0.7)

        header = tk.Label(card, text=title, bg="white", fg="#1f3a5f",
                          font=("Segoe UI", 16, "bold"))
        header.pack(pady=(16,8))

        content_frame = tk.Frame(card, bg="white")
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0,20))

        # Format student details into a multi-line string
        txt = (
            f"Student Name: {student['name']}\n"
            f"Student Number: {student['code']}\n\n"
            f"Coursework: {student['c1']}, {student['c2']}, {student['c3']}  (Total: {student['coursework']} / 60)\n"
            f"Exam Mark: {student['exam']} / 100\n"
            f"Overall Percentage: {student['percentage']:.2f}%\n"
            f"Grade: {student['grade']}\n"
        )
        label = tk.Label(content_frame, text=txt, justify="left", anchor="nw",
                         bg="white", fg="#222222", font=("Segoe UI", 12))
        label.pack(fill="both", expand=True)

        btn = tk.Button(card, text="Close", bg="#1f3a5f", fg="white",
                        font=("Segoe UI", 11, "bold"), bd=0,
                        command=self.destroy)
        btn.pack(pady=(0,16))

        if hasattr(self, "_bg_label"):
            self._bg_label.lower()

# Class for displaying student records in a sortable Treeview widget
# I used help from online resources and used the treeview for the table
class TableWindowBase(tk.Toplevel):
    def __init__(self, parent, title, row_data):
        super().__init__(parent)
        self.title(title)
        self.geometry("1000x700")
        add_responsive_background(self, MAIN_BG)

        shadow, self.card = create_center_card(self, relwidth=0.88, relheight=0.86)

        header = tk.Label(self.card, text=title, bg="white", fg="#1f3a5f",
                          font=("Segoe UI", 16, "bold"))
        header.pack(pady=(14,8))

        self.table_frame = tk.Frame(self.card, bg="white")
        self.table_frame.pack(fill="both", expand=True, padx=16, pady=(0,16))

        # Define Treeview columns and headings
        cols = ("code", "name", "coursework", "exam", "percentage", "grade")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings")
        for c in cols:
            text = c.title() if c != "coursework" else "Coursework (/60)"
            self.tree.heading(c, text=text)
        # Define column widths and alignment
        self.tree.column("code", width=110, anchor="center")
        self.tree.column("name", width=260, anchor="w")
        self.tree.column("coursework", width=120, anchor="center")
        self.tree.column("exam", width=110, anchor="center")
        self.tree.column("percentage", width=120, anchor="center")
        self.tree.column("grade", width=80, anchor="center")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, side="left")

        # Insert data rows
        for row in row_data:
            self.tree.insert("", "end", values=row)

        # Calculate and display average percentage
        avg = 0.0
        if row_data:
            avg = sum(float(r[4]) for r in row_data) / len(row_data)
        footer = tk.Label(self.card, text=f"Total students: {len(row_data)}    Average %: {avg:.2f}",
                          bg="white", fg="#333333", font=("Segoe UI", 11))
        footer.pack(pady=(4,12))

        if hasattr(self, "_bg_label"):
            self._bg_label.lower()

# Specific window to display all student records
class ViewAllWindow(TableWindowBase):
    def __init__(self, parent):
        rows = []
        # Prepare data for the Treeview table
        for s in students:
            # Format coursework marks into a single string
            rows.append((s["code"], s["name"], f"{s['c1']},{s['c2']},{s['c3']}", str(s["exam"]), f"{s['percentage']:.2f}", s["grade"]))
        super().__init__(parent, "All Student Records", rows)
        
# Specific window to display sorted student records
class SortedWindow(TableWindowBase):
    def __init__(self, parent, sorted_students, order_label):
        rows = []
        for s in sorted_students:
            rows.append((s["code"], s["name"], f"{s['c1']},{s['c2']},{s['c3']}", str(s["exam"]), f"{s['percentage']:.2f}", s["grade"]))
        super().__init__(parent, f"Sorted Student Records ({order_label})", rows)

# A generic window that displays all students in a Treeview and allows the user to select one record to perform an action (delete or update)
class SelectionWindow(tk.Toplevel):
    def __init__(self, parent, title, callback):
        super().__init__(parent)
        self.title(title)
        self.geometry("900x500")
        add_responsive_background(self, MAIN_BG)

        shadow, card = create_center_card(self, relwidth=0.96, relheight=0.92)

        header = tk.Label(card, text=title, bg="white", fg="#1f3a5f",
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=(10,8))

        frame = tk.Frame(card, bg="white")
        frame.pack(fill="both", expand=True, padx=12, pady=6)

        # Treeview setup is similar to TableWindowBase
        cols = ("code", "name", "coursework", "exam", "percentage", "grade")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        for c in cols:
            self.tree.heading(c, text=c.title())
        self.tree.column("code", width=120, anchor="center")
        self.tree.column("name", width=260, anchor="w")
        self.tree.column("coursework", width=140, anchor="center")
        self.tree.column("exam", width=90, anchor="center")
        self.tree.column("percentage", width=100, anchor="center")
        self.tree.column("grade", width=70, anchor="center")

        # Scrollbar setup
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True, side="left")

        # Populate the treeview, using the list index as the Item ID
        for idx, s in enumerate(students):
            self.tree.insert("", "end", iid=str(idx), values=(
                s["code"], s["name"], f"{s['c1']},{s['c2']},{s['c3']}", s["exam"],
                f"{s['percentage']:.2f}", s['grade']
            ))

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(pady=8)

        # Get the selected student's index and pass it to the callback
        def on_select():
            sel = self.tree.selection()
            if not sel:
                messagebox.showinfo("Select", "Please select a student first.")
                return
            # The iid is the index in the global 'students' list
            idx = int(sel[0])
            self.destroy()
            callback(idx, students[idx]) # Execute the action function(delete or update)

        # Action buttons
        tk.Button(btn_frame, text="Select", bg="#1f3a5f", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, command=on_select).pack(side="left", padx=8)
        tk.Button(btn_frame, text="Cancel", bg="#999", fg="white", font=("Segoe UI", 11),
                  bd=0, command=self.destroy).pack(side="left", padx=8)

        if hasattr(self, "_bg_label"):
            self._bg_label.lower()

# Window for entering details to add a new student record
class AddStudentWindow(tk.Toplevel):
    def __init__(self, parent, on_added=None):
        super().__init__(parent)
        self.title("Add Student")
        self.geometry("420x420")
        add_responsive_background(self, MAIN_BG)

        shadow, card = create_center_card(self, relwidth=0.92, relheight=0.92)

        header = tk.Label(card, text="Add Student", bg="white", fg="#1f3a5f",
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=(10,6))

        form = tk.Frame(card, bg="white")
        form.pack(padx=12, pady=6, fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        # Create input fields and labels
        labels = ["Student Number:", "Name:", "Coursework 1 (0-20):", "Coursework 2 (0-20):", "Coursework 3 (0-20):", "Exam (0-100):"]
        keys = ["code", "name", "c1", "c2", "c3", "exam"]
        self.entries = {}
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            tk.Label(form, text=lbl, bg="white", anchor="w").grid(row=i, column=0, sticky="w", pady=6)
            e = tk.Entry(form)
            e.grid(row=i, column=1, sticky="ew", pady=6, padx=(8,0))
            self.entries[key] = e

        # Verify input, add new student to the list, and save to file
        def on_add():
            code = self.entries["code"].get().strip()
            name = self.entries["name"].get().strip()
            # Check for valid integers and range
            try:
                c1 = int(self.entries["c1"].get().strip())
                c2 = int(self.entries["c2"].get().strip())
                c3 = int(self.entries["c3"].get().strip())
                exam = int(self.entries["exam"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Numeric fields must be integers.")
                return
            # Check for duplicate student code
            if not code or not name:
                messagebox.showerror("Error", "Code and name required.")
                return
            if any(other['code'].lower() == code.lower() for other in students):
                messagebox.showerror("Error", "A student with this number already exists.")
                return
            if not (0 <= c1 <= 20 and 0 <= c2 <= 20 and 0 <= c3 <= 20 and 0 <= exam <= 100):
                messagebox.showerror("Error", "Marks out of range.")
                return
            
            # Create new student record
            new = {"code": code, "name": name, "c1": c1, "c2": c2, "c3": c3, "exam": exam}
            recalc_student(new)
            students.append(new)
            save_students_to_file(students)    # Save updated list
            messagebox.showinfo("Added", f"Student {name} added.")
            if callable(on_added):
                on_added()
            self.destroy()

        # Action buttons
        btns = tk.Frame(card, bg="white")
        btns.pack(pady=8)
        tk.Button(btns, text="Add Student", bg="#1f3a5f", fg="white", bd=0, font=("Segoe UI", 11, "bold"),
                  command=on_add).pack(side="left", padx=6)
        tk.Button(btns, text="Cancel", bg="#999", fg="white", bd=0, font=("Segoe UI", 11),
                  command=self.destroy).pack(side="left", padx=6)

        if hasattr(self, "_bg_label"):
            self._bg_label.lower()

# Window for editing marks and details of an existing student record
class EditStudentWindow(tk.Toplevel):
    def __init__(self, parent, idx, student, on_saved=None):
        super().__init__(parent)
        self.title(f"Update: {student['name']} ({student['code']})")
        self.geometry("420x420")
        add_responsive_background(self, MAIN_BG)

        self.idx = idx           # Index in the global students list
        self.student = student
        self.on_saved = on_saved

        shadow, card = create_center_card(self, relwidth=0.92, relheight=0.92)

        header = tk.Label(card, text="Update Student", bg="white", fg="#1f3a5f",
                          font=("Segoe UI", 14, "bold"))
        header.pack(pady=(10,6))

        form = tk.Frame(card, bg="white")
        form.pack(padx=12, pady=6, fill="both", expand=True)
        form.columnconfigure(1, weight=1)

        # Create input fields and labels
        labels = ["Student Number:", "Name:", "Coursework 1 (0-20):", "Coursework 2 (0-20):", "Coursework 3 (0-20):", "Exam (0-100):"]
        keys = ["code", "name", "c1", "c2", "c3", "exam"]
        self.entries = {}
        for i, (lbl, key) in enumerate(zip(labels, keys)):
            tk.Label(form, text=lbl, bg="white", anchor="w").grid(row=i, column=0, sticky="w", pady=6)
            e = tk.Entry(form)
            e.grid(row=i, column=1, sticky="ew", pady=6, padx=(8,0))
            self.entries[key] = e

        # Pre-fill entries with current student data
        self.entries["code"].insert(0, student['code'])
        self.entries["name"].insert(0, student['name'])
        self.entries["c1"].insert(0, str(student['c1']))
        self.entries["c2"].insert(0, str(student['c2']))
        self.entries["c3"].insert(0, str(student['c3']))
        self.entries["exam"].insert(0, str(student['exam']))

       # Verify input, update student record in the list, and save to file
        def on_save():
            new_code = self.entries["code"].get().strip()
            new_name = self.entries["name"].get().strip()
            # Check for valid integers and range
            try:
                nc1 = int(self.entries["c1"].get().strip())
                nc2 = int(self.entries["c2"].get().strip())
                nc3 = int(self.entries["c3"].get().strip())
                ne = int(self.entries["exam"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Numeric fields must be integers.")
                return
            if not new_code or not new_name:
                messagebox.showerror("Error", "Code and name required.")
                return
            # Check for duplicate student code
            for i, other in enumerate(students):
                if i != self.idx and other['code'].lower() == new_code.lower():
                    messagebox.showerror("Error", "Another student already has that code.")
                    return
            if not (0 <= nc1 <= 20 and 0 <= nc2 <= 20 and 0 <= nc3 <= 20 and 0 <= ne <= 100):
                messagebox.showerror("Error", "Marks out of range.")
                return
            
            # Update the student dictionary in the global list
            student['code'] = new_code
            student['name'] = new_name
            student['c1'] = nc1
            student['c2'] = nc2
            student['c3'] = nc3
            student['exam'] = ne
            recalc_student(student)   # Recalculate derived fields(percentage, grade)
            save_students_to_file(students)
            messagebox.showinfo("Saved", f"Student {student['name']} updated.")
            if callable(self.on_saved):
                self.on_saved()
            self.destroy()

        # Action buttons
        btns = tk.Frame(card, bg="white")
        btns.pack(pady=8)
        tk.Button(btns, text="Save Changes", bg="#1f3a5f", fg="white", bd=0, font=("Segoe UI", 11, "bold"),
                  command=on_save).pack(side="left", padx=6)
        tk.Button(btns, text="Cancel", bg="#999", fg="white", bd=0, font=("Segoe UI", 11),
                  command=self.destroy).pack(side="left", padx=6)

        if hasattr(self, "_bg_label"):
            self._bg_label.lower()

# The main application window and primary menu
class StudentManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student Marks Manager")
        self.geometry("1000x700")
        self.minsize(800, 560)

        # Set application icon
        try:
            icon_img = Image.open(ICON_IMG)
            icon_photo = ImageTk.PhotoImage(icon_img)
            self.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"Failed to set root icon with iconphoto: {e}")

        add_responsive_background(self, MENU_BG)    # Use menu background

        # Create the central menu card
        shadow_main, card_main = create_center_card(self, relwidth=0.48, relheight=0.72, shadow_offset=(0.02,0.03), relx=0.63)
        self.card_main = card_main

        # Main title label
        title = tk.Label(card_main, text="Student Manager", bg="white", fg="#1f3a5f",
                         font=("Segoe UI", 20, "bold"))
        title.pack(pady=(18,12))

        btn_frame = tk.Frame(card_main, bg="white")
        btn_frame.pack(pady=8, fill="both", expand=True)
  
        # Common configuration for menu buttons
        btn_cfg = {"font":("Segoe UI", 12, "bold"), "bd":0, "width":26, "height":1, "fg":"white", "bg":"#1f3a5f", "activebackground":"#162a44"}

        # Menu Buttons 
        tk.Button(btn_frame, text=" View All Student Records", command=self.on_view_all, **btn_cfg).pack(pady=6)
        tk.Button(btn_frame, text=" View Individual Student", command=self.on_view_individual, **btn_cfg).pack(pady=6)
        tk.Button(btn_frame, text=" Highest Overall Score", command=self.on_highest, **btn_cfg).pack(pady=6)
        tk.Button(btn_frame, text=" Lowest Overall Score", command=self.on_lowest, **btn_cfg).pack(pady=6)

        tk.Button(btn_frame, text=" Sort Student Records", command=self.on_sort, **btn_cfg).pack(pady=6)
        tk.Button(btn_frame, text=" + Add Student Record", command=self.on_add, **btn_cfg).pack(pady=6)
        tk.Button(btn_frame, text=" Delete Student Record", command=self.on_delete, **btn_cfg).pack(pady=6)
        tk.Button(btn_frame, text=" Update Student Record", command=self.on_update, **btn_cfg).pack(pady=6)

        tk.Button(btn_frame, text=" Exit", command=self.quit, **btn_cfg).pack(pady=(12,6))

        if hasattr(self, "_bg_label"):
            self._bg_label.lower()

    # Opens a window displaying all student records in a table
    def on_view_all(self):
        ViewAllWindow(self)

    # Prompts for student code/name and opens the ShowStudentWindow for a match
    def on_view_individual(self):
        q = simpledialog.askstring("Search Student", "Enter student number or name:")
        if not q:
            return
        ql = q.lower()
        # Linear search for the student
        for s in students:
            if ql in s['code'].lower() or ql in s['name'].lower():
                ShowStudentWindow(self, "Student Record", s)
                return
        messagebox.showinfo("Not found", "No matching student.")

    # Finds and displays the student with the highest overall percentage
    def on_highest(self):
        if not students:
            messagebox.showinfo("No data", "No student records loaded.")
            return
        # Use max() with a key function for search
        top = max(students, key=lambda x: x['percentage'])
        ShowStudentWindow(self, "Highest Overall Score", top)

    # Finds and displays the student with the lowest overall percentage
    def on_lowest(self):
        if not students:
            messagebox.showinfo("No data", "No student records loaded.")
            return
        # Use min() with a key function for search
        low = min(students, key=lambda x: x['percentage'])
        ShowStudentWindow(self, "Lowest Overall Score", low)

    # Prompts for sort order and opens a window with the sorted table
    def on_sort(self):
        if not students:
            messagebox.showinfo("No data", "No student records loaded.")
            return
        order = simpledialog.askstring("Sort Students", "Sort by percentage ascending or descending? (asc/desc)")
        if not order or order.lower() not in ("asc","desc"):
            messagebox.showinfo("Cancelled", "Sort cancelled or invalid input.")
            return
        # Sort the global student list based on percentage
        reverse = order.lower() == "desc"
        sorted_students = sorted(students, key=lambda x: x['percentage'], reverse=reverse)
        SortedWindow(self, sorted_students, order.lower())

    # Opens the AddStudentWindow
    def on_add(self):
        AddStudentWindow(self)

    # Opens the selection window to choose a student, then prompts for delete confirmation
    def on_delete(self):
        def do_delete(idx, student):
            # The callback function executed after selection
            confirm = messagebox.askyesno("Confirm Delete", f"Delete student {student['name']} ({student['code']})?")
            if confirm:
                students.pop(idx)      # Remove student from the global list
                save_students_to_file(students)   # Save the modified list
                messagebox.showinfo("Deleted", f"Student {student['name']} deleted.")
        SelectionWindow(self, "Select student to DELETE", do_delete)

    # Opens the selection window to choose a student, then opens the EditStudentWindow
    def on_update(self):
        def open_edit(idx, student):
            # The callback function executed after selection
            def refresh_callback():
                pass     # A placeholder refresh callback if required later
            EditStudentWindow(self, idx, student, on_saved=refresh_callback)
        SelectionWindow(self, "Select student to UPDATE", open_edit)

if __name__ == "__main__":
    # Start the Tkinter event loop
    app = StudentManagerApp()
    app.mainloop()
