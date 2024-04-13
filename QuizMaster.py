import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import webbrowser
from tkinter.font import Font
from tkinter import Label, Button, LabelFrame, Frame, Entry  # Possibly taking those from ttkbootstrap at some point
from file_parser import parse_quiz_and_flashcards
from expression_parser import parse_expression
import random
import os

LIGHTBULB = "💡"
ERRORS = {1: "An unexpected error occurred.",
          2: "An item was not properly ended.",
          3: "Flashcards cannot have options.",
          4: "Unknown line argument.",
          5: "An item is missing required fields.",
          6: "Answer not in options.",
          7: "Arguments must be between Q or F and END.",
          8: "No content."}
APP_DIR = os.getenv("LOCALAPPDATA") + "\\QuizMaster"  # Sorry guys, Windows only
QUIZZES_DIR = APP_DIR + '\\Quizzes'


def safe_callback(callback):
    """Decorator to catch and print exceptions in Tkinter callbacks."""

    def wrapped(*args, **kwargs):
        try:
            return callback(*args, **kwargs)
        except Exception as e:
            print(f"Error in callback: {e}")
            raise  # Re-raise the exception to see the full traceback in the console

    return wrapped


def import_files(folder: str = None):
    """
    Import the default quiz files from the specified folder.
    :param folder: The folder containing the default quiz files.
    """
    if folder is None:
        folder = QUIZZES_DIR
    errors = []
    result = {}
    nb_success = 0
    for subdir in os.walk(folder):
        for file in subdir[2]:
            if file.endswith(".qz") or file.endswith(".txt"):
                with open(os.path.join(subdir[0], file), 'r') as f:
                    content = f.read()
                    items, error_code = parse_quiz_and_flashcards(content)
                    if error_code != 0:
                        errors.append(f"{file} : Error {error_code} : {ERRORS.get(error_code, 'Unknown error.')}")
                    else:
                        result |= items
                        nb_success += 1
    return result, errors, nb_success


class QuizMasterApp(tk.Tk):
    """
    The main application window for the Quiz Master app.
    """

    def __init__(self):
        super().__init__()
        self.title("Quiz Master")
        self.geometry("600x400")
        global quiz_db
        quiz_db, errors, nb = import_files()
        print(quiz_db)
        if errors:
            messagebox.showerror("Error opening files",
                                 "Errors have been found in the default files:\n" + "\n".join(
                                     errors) + f"\n{nb} other files were opened successfully.")
        self.grid_columnconfigure(0, weight=1)  # Configure the weight of columns to allow for proper resizing
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.buttons = []
        self.button_font = Font(family="Arial", size=12)

        self.title_text = Label(self, text="Welcome to Quiz Master!", font=("Arial", 24))
        self.title_text.place(relx=0.5, rely=0.5, anchor="center")

        self.create_main_buttons()
        self.bind("<Configure>", self.resize_text)

    def create_main_buttons(self):
        # Import Files Button - Top Left
        self.import_button = Button(self, text="Import Quizzes & Cards", command=self.open_import_window,
                                    font=self.button_font)
        self.import_button.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)
        self.buttons.append(self.import_button)

        # View Questions Button - Top Right
        self.view_questions_bank_button = Button(self, text="Question Bank", command=self.open_view_questions_window,
                                                 font=self.button_font)
        self.view_questions_bank_button.grid(row=0, column=1, sticky="nsew", padx=50, pady=50)
        self.buttons.append(self.view_questions_bank_button)

        # Review Flashcards Button - Bottom Left
        self.review_flashcards_button = Button(self, text="Review Flashcards",
                                               command=self.open_review_flashcards_window, font=self.button_font)
        self.review_flashcards_button.grid(row=1, column=0, sticky="nsew", padx=50, pady=50)
        self.buttons.append(self.review_flashcards_button)

        # Start Quiz Button - Bottom Right
        self.start_quiz_button = Button(self, text="Start Quiz", command=self.open_start_quiz_window,
                                        font=self.button_font)
        self.start_quiz_button.grid(row=1, column=1, sticky="nsew", padx=50, pady=50)
        self.buttons.append(self.start_quiz_button)

    def resize_text(self, event):
        # Simple logic to adjust font size based on window width
        new_size = max(8, min(24, int(self.winfo_width() / 80)))
        self.button_font.configure(size=new_size)

    def open_import_window(self):
        import_window = ImportFilesWindow(self)
        import_window.grab_set()  # Optional: makes the import window modal

    def open_view_questions_window(self):
        question_bank_window = QuestionBankWindow(self)
        question_bank_window.grab_set()  # Optional: makes the import window modal

    def open_review_flashcards_window(self):
        messagebox.showinfo("Placeholder", "The Flashcards review hasn't been implemented yet.")

    def open_start_quiz_window(self):
        quiz_windows = QuizOptionsWindow(self)
        quiz_windows.grab_set()  # Optional: makes the import window modal
        # messagebox.showinfo("Placeholder", "This will open the Start Quiz window.")


class ScrollableFrame(Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # Creating a canvas and a scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas, background="#ffffff")

        # Scrollable area which can contain widgets
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.update_idletasks()  # Update geometry

    def update_scrollregion(self):
        self.update_idletasks()  # Update geometry
        self.canvas.config(scrollregion=self.canvas.bbox('all'))


class ImportFilesWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Import Quizzes & Files")

        # File selection
        self.select_button = Button(self, text="Select file", command=self.select_file)
        self.select_button.grid(row=0, column=0, padx=5, pady=5)

        self.file_path_label = Label(self, text="", relief="sunken", anchor="w")
        self.file_path_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.ok_button = Button(self, text="OK", command=self.get_file_content)
        self.ok_button.grid(row=0, column=2, padx=5, pady=5)

        # Configuring the column weights
        self.grid_columnconfigure(1, weight=1)

        # Text area for file content
        self.last_text_change = None
        self.content_text = scrolledtext.ScrolledText(self)
        self.content_text.insert('1.0', "Or paste your content here", )
        self.content_text.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.content_text.bind("<FocusIn>", self.clear_guide_text)
        self.content_text.bind("<<Modified>>", self.on_text_change)

        # Open GPT
        url = "https://chat.openai.com/g/g-xuxEE9uh8-quiz-master"
        self.link_button = Button(self, text="Open QuizMaster GPT", command=lambda: webbrowser.open(url))
        self.link_button.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

        # Questions and flashcards preview
        self.preview_frame = ScrollableFrame(self)
        self.preview_frame.grid(row=1, column=3, sticky="nsew", padx=10, pady=10)

        # Label to display between the text area and submit button
        self.add_to_db_label = Label(self, text="These questions will be added to the database")
        self.add_to_db_label.grid(row=2, column=3, padx=5, pady=5)

        # Submit button
        self.submit_button = Button(self, text="SUBMIT", command=self.submit_data)
        self.submit_button.grid(row=3, column=3, padx=5, pady=5)

        # Configuring the row and column weights for resizing
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(3, weight=1)

    def clear_guide_text(self, event):
        if self.content_text.get('1.0', 'end-1c') == "Or paste your content here":
            self.content_text.delete('1.0', tk.END)

    def on_text_change(self, event=None):
        self.content_text.edit_modified(0)  # reset the modified flag
        if self.last_text_change:
            self.after_cancel(self.last_text_change)
        self.last_text_change = self.after(500, self.update_preview)  # Debounce for 500 ms

    def select_file(self):
        file_path = filedialog.askopenfilename(initialdir="%UserProfile%\\Documents", title="Select file",
                                               filetypes=(("All files", "*.txt;*.qz"), ("Text files", "*.txt"),
                                                          ("Quiz files", "*.qz")))
        if file_path:  # Ensure the user selected a file
            self.file_path_label.configure(text=file_path)
            self.content_text.delete('1.0', tk.END)  # Clear previous content

    def get_file_content(self):
        # Read the content of the file and place it in the content_text area
        file_path = self.file_path_label['text']
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.content_text.delete('1.0', tk.END)
                self.content_text.insert('1.0', content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")

    def update_preview(self):
        # Clear the current content of the preview frame
        if self.content_text.get('1.0', tk.END) != "Or paste your content here\n":
            for widget in self.preview_frame.scrollable_frame.winfo_children():
                widget.destroy()

            # Pre-parsed items
            parsed_items, error_code = parse_quiz_and_flashcards(self.content_text.get('1.0', tk.END))

            if error_code not in (0, 8):
                # Display the error message
                error_message = f"Error {error_code} : {ERRORS.get(error_code, 'Unknown error.')}"
                error_label = Label(self.preview_frame.scrollable_frame, text=error_message, fg="red")
                error_label.pack(pady=10)

            else:

                # Iterate over the parsed items and create widgets for each
                for item in parsed_items.values():
                    if item['type'] == 'quiz':
                        self.create_quiz_preview(item)
                    elif item['type'] == 'flashcard':
                        self.create_flashcard_preview(item)

            self.preview_frame.update_scrollregion()

    def create_quiz_preview(self, quiz):
        # Create a frame for the quiz
        quiz_frame = LabelFrame(self.preview_frame.scrollable_frame, text=quiz['question'], borderwidth=1,
                                relief="solid")
        quiz_frame.pack(fill="x", expand=True, padx=10, pady=5)

        # Add options to the quiz frame
        for key, value in quiz['options'].items():
            option = f"{key}. {value}"
            label = Label(quiz_frame, text=option, anchor="w")
            label.pack(fill="x")

        # Indicate the correct answer
        answer_label = Label(quiz_frame, text=f"Answer: {quiz['answer']}", anchor="w", fg="green")
        answer_label.pack(fill="x")

        if 'tags' in quiz:
            tags_label = Label(quiz_frame, text="Tags: " + ", ".join(quiz['tags']), anchor="w", fg="gray")
            tags_label.pack(fill="x")

    def create_flashcard_preview(self, flashcard):
        # Create a frame for the flashcard
        flashcard_frame = LabelFrame(self.preview_frame.scrollable_frame, text="Flashcard", borderwidth=1,
                                     relief="solid")
        flashcard_frame.pack(fill="x", expand=True, padx=10, pady=5)

        # Add fact and answer to the flashcard frame
        fact_label = Label(flashcard_frame, text=flashcard['fact'], anchor="w")
        fact_label.pack(fill="x")

        answer_label = Label(flashcard_frame, text=f"{flashcard['answer']}", anchor="w", fg="green")
        answer_label.pack(fill="x")

        if 'tags' in flashcard:
            tags_label = Label(flashcard_frame, text="Tags: " + ", ".join(flashcard['tags']), anchor="w", fg="gray")
            tags_label.pack(fill="x")

    def submit_data(self):
        content = self.content_text.get('1.0', tk.END)
        items, error_code = parse_quiz_and_flashcards(content)
        if error_code != 0:
            messagebox.showerror("Error", f"Error {error_code} : {ERRORS.get(error_code, 'Unknown error.')}")
        else:
            try:
                global quiz_db
                quiz_db |= items
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            else:
                messagebox.showinfo("Success",
                                    """Data submitted successfully!
Note: This data will not be saved after the app is closed.
If you want this data to be saved, you can add it to a file in the AppData/Local/QuizMaster/Quizzes folder.
"""
                                    )
                self.content_text.delete('1.0', tk.END)


class QuestionBankWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Question Bank")
        self.geometry("600x400")

        self.scrollable_frame = ScrollableFrame(self)
        self.scrollable_frame.pack(fill="both", expand=True)

        self.last_width = self.winfo_width()
        self.resize_after_id = None

        self.populate_bank()
        self.bind("<Configure>", self.on_resize)

    @safe_callback
    def on_resize(self, event):
        # This method is triggered whenever the window is resized.
        # Call the method to recalculate the layout of items.
        current_width = self.winfo_width()
        if self.last_width != current_width:
            self.last_width = current_width
            if self.resize_after_id is not None:
                self.after_cancel(self.resize_after_id)
            self.resize_after_id = self.after(100, self.populate_bank)  # Delay repopulating

    @safe_callback
    def populate_bank(self):
        # Clear current content
        for widget in self.scrollable_frame.scrollable_frame.winfo_children():
            widget.destroy()

        # Update the scrollable_frame's geometry
        self.scrollable_frame.update_idletasks()

        # Get the width of the scrollable_frame now that it has been updated
        frame_width = self.scrollable_frame.winfo_width()

        # Keep track of the current row frame
        current_row_frame = None
        row_width = 0

        # Iterate over the parsed items and create widgets for each
        for item_key in quiz_db:
            item = quiz_db[item_key]
            item_frame_width = self.get_item_frame_width(item)

            if current_row_frame is None or row_width + item_frame_width > frame_width:
                # If there's no row frame or we've exceeded the width, start a new row
                current_row_frame = Frame(self.scrollable_frame.scrollable_frame)
                current_row_frame.pack(fill='x')
                row_width = 0  # Reset the row width

            if item['type'] == 'quiz':
                self.create_quiz_preview(item_key, current_row_frame)
            elif item['type'] == 'flashcard':
                self.create_flashcard_preview(item_key, current_row_frame)

            # Increment the row width by the width of the newly added item frame
            row_width += item_frame_width

        self.scrollable_frame.update_scrollregion()

    @safe_callback
    def get_item_frame_width(self, item):
        return Font().measure(item['question'] if item['type'] == 'quiz' else item['fact'])

    @safe_callback
    def create_quiz_preview(self, key, parent_frame):
        quiz_frame = LabelFrame(parent_frame, text="Quiz", borderwidth=1, relief="solid")
        quiz_frame.pack(side="left", expand=True, padx=10, pady=5)
        quiz_frame.bind("<Button-1>", lambda event, k=key: self.edit_item(k))

        for child in quiz_frame.winfo_children():
            child.bind("<Button-1>", lambda event, k=key: self.edit_item(k))

        question_label = Label(quiz_frame, text=quiz_db[key]['question'], anchor="w")
        question_label.pack(fill="x")
        question_label.bind("<Button-1>", lambda event, k=key: self.edit_item(k))

        # ... add options and answer labels ...

    @safe_callback
    def create_flashcard_preview(self, key, parent_frame):
        flashcard_frame = LabelFrame(parent_frame, text="Flashcard", borderwidth=1,
                                     relief="solid")
        flashcard_frame.pack(side="left", expand=True, padx=10, pady=5)
        flashcard_frame.bind("<Button-1>", lambda event, k=key: self.edit_item(k))

        for child in flashcard_frame.winfo_children():
            child.bind("<Button-1>", lambda event, k=key: self.edit_item(k))

        fact_label = Label(flashcard_frame, text=quiz_db[key]['fact'], anchor="w")
        fact_label.pack(fill="x")
        fact_label.bind("<Button-1>", lambda event, k=key: self.edit_item(k))

    def edit_item(self, key):
        # Open EditItemWindow
        edit_window = EditItemWindow(master=self, item_key=key)
        self.wait_window(edit_window)


class EditItemWindow(tk.Toplevel):
    def __init__(self, master: QuestionBankWindow = None, item_key=None):
        super().__init__(master)
        self.master: QuestionBankWindow = master  # To stop PyCharm from freaking out when I call its method.
        self.title("Edit Item")
        self.geometry("400x300")

        self.item_key = item_key
        self.item = quiz_db[item_key]

        self.entries = {}  # To keep track of Entry widgets for options

        self.create_widgets()

        self.save_button = tk.Button(self, text="Save", command=self.save)
        self.save_button.pack(side="bottom", pady=10)

    def create_widgets(self):
        match self.item['type']:
            case 'quiz':
                Label(self, text="Question:").pack(fill='x')
                self.question_entry = Entry(self)
                self.question_entry.insert(0, self.item.get('question', ''))
                self.question_entry.pack(fill='x', expand=True, padx=10)

                self.correct_answer_var = tk.StringVar(value=self.item.get('answer', ''))

                options_frame = tk.Frame(self)  # Frame to contain option entries and radio buttons
                options_frame.pack(fill='x', expand=True, padx=10)

                for option_key, option_value in self.item.get('options', {}).items():
                    option_frame = tk.Frame(options_frame)  # Frame for each option
                    option_frame.pack(fill='x', expand=True)

                    entry = Entry(option_frame)
                    entry.insert(0, option_value)
                    entry.pack(side='left', fill='x', expand=True, padx=(10, 20))
                    self.entries[option_key] = entry

                    # Radio button for selecting the correct answer
                    rb = tk.Radiobutton(option_frame, variable=self.correct_answer_var, value=option_key)
                    rb.pack(side='left')

                # Explanation field
                Label(self, text="Explanation:").pack(fill='x')
                self.explanation_entry = Entry(self)
                self.explanation_entry.insert(0, self.item.get('explanation', ''))
                self.explanation_entry.pack(fill='x', expand=True, padx=10)

                # Tags field
                Label(self, text="Tags:").pack(fill='x')
                self.tags_entry = Entry(self)
                self.tags_entry.insert(0, ", ".join(self.item.get('tags', [])))
                self.tags_entry.pack(fill='x', expand=True, padx=10)

            case 'flashcard':
                Label(self, text="Fact:").pack(fill='x')
                self.fact_entry = Entry(self)
                self.fact_entry.insert(0, self.item.get('fact', ''))
                self.fact_entry.pack(fill='x', expand=True, padx=10)

                Label(self, text="Answer:").pack(fill='x')
                self.answer_entry = Entry(self)
                self.answer_entry.insert(0, self.item.get('answer', ''))
                self.answer_entry.pack(fill='x', expand=True, padx=10)

                # Even flashcards get explanation and tags fields for consistency
                Label(self, text="Explanation:").pack(fill='x')
                self.explanation_entry = Entry(self)
                self.explanation_entry.insert(0, self.item.get('explanation', ''))
                self.explanation_entry.pack(fill='x', expand=True, padx=10)

                Label(self, text="Tags:").pack(fill='x')
                self.tags_entry = Entry(self)
                self.tags_entry.insert(0, ", ".join(self.item.get('tags', [])))
                self.tags_entry.pack(fill='x', expand=True, padx=10)

    def save(self):
        # Update the item based on its type
        match self.item['type']:
            case 'quiz':
                self.item['question'] = self.question_entry.get()
                self.item['options'] = {key: entry.get() for key, entry in self.entries.items()}
                self.item['answer'] = self.correct_answer_var.get()
                self.item['explanation'] = self.explanation_entry.get()
                self.item['tags'] = [tag.strip() for tag in self.tags_entry.get().split(',')]
            case 'flashcard':
                self.item['fact'] = self.fact_entry.get()
                self.item['answer'] = self.answer_entry.get()
                self.item['explanation'] = self.explanation_entry.get()
                self.item['tags'] = [tag.strip() for tag in self.tags_entry.get().split(',')]

        quiz_db[self.item_key] = self.item  # Commit changes to the database
        messagebox.showinfo("Success", "Item updated successfully.\nDo note that only the current session is updated.")
        self.master.populate_bank()
        self.destroy()  # Close the window


class QuizOptionsWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Quiz Options and Tag Selection")
        self.geometry("500x400")

        # Configure grid layout
        self.all_tags = {tag for item in quiz_db.values() for tag in item.get('tags', []) if item['type'] == 'quiz'}

        # Grid configuration for layout management
        self.grid_columnconfigure(0, weight=1)
        for i in range(5):  # Configure rows to place elements
            self.grid_rowconfigure(i, weight=1)

        # Tag entry field
        tk.Label(self, text="Enter tags (use AND, OR, NOT for filtering):").grid(row=0, column=0, sticky="w", padx=10,
                                                                                 pady=(10, 0))
        self.tag_entry = tk.Entry(self)
        self.tag_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.timer_check = tk.IntVar(value=0)
        tk.Checkbutton(self, text="Enable Timer", variable=self.timer_check, command=self.toggle_timer_option).grid(
            row=2, column=0, padx=10, pady=5, sticky="w")

        # Timer duration controls - Initially hidden
        self.timer_duration_label = tk.Label(self, text="Timer Duration (seconds):")
        self.timer_duration_spinbox = tk.Spinbox(self, from_=10, to=600)
        # Positioning handled by toggle_timer_option

        # Number of questions and hints in subsequent rows
        tk.Label(self, text="Number of Questions:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.questions_default_value = tk.StringVar(value=10)
        self.questions_spinbox = tk.Spinbox(self, from_=1, to=50, textvariable=self.questions_default_value)
        self.questions_spinbox.grid(row=4, column=1, sticky="ew", padx=10, pady=5)

        tk.Label(self, text="Number of Hints:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.hints_spinbox = tk.Spinbox(self, from_=0, to=10)
        self.hints_spinbox.grid(row=5, column=1, sticky="ew", padx=10, pady=5)

        # Start Quiz button
        tk.Button(self, text="Start Quiz", command=self.start_quiz).grid(row=6, column=0, columnspan=2, pady=10,
                                                                         sticky="ew", padx=10)

        # Scrollable list of tags positioned at the bottom
        self.tag_list_label = tk.Label(self, text="Available Tags:")
        self.tag_list_label.grid(row=7, column=0, padx=10, pady=(5, 0), sticky="w")
        self.tag_list = tk.Listbox(self, height=4)
        self.tag_list_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.tag_list.yview)
        self.tag_list.configure(yscrollcommand=self.tag_list_scrollbar.set)
        for tag in self.all_tags:
            self.tag_list.insert(tk.END, tag)
        self.tag_list.grid(row=8, column=0, sticky="ew", padx=10)
        self.tag_list_scrollbar.grid(row=8, column=1, sticky="ns")
        self.tag_list.bind('<Double-1>', self.on_tag_double_click)

    def toggle_timer_option(self):
        if self.timer_check.get() == 1:
            self.timer_duration_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
            self.timer_duration_spinbox.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        else:
            self.timer_duration_label.grid_remove()
            self.timer_duration_spinbox.grid_remove()

    def on_tag_double_click(self, event):
        selection = self.tag_list.curselection()
        if selection:
            selected_tag = self.tag_list.get(selection[0])
            current_text = self.tag_entry.get()
            new_text = f"{current_text} {selected_tag}" if current_text else selected_tag
            self.tag_entry.delete(0, tk.END)
            self.tag_entry.insert(0, new_text.strip())

    def start_quiz(self):
        # Parse tag entry and apply options
        tags = self.tag_entry.get()
        use_timer = self.timer_check.get() == 1
        num_questions = int(self.questions_spinbox.get())
        num_hints = int(self.hints_spinbox.get())
        timer_seconds = int(self.timer_duration_spinbox.get()) if use_timer else 0
        available_questions = []
        for key, item in quiz_db.items():
            if item['type'] == 'quiz' and parse_expression(tags, item.get('tags', [])):
                available_questions.append(key)

        if len(available_questions) < num_questions:
            messagebox.showwarning("Warning", "Not enough questions available for the selected tags.")
            quiz_questions = available_questions.copy()
        elif len(available_questions) == num_questions:
            random.shuffle(available_questions)
            quiz_questions = available_questions.copy()
        else:
            quiz_questions = random.sample(available_questions, num_questions)

        # Placeholder for starting the quiz with these options
        for key in quiz_questions:
            print(quiz_db[key])

        quiz_window = QuizWindow(questions=[quiz_db[key] for key in quiz_questions], master=self, timer=use_timer,
                                 duration=timer_seconds, hints=num_hints)
        self.wait_window(quiz_window)
        self.destroy()


class QuizWindow(tk.Toplevel):
    def __init__(self, questions, master=None, **kwargs):
        super().__init__(master)
        self.title("Quiz")
        self.geometry("800x600")  # Example size, adjust as needed

        self.questions = questions
        self.current_question_index = 0
        self.answered = None
        self.current_question = None
        self.current_options = None

        self.use_timer = kwargs.get('timer', False)
        self.time_limit = kwargs.get('duration', 30)
        self.hints_used = 0
        self.max_hints = kwargs.get('hints', 0)
        self.good_answers = 0

        self.next_button = tk.Button(self, text="Next", command=self.next_question)
        self.hint_button = tk.Button(self, text=str(self.max_hints) + LIGHTBULB, command=self.show_hint)
        self.hint_button.place(relx=1.0, rely=0.0, x=-2, y=2, anchor="ne")

        self.question_label = tk.Label(self, font=('Arial', 16))
        self.question_label.pack(pady=(20, 10), padx=20)

        self.options_frame = tk.Frame(self)
        self.options_frame.pack(fill="both", expand=True, padx=20, pady=20)

        if self.use_timer:
            self.timer_label = tk.Label(self, font=('Arial', 14), text="00:30")
            self.timer_label.pack(side="top", fill="x", padx=20, pady=5)

        self.explanation_label = tk.Label(self, font=('Arial', 12), wraplength=500)
        self.explanation_label.pack(side="bottom", fill="x", padx=20, pady=10)

        self.button_font = Font(family="Arial", size=14)

        self.update_content(self.questions[self.current_question_index])

    def update_content(self, q):
        self.hint_button.config(state="normal")
        self.current_question = q
        self.next_button.pack_forget()
        self.explanation_label.config(text="")  # Clear explanation text
        self.question_label.config(text=q['question'])
        self.answered = False  # Reset answered flag for the new question
        self.current_options = q['options'].items()
        self.display_options()
        if self.use_timer:
            self.start_timer()

    def display_options(self):
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        rows = (len(self.current_options) + 1) // 2
        for index, (option_key, option_value) in enumerate(self.current_options):
            row = index // 2
            column = index % 2
            button = tk.Button(self.options_frame, text=f"{option_key}: {option_value}", padx=10, pady=5,
                               font=self.button_font)
            button.grid(row=row, column=column, sticky="nsew", padx=5, pady=5)
            button.bind("<Button-1>",
                        lambda event, correct=(option_key == self.current_question['answer']),
                               widget=button: self.answer_selected(correct,
                                                                   widget))

            self.options_frame.grid_columnconfigure(column, weight=1)
        for row_index in range(rows):
            self.options_frame.grid_rowconfigure(row_index, weight=1)

    def show_hint(self):
        right_answer = [(k, v) for k, v in self.current_options if k == self.current_question['answer']]
        wrong_answers = [(k, v) for k, v in self.current_options if k != self.current_question['answer']]
        random.shuffle(wrong_answers)
        self.current_options = right_answer + wrong_answers[:1]

        print(self.current_options)

        self.hints_used += 1
        if self.hints_used == self.max_hints:
            self.hint_button.place_forget()
        else:
            self.hint_button.config(text=str(self.max_hints - self.hints_used) + LIGHTBULB)

        self.hint_button.config(state="disabled")

        self.display_options()

    def start_timer(self):
        self.time_left = self.time_limit
        self.timer_label.config(text=f"00:{self.time_left:02}")
        self.update_timer()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.config(text=f"00:{self.time_left:02}")
            self.timer_id = self.after(1000, self.update_timer)
        else:
            self.time_up()

    def time_up(self):
        if not self.answered:
            self.answer_selected(False, None)  # Handle time up as incorrect answer

    def answer_selected(self, is_correct, widget):
        if self.answered:  # Check if an answer has already been processed
            return
        self.answered = True  # Set the answered flag

        # Disable further clicks immediately after one has been processed
        for child in self.options_frame.winfo_children():
            if isinstance(child, tk.Button):
                child.config(state="disabled")

        if self.use_timer:
            self.after_cancel(self.timer_id)

        if is_correct:
            if widget:
                widget.config(bg="green", fg="white", disabledforeground="white")
            self.good_answers += 1
        elif widget:
            widget.config(bg="red", fg="black", disabledforeground="black")

        if not is_correct:
            correct_key = self.current_question['answer']  # Assuming 'answer' holds the key of the correct option
            for child in self.options_frame.winfo_children():
                if isinstance(child, tk.Button):
                    option_key = child.cget("text").split(":")[
                        0].strip()  # Assumes button text is like 'A: Option Text'
                    if option_key == correct_key:
                        child.config(bg="green", fg="white", disabledforeground="white")
                        break

        explanation = self.current_question.get('explanation', '')
        self.explanation_label.config(text=f"Explanation : {explanation}" if explanation else explanation)

        self.hint_button.config(state="disabled")

        self.next_button.pack(side="bottom", pady=10)

    def next_question(self):
        if self.current_question_index + 1 < len(self.questions):
            self.current_question_index += 1
            self.update_content(self.questions[self.current_question_index])
        else:
            self.end_quiz()

    def end_quiz(self):
        tk.messagebox.showinfo("Quiz Completed",
                               f"""You have completed the quiz using {self.hints_used} hints!
You got {self.good_answers} good answers, and your grade is {int(80 * self.good_answers / len(self.questions)) / 4}/20.""")
        self.destroy()


if __name__ == "__main__":

    if not os.path.isdir(APP_DIR):
        os.mkdir(APP_DIR)
        os.mkdir(QUIZZES_DIR)
    elif not os.path.isdir(QUIZZES_DIR):
        os.mkdir(QUIZZES_DIR)

    quiz_db: dict = {}

    app = QuizMasterApp()
    app.mainloop()
