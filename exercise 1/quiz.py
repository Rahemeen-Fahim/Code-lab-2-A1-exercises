import tkinter as tk
# To open images, display them and read GIF animation frames.
from PIL import Image, ImageTk, ImageSequence
import random
# Use math for the sine movement that makes the background symbols move.
import math
# To find image files in the same folder as this Python program.
from pathlib import Path
import pygame 

# Find the folder containing this Python file so image paths work even if the program is run elsewhere.
IMAGE_FOLDER = Path(__file__).resolve().parent

# This is to initialise and play background music throughout the session.
pygame.mixer.init()
pygame.mixer.music.load(IMAGE_FOLDER / "music.mp3")

root = tk.Tk()
root.title("Maths Quiz")

# Load the application window icon.
icon = tk.PhotoImage(file=IMAGE_FOLDER / "quiz.png")
root.iconphoto(True, icon)

root.geometry("1220x880")
root.minsize(1020, 740)
root.config(bg="#F6D5DC")

BLUSH_BG = "#F6D5DC"
NOTEBOOK_LINE = "#EBBCC7"
MARGIN_LINE = "#DF9BAE"
CARD_BG = "#FFF8FA"
CARD_ALT = "#FCECF0"
INK_OUTLINE = "#3A2E39"
INK_MUTED = "#72596B"
ROSE_BTN = "#E99CB3"
ROSE_HOVER = "#DC849E"
ROSE_DARK = "#9E3E5E"
LAV_BTN = "#D7C5EC"
LAV_HOVER = "#C3ACE0"
LAV_DARK = "#644B82"
BOW_GOLD = "#F2CFA5"
GOLD_DARK = "#8E6234"
SUCCESS_FG = "#2E7D5B"
SUCCESS_BG = "#E3F5EC"
ERROR_FG = "#B53852"
ERROR_BG = "#FDE4EA"

FONT_DISPLAY = "Georgia"
FONT_UI = "Segoe UI"
EQUATION_DIGIT_FONT = (FONT_UI, 48, "bold")
EQUATION_OPERATOR_FONT = (FONT_UI, 44, "bold")

# These variables store the quiz progress and the values needed while a question is being answered.
score = 0
streak = 0
question_number = 0
attempts = 0
hint_used = False
minimum_value = 1
maximum_value = 9
difficulty_level = ""
first_number = 0
second_number = 0
current_operation = "+"
correct_answer = 0
answer_locked = False

# Tkinter uses these timer IDs to keep track of animations that may need to be stopped later.
gif_frame_timer = None
background_motion_timer = None
score_counter_timer = None
motion_tick = 0

# Lists hold the loaded animation frames and the background symbols currently moving on the canvas.
sparkles_frames = []
confetti_frames = []
floating_symbols = []


# Load one image file and resize it to fit the space available on the screen.
def load_image(filename, width, height):
    # If an image is missing or cannot be opened, return None instead of stopping the whole quiz.
    try:
        image = Image.open(IMAGE_FOLDER / filename).convert("RGBA")
        image.thumbnail((width, height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception:
        return None


# Load every frame of a GIF so Tkinter can display the frames one after another.
def load_animation(filename, width, height):
    try:
        gif = Image.open(IMAGE_FOLDER / filename)
        frames = []

        # Go through the GIF one frame at a time, rather than treating it as one still image.
        for frame in ImageSequence.Iterator(gif):
            rgba = frame.convert("RGBA")
            rgba.thumbnail((width, height), Image.Resampling.LANCZOS)

            # Convert each frame into a Tkinter compatible image and keep it in memory.
            photo = ImageTk.PhotoImage(rgba)

            # Read how long this frame should appear; use 95 milliseconds if the GIF has no timing information.
            duration = frame.info.get("duration", 95)
            frames.append((photo, duration))

        return frames
    except Exception:
        return []


# Load the pictures used on the welcome, level selection, and results screens.
calculator_img = load_image("calculator.png", 145, 145)
books_img = load_image("books.png", 140, 140)
trophy_img = load_image("trophy.png", 136, 136)
stationery_img = load_image("stationary.png", 116, 116)

# Load the decorative GIF animations used for correct answers and the final results screen.
sparkles_frames = load_animation("sparkles.gif", 160, 95)
confetti_frames = load_animation("confetti.gif", 250, 125)


# Create buttons through one reusable function so all buttons share the same design and behaviour.
def create_button(parent, text, bg, hover_bg, fg=INK_OUTLINE, width=24, pady=12, font_size=13, command=None):
    button = tk.Button(
        parent,
        text=text,
        font=(FONT_UI, font_size, "bold"),
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        width=width,
        pady=pady,
        relief="solid",
        bd=3,
        highlightbackground=INK_OUTLINE,
        highlightcolor=INK_OUTLINE,
        highlightthickness=2,
        cursor="hand2",
        command=command,
    )

    # Change the button colour while the mouse is over it to give the user a visual response.
    button.bind("<Enter>", lambda _event: button.config(bg=hover_bg))

    # Restore the button's normal colour when the mouse moves away.
    button.bind("<Leave>", lambda _event: button.config(bg=bg))

    return button


# Create a reusable card frame. Other parts of the program can choose its spacing and background colour.
def create_card(parent, padx=48, pady=34, bg=CARD_BG, border_px=4):
    return tk.Frame(
        parent,
        bg=bg,
        padx=padx,
        pady=pady,
        highlightbackground=INK_OUTLINE,
        highlightcolor=INK_OUTLINE,
        highlightthickness=border_px,
    )


# The canvas acts as the background layer, allowing drawings and screen frames to appear together.
quiz_canvas = tk.Canvas(root, bg=BLUSH_BG, highlightthickness=0, bd=0)
quiz_canvas.pack(fill="both", expand=True)


# Keep the background drawings behind the quiz screens and arrange them in the correct order.
def arrange_canvas_layers():
    # Check whether the notebook lines have already been drawn on the canvas.
    has_lines = bool(quiz_canvas.find_withtag("notebook_lines"))

    # Check whether the floating maths symbols have already been added.
    has_symbols = bool(quiz_canvas.find_withtag("floating_symbols"))

    # Check whether the corner illustrations have already been drawn.
    has_decor = bool(quiz_canvas.find_withtag("corner_decor"))

    # Move the notebook lines to the very back so they do not cover other decorations.
    if has_lines:
        quiz_canvas.tag_lower("notebook_lines")

    # Place the floating symbols above the notebook lines but below the corner illustrations.
    if has_symbols and has_lines:
        quiz_canvas.tag_raise("floating_symbols", "notebook_lines")

    # Keep the corner illustrations above the floating symbols.
    if has_decor and has_symbols:
        quiz_canvas.tag_raise("corner_decor", "floating_symbols")
    elif has_decor and has_lines:
        quiz_canvas.tag_raise("corner_decor", "notebook_lines")

    # Raise each screen frame above the background drawings so its buttons and text remain visible.
    for window_id in screen_windows.values():
        quiz_canvas.tag_raise(window_id)


# Draw the notebook style background. The optional event argument lets this function run after resizing.
def draw_notebook_background(_event=None):
    quiz_canvas.delete("corner_decor")
    quiz_canvas.delete("notebook_lines")

    # Read the current window size, while keeping a minimum drawing area for smaller windows.
    canvas_w = max(root.winfo_width(), 920)
    canvas_h = max(root.winfo_height(), 700)

    # Draw evenly spaced horizontal lines to make the background look like notebook paper.
    for y in range(44, canvas_h, 44):
        quiz_canvas.create_line(0, y, canvas_w, y, fill=NOTEBOOK_LINE, width=1, tags="notebook_lines")

    quiz_canvas.create_line(74, 0, 74, canvas_h, fill=MARGIN_LINE, width=3, tags="notebook_lines")

    # Draw the small formula card in the top left corner of the background.
    quiz_canvas.create_rectangle(28, 28, 246, 142, fill=INK_OUTLINE, outline="", tags="corner_decor")
    quiz_canvas.create_rectangle(22, 22, 240, 136, fill=CARD_BG, outline=INK_OUTLINE, width=3, tags="corner_decor")
    quiz_canvas.create_text(131, 48, text="x² + y² = r²", fill=INK_OUTLINE, font=(FONT_DISPLAY, 13, "bold"), tags="corner_decor")
    quiz_canvas.create_text(131, 78, text="π ≈ 3.14159", fill=ROSE_DARK, font=(FONT_DISPLAY, 12, "italic"), tags="corner_decor")
    quiz_canvas.create_text(131, 109, text="sin²α + cos²α = 1", fill=LAV_DARK, font=(FONT_DISPLAY, 11, "bold"), tags="corner_decor")

    # Draw a calculator using canvas shapes and text, rather than loading a separate calculator image.
    calc_x = canvas_w - 190
    calc_y = 26
    quiz_canvas.create_rectangle(calc_x + 7, calc_y + 7, calc_x + 161, calc_y + 211, fill=INK_OUTLINE, outline="", tags="corner_decor")
    quiz_canvas.create_rectangle(calc_x, calc_y, calc_x + 154, calc_y + 204, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="corner_decor")
    quiz_canvas.create_rectangle(calc_x + 18, calc_y + 18, calc_x + 136, calc_y + 56, fill="#DCE5DF", outline=INK_OUTLINE, width=2, tags="corner_decor")
    quiz_canvas.create_text(calc_x + 77, calc_y + 37, text="MATHS", fill=INK_OUTLINE, font=(FONT_UI, 10, "bold"), tags="corner_decor")

    # These are the labels shown on the calculator keys.
    keypad = ["7", "8", "9", "+", "4", "5", "6", "−", "1", "2", "3", "="]

    # Use enumerate so each key has both its position number and its displayed character.
    for idx, key in enumerate(keypad):
        # The remainder gives the key's column number, from 0 to 3.
        col = idx % 4

        # Integer division gives the key's row number.
        row = idx // 4

        key_x1 = calc_x + 18 + col * 30
        key_y1 = calc_y + 70 + row * 39

        # Give the operation keys a different colour from the number keys.
        key_fill = LAV_BTN if key in ("+", "−", "=") else CARD_BG
        quiz_canvas.create_rectangle(key_x1, key_y1, key_x1 + 25, key_y1 + 31, fill=key_fill, outline=INK_OUTLINE, width=2, tags="corner_decor")
        quiz_canvas.create_text(key_x1 + 12, key_y1 + 15, text=key, fill=INK_OUTLINE, font=(FONT_UI, 9, "bold"), tags="corner_decor")

    # Draw an open notebook in the bottom left corner of the background.
    book_x = 20
    book_y = canvas_h - 166
    quiz_canvas.create_rectangle(book_x + 5, book_y + 5, book_x + 205, book_y + 144, fill=INK_OUTLINE, outline="", tags="corner_decor")
    quiz_canvas.create_rectangle(book_x, book_y, book_x + 200, book_y + 139, fill=CARD_BG, outline=INK_OUTLINE, width=3, tags="corner_decor")
    quiz_canvas.create_line(book_x + 100, book_y, book_x + 100, book_y + 139, fill=INK_OUTLINE, width=3, tags="corner_decor")

    # Add ruled lines to both pages of the illustrated notebook.
    for line_y in range(book_y + 22, book_y + 128, 20):
        quiz_canvas.create_line(book_x + 14, line_y, book_x + 88, line_y, fill=NOTEBOOK_LINE, width=1, tags="corner_decor")
        quiz_canvas.create_line(book_x + 112, line_y, book_x + 186, line_y, fill=NOTEBOOK_LINE, width=1, tags="corner_decor")

    quiz_canvas.create_text(book_x + 51, book_y + 40, text="∑ n = n(n+1)/2", fill=INK_OUTLINE, font=(FONT_DISPLAY, 9, "bold"), tags="corner_decor")
    quiz_canvas.create_text(book_x + 51, book_y + 78, text="a² + b² = c²", fill=ROSE_DARK, font=(FONT_DISPLAY, 10, "bold"), tags="corner_decor")
    quiz_canvas.create_text(book_x + 149, book_y + 48, text="✦  π  ✦", fill=LAV_DARK, font=(FONT_DISPLAY, 12, "bold"), tags="corner_decor")
    quiz_canvas.create_text(book_x + 149, book_y + 88, text="PRACTICE", fill=INK_OUTLINE, font=(FONT_UI, 9, "bold"), tags="corner_decor")

    # Draw the books and ribbon decoration in the bottom right corner.
    stack_x = canvas_w - 214
    stack_y = canvas_h - 178

    # Each pair contains a book colour and its width; enumerate gives each book its vertical position.
    for band_idx, (band_color, band_width) in enumerate([(LAV_BTN, 168), (BOW_GOLD, 152), (ROSE_BTN, 178)]):
        shelf_y = stack_y + 56 + band_idx * 29
        quiz_canvas.create_rectangle(stack_x, shelf_y, stack_x + band_width, shelf_y + 27, fill=band_color, outline=INK_OUTLINE, width=3, tags="corner_decor")

    bow_center_x = stack_x + 86
    bow_center_y = stack_y + 32
    quiz_canvas.create_oval(bow_center_x - 48, bow_center_y - 19, bow_center_x - 6, bow_center_y + 19, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="corner_decor")
    quiz_canvas.create_oval(bow_center_x + 6, bow_center_y - 19, bow_center_x + 48, bow_center_y + 19, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="corner_decor")
    quiz_canvas.create_polygon(bow_center_x - 8, bow_center_y + 10, bow_center_x - 28, bow_center_y + 38, bow_center_x - 6, bow_center_y + 29, fill=ROSE_DARK, outline=INK_OUTLINE, width=2, tags="corner_decor")
    quiz_canvas.create_polygon(bow_center_x + 8, bow_center_y + 10, bow_center_x + 28, bow_center_y + 38, bow_center_x + 6, bow_center_y + 29, fill=ROSE_DARK, outline=INK_OUTLINE, width=2, tags="corner_decor")
    quiz_canvas.create_oval(bow_center_x - 12, bow_center_y - 12, bow_center_x + 12, bow_center_y + 12, fill=ROSE_DARK, outline=INK_OUTLINE, width=3, tags="corner_decor")

    arrange_canvas_layers()


# Store the maths symbols, their colours, and their font sizes for the moving background effect.
MATH_SYMBOLS = [
    ("+", "#8C5A72", 22),
    ("−", "#8C5A72", 22),
    ("=", "#9A6B82", 21),
    ("π", "#7E5D9E", 20),
    ("∞", "#A3637D", 21),
    ("✦", "#8E6BB8", 21),
]


# Create decorative maths symbols at random positions on the canvas.
def create_floating_symbols(count=24):
    # Remove the old symbols first so calling this function does not leave duplicates behind.
    quiz_canvas.delete("floating_symbols")

    # Clear the list as well, because it stores the canvas IDs and movement details of the old symbols.
    floating_symbols.clear()

    canvas_w = max(root.winfo_width(), 1220)
    canvas_h = max(root.winfo_height(), 880)
    min_x = 96
    max_x = max(min_x + 40, canvas_w - 96)

    # Create the requested number of symbols, giving each one its own starting position and movement.
    for index in range(count):
        # Cycle through the symbol list so the different maths symbols are reused.
        symbol, color, size = MATH_SYMBOLS[index % len(MATH_SYMBOLS)]
        x = random.randint(min_x, max_x)
        y = random.randint(40, canvas_h - 40)

        # A negative vertical speed makes the symbol slowly move upwards.
        vy = random.uniform(-0.55, -0.2)

        # Give each symbol a slightly different horizontal speed.
        base_vx = random.uniform(-0.3, 0.3)

        # A random phase makes each symbol sway at a different point in its movement cycle.
        phase = random.uniform(0, math.pi * 2)

        item_id = quiz_canvas.create_text(
            x,
            y,
            text=symbol,
            fill=color,
            font=(FONT_DISPLAY, size, "bold"),
            tags="floating_symbols",
        )

        # Store each symbol's canvas ID and movement values so it can be updated later.
        floating_symbols.append({
            "id": item_id,
            "vy": vy,
            "base_vx": base_vx,
            "phase": phase,
        })

    arrange_canvas_layers()


# Move the background symbols repeatedly to create a gentle animation.
def update_background_motion():
    # These variables are shared with other functions so the animation timer can be tracked.
    global background_motion_timer, motion_tick

    # Increase the animation step. This value is used to calculate the symbols' side to  side movement.
    motion_tick += 1

    canvas_w = max(root.winfo_width(), 200)
    canvas_h = max(root.winfo_height(), 200)
    min_x = 96
    max_x = max(min_x + 40, canvas_w - 96)

    # Update the position of every floating symbol.
    for item in floating_symbols:
        # Sine creates a smooth back and forth movement instead of a sudden left right jump.
        sway = math.sin(motion_tick * 0.035 + item["phase"]) * 0.35

        # Move the symbol using its normal speed plus the gentle side to side sway.
        quiz_canvas.move(item["id"], item["base_vx"] + sway, item["vy"])

        # Get the symbol's current canvas coordinates so we can check whether it has left the screen.
        coords = quiz_canvas.coords(item["id"])

        if coords:
            cx, cy = coords[0], coords[1]

            # When a symbol moves above the top edge, place it just below the bottom edge to start again.
            if cy < -30:
                quiz_canvas.coords(item["id"], random.randint(min_x, max_x), canvas_h + 25)

            # If a symbol leaves the left edge, bring it back from the right edge.
            elif cx < min_x:
                quiz_canvas.coords(item["id"], max_x, cy)

            # If a symbol leaves the right edge, bring it back from the left edge.
            elif cx > max_x:
                quiz_canvas.coords(item["id"], min_x, cy)

    # Reapply the layer order so the moving symbols stay behind the screen content.
    arrange_canvas_layers()

    # Schedule this function to run again after 28 milliseconds; this creates the repeating animation.
    background_motion_timer = root.after(28, update_background_motion)


# Display a GIF by changing the label's image to the next frame at the correct time.
def animate_gif(label, frames, frame_index=0):
    global gif_frame_timer

    # There is nothing to animate if the GIF could not be loaded, so safely stop here.
    if not frames:
        return

    # Get the current frame image and the time it should remain visible.
    picture, duration = frames[frame_index]
    label.config(image=picture)

    # Keep a reference to the image. Without this, Python may remove it and the label may go blank.
    label.image = picture

    # Move to the next frame and return to frame zero when the end of the GIF is reached.
    next_index = (frame_index + 1) % len(frames)

    # Use after() to show the next frame later without freezing the rest of the application.
    gif_frame_timer = root.after(max(duration, 30), lambda: animate_gif(label, frames, next_index))


# Stop running visual effects when changing screens, so old animations do not continue in the background.
def stop_effects():
    global gif_frame_timer, score_counter_timer

    # Only cancel the GIF timer if one is currently active.
    if gif_frame_timer is not None:
        root.after_cancel(gif_frame_timer)
        gif_frame_timer = None

    # Stop the score animation too, if it is still running.
    if score_counter_timer is not None:
        root.after_cancel(score_counter_timer)
        score_counter_timer = None

    # Clear the animation labels so the previous screen's effects are no longer visible.
    sparkles_label.config(image="", text="")
    confetti_label.config(image="", text="")


# Create each screen as a separate frame. Only one of these frames is shown at a time.
welcome_screen = tk.Frame(quiz_canvas, bg=BLUSH_BG)
level_screen = tk.Frame(quiz_canvas, bg=BLUSH_BG)
quiz_screen = tk.Frame(quiz_canvas, bg=BLUSH_BG)
results_screen = tk.Frame(quiz_canvas, bg=BLUSH_BG)

# Store the canvas window IDs so each screen can be moved, shown, or hidden later.
screen_windows = {
    welcome_screen: quiz_canvas.create_window(0, 0, window=welcome_screen, anchor="center"),
    level_screen: quiz_canvas.create_window(0, 0, window=level_screen, anchor="center"),
    quiz_screen: quiz_canvas.create_window(0, 0, window=quiz_screen, anchor="center"),
    results_screen: quiz_canvas.create_window(0, 0, window=results_screen, anchor="center"),
}

# Remember which screen is currently active so resizing keeps the correct screen visible.
active_screen = welcome_screen


# Reposition the screens and redraw the background whenever the main window changes size.
def handle_resize(_event=None):
    canvas_w = max(root.winfo_width(), 200)
    canvas_h = max(root.winfo_height(), 200)

    draw_notebook_background()

    # Go through every screen and its canvas ID.
    for frame_box, window_id in screen_windows.items():
        # Place each screen in the centre of the canvas.
        quiz_canvas.coords(window_id, canvas_w // 2, canvas_h // 2)

        # Show the active screen and hide the other screens without deleting them.
        quiz_canvas.itemconfigure(window_id, state="normal" if frame_box is active_screen else "hidden")

    arrange_canvas_layers()


# Run the resize function whenever Tkinter reports that the window's size or layout has changed.
root.bind("<Configure>", handle_resize)


# Switch to a selected screen and stop effects belonging to the screen being left.
def show_screen(frame_box):
    global active_screen

    # Prevent animations from an earlier screen from continuing after the screen changes.
    stop_effects()

    # Save the selected frame as the screen that should currently be visible.
    active_screen = frame_box
    handle_resize()
    quiz_canvas.tag_raise(screen_windows[frame_box])


# Return a random whole number within the selected difficulty range.
def generate_number(low, high):
    return random.randint(low, high)


# Randomly choose either addition or subtraction for a new question.
def choose_operation():
    return random.choice(["+", "-"])


# Open the screen where the user chooses a difficulty level.
def show_level_menu():
    show_screen(level_screen)


# Start a fresh quiz using the number range chosen by the user.
def start_quiz(level_name, low, high):
    # These values are shared with other functions, so declare them global before changing them.
    global score, streak, question_number, attempts, minimum_value, maximum_value, difficulty_level

    # Reset the score and all progress from any previous quiz.
    score = 0
    streak = 0
    question_number = 0
    attempts = 0

    # Save the selected difficulty name and number range for question generation.
    difficulty_level = level_name
    minimum_value = low
    maximum_value = high

    show_next_question()


# Update the ten progress markers to show completed, current, and upcoming questions.
def update_progress_bar(current_question):
    # Check each marker's position in the row of ten progress markers.
    for index, pill in enumerate(progress_pills):
        # Mark questions before the current one as completed.
        if index < current_question - 1:
            pill.config(bg=SUCCESS_FG)

        # Highlight the marker for the question currently being answered.
        elif index == current_question - 1:
            pill.config(bg=ROSE_DARK)

        # Keep markers for questions that have not started in their normal colour.
        else:
            pill.config(bg=CARD_BG)


# Update the four labels that display the numbers and operation in the equation.
def set_equation_display(num_a, op_symbol, num_b):
    first_num_label.config(text=f"{num_a}")
    operator_label.config(text=f"{op_symbol}")
    second_num_label.config(text=f"{num_b}")
    equation_tail_label.config(text="=  ?")


# Prepare and display the next question, or show the results after question ten.
def show_next_question():
    global correct_answer, question_number, attempts, answer_locked, hint_used
    global first_number, second_number, current_operation

    # The quiz contains ten questions. Once all ten have been completed, move to the results screen.
    if question_number == 10:
        show_results()
        return

    # Clear effects from the previous question before displaying the next one.
    stop_effects()

    # Give the user two fresh attempts for this question.
    attempts = 0

    # Allow the hint to be used again for the new question.
    hint_used = False

    # Unlock answer checking for the new question.
    answer_locked = False

    # Generate two new numbers using the range selected on the difficulty screen.
    first_number = generate_number(minimum_value, maximum_value)
    second_number = generate_number(minimum_value, maximum_value)

    # Randomly choose whether this question uses addition or subtraction.
    current_operation = choose_operation()

    # Calculate the correct answer using the operation selected for this question.
    correct_answer = (first_number + second_number) if current_operation == "+" else (first_number - second_number)

    # Increase the question number because a new question is now being displayed.
    question_number += 1

    # Make the quiz screen visible before updating its question details.
    show_screen(quiz_screen)

    # Update the progress markers to match the new question number.
    update_progress_bar(question_number)

    question_label.config(text=f"Question {question_number} / 10")
    score_label.config(text=f"Score: {score}")
    streak_badge.config(text=f"✦ Streak: {streak}")
    level_badge.config(text=f"{difficulty_level.upper()} LEVEL")
    lives_label.config(text="♥ ♥", fg=ROSE_DARK)
    set_equation_display(first_number, current_operation, second_number)

    # Make the hint available again and restore its original button text.
    hint_button.config(state="normal", text="💡 Hint")
    entry_wrapper.config(highlightbackground=INK_OUTLINE, bg=CARD_BG)
    answer_entry.config(bg=CARD_BG)
    answer_entry.delete(0, tk.END)

    # Show the normal instruction message and place the cursor in the answer box.
    feedback_banner.config(text="Enter your answer and press Enter", bg=CARD_BG, fg=INK_MUTED)
    answer_entry.focus_set()


# Give the user one helpful clue without directly entering the answer for them.
def show_hint():
    global hint_used

    # Do not allow another hint or a hint after the question has already been answered.
    if hint_used or answer_locked:
        return

    # Remember that the hint has been used so it cannot be used a second time.
    hint_used = True
    hint_button.config(state="disabled", text="💡 Hint Used")

    # Give an addition specific tip when the current question uses addition.
    if current_operation == "+":
        tip_text = f"Tip: Add the tens first, then units around {round(correct_answer, -1) if abs(correct_answer) >= 10 else correct_answer}."

    # For subtraction, remind the user to find the difference and pay attention to the sign.
    else:
        tip_text = f"Tip: Find the difference between {first_number} and {second_number} (watch the sign)."

    feedback_banner.config(text=tip_text, bg=CARD_ALT, fg=LAV_DARK)


# Read the user's answer, check it, and update the score or attempt count.
def check_answer():
    global score, streak, attempts, answer_locked

    # Ignore submissions if the answer is already locked or the user is not on the quiz screen.
    if answer_locked or active_screen is not quiz_screen:
        return

    # Read the entry box and remove extra spaces from the beginning and end.
    raw_input = answer_entry.get().strip()

    # Convert the typed text into a whole number; handle letters or other invalid input safely.
    try:
        # int() changes number text, such as '12', into an integer that can be compared with the answer.
        user_guess = int(raw_input)

    # ValueError happens if the text cannot be converted into a whole number.
    except ValueError:
        entry_wrapper.config(highlightbackground=ERROR_FG)
        feedback_banner.config(text="Please enter a valid whole number.", bg=ERROR_BG, fg=ERROR_FG)
        return

    # Compare the user's number with the correct answer.
    if user_guess == correct_answer:
        # Lock the question so repeated clicks cannot award points more than once.
        answer_locked = True

        # Award 10 points for a correct first attempt, or 5 points if the second attempt is correct.
        earned_points = 10 if attempts == 0 else 5

        # Add the points earned for this question to the overall score.
        score += earned_points

        # Increase the streak because the user answered this question correctly.
        streak += 1

        # Change the answer box border and background to green to show a correct answer.
        entry_wrapper.config(highlightbackground=SUCCESS_FG, bg=SUCCESS_BG)
        answer_entry.config(bg=SUCCESS_BG)
        score_label.config(text=f"Score: {score}")
        streak_badge.config(text=f"✦ Streak: {streak}")

        # Update the feedback message to tell the user how many points they earned.
        feedback_banner.config(
            text=f"Correct! +{earned_points} points earned.",
            bg=SUCCESS_BG,
            fg=SUCCESS_FG,
        )

        # Play the sparkle GIF if it loaded successfully.
        if sparkles_frames:
            animate_gif(sparkles_label, sparkles_frames)

        # Use text symbols as a simple alternative if the sparkle GIF is unavailable.
        else:
            sparkles_label.config(text="✦  ✦  ✦", font=(FONT_DISPLAY, 16, "bold"), fg=ROSE_DARK)

        # Wait 1.35 seconds before automatically moving to the next question.
        root.after(1350, show_next_question)

    else:
        # Increase the failed attempt count because the submitted answer was incorrect.
        attempts += 1

        # After the first wrong answer, allow the user one final attempt.
        if attempts == 1:
            # Show one remaining heart to represent the final attempt.
            lives_label.config(text="♥ ♡", fg=ERROR_FG)
            entry_wrapper.config(highlightbackground=ERROR_FG)

            feedback_banner.config(
                text="Not quite! one try remaining.",
                bg=ERROR_BG,
                fg=ERROR_FG,
            )

            # Clear the incorrect answer so the user can type a new one.
            answer_entry.delete(0, tk.END)
            answer_entry.focus_set()

        # If the second attempt is also wrong, the user has used both available tries.
        else:
            # Reset the correct answer streak after two incorrect attempts.
            streak = 0
            streak_badge.config(text="✦ Streak: 0")

            # Lock the question so no more answers can be submitted for it.
            answer_locked = True

            # Show that no attempts remain by displaying empty hearts.
            lives_label.config(text="♡ ♡", fg=INK_MUTED)
            entry_wrapper.config(highlightbackground=ERROR_FG, bg=ERROR_BG)
            answer_entry.config(bg=ERROR_BG)

            # Tell the user the correct answer after both attempts have been used.
            feedback_banner.config(
                text=f"Out of tries :( the answer was {correct_answer}.",
                bg=ERROR_BG,
                fg=ERROR_FG,
            )

            # Wait briefly so the user can read the feedback before the next question appears.
            root.after(1650, show_next_question)


# Count up to the final score gradually instead of displaying it all at once.
def animate_score_counter(target_score, current_score=0):
    global score_counter_timer

    # Display the current value of the animated score counter.
    final_score_label.config(text=f"{current_score}")

    # Keep counting while the displayed score is lower than the final score.
    if current_score < target_score:
        # Increase by a larger step for bigger scores, while always increasing by at least one.
        step = max(1, (target_score - current_score) // 6)

        # Make sure the next value never goes beyond the target score.
        next_val = min(target_score, current_score + step)

        # Schedule the next counter update so the number rises smoothly without freezing the window.
        score_counter_timer = root.after(30, lambda: animate_score_counter(target_score, next_val))


# Choose a grade and message based on the final score, then display the results screen.
def show_results():
    show_screen(results_screen)

    # Match the score to a grade. Higher scores receive the stronger grade and message.
    if score >= 90:
        grade, message, badge_bg, badge_fg = "A+", "Outstanding! Sharp mental maths.", SUCCESS_BG, SUCCESS_FG
    elif score >= 80:
        grade, message, badge_bg, badge_fg = "A", "Great job! Very strong accuracy.", SUCCESS_BG, SUCCESS_FG
    elif score >= 70:
        grade, message, badge_bg, badge_fg = "B", "Good work! Keep building speed.", CARD_ALT, LAV_DARK
    elif score >= 60:
        grade, message, badge_bg, badge_fg = "C", "Solid effort! Regular practice helps.", CARD_ALT, LAV_DARK
    elif score >= 50:
        grade, message, badge_bg, badge_fg = "D", "Fair start! Ready for another round?", BOW_GOLD, GOLD_DARK
    else:
        grade, message, badge_bg, badge_fg = "F", "Keep practising, try another round!", ERROR_BG, ERROR_FG

    # Start the animated score at zero and count up to the score earned in the quiz.
    animate_score_counter(score, 0)

    # Display the grade using the background and text colours chosen for that grade.
    grade_badge.config(text=f"GRADE  {grade}", bg=badge_bg, fg=badge_fg)
    result_message.config(text=message)

    # Play the confetti animation when the GIF is available.
    if confetti_frames:
        animate_gif(confetti_label, confetti_frames)

    # If the GIF is missing, display a simple text message instead.
    else:
        confetti_label.config(
            text="✦  QUIZ COMPLETE  ✦",
            font=(FONT_DISPLAY, 15, "bold"),
            fg=ROSE_DARK,
        )


# Return to the difficulty screen so the user can start another quiz.
def play_again():
    show_level_menu()


# Build the welcome screen by adding its headings, images, information, and start button.
tk.Label(
    welcome_screen,
    text="Arithmetic Practice",
    font=(FONT_UI, 13, "bold"),
    bg=BLUSH_BG,
    fg=LAV_DARK,
).pack()

tk.Label(
    welcome_screen,
    text="Maths Quiz",
    font=(FONT_DISPLAY, 54, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

tk.Label(
    welcome_screen,
    text="Addition and subtraction practice with instant feedback",
    font=(FONT_UI, 14),
    bg=BLUSH_BG,
    fg=INK_MUTED,
).pack(pady=(4, 18))

# Place the welcome screen content inside a bordered card to keep it grouped together.
welcome_card = create_card(welcome_screen, padx=72, pady=40, border_px=4)
welcome_card.pack()

# Use a separate frame to keep the two welcome images aligned in one row.
img_row = tk.Frame(welcome_card, bg=CARD_BG)
img_row.pack(pady=(0, 16))

# Only display an image if it was loaded successfully.
if books_img:
    tk.Label(img_row, image=books_img, bg=CARD_BG).grid(row=0, column=0, padx=28)

if calculator_img:
    tk.Label(img_row, image=calculator_img, bg=CARD_BG).grid(row=0, column=1, padx=28)

tk.Label(
    welcome_card,
    text="Ready to Begin?",
    font=(FONT_DISPLAY, 25, "bold"),
    bg=CARD_BG,
    fg=INK_OUTLINE,
).pack(pady=(2, 14))

# Group the quiz information labels together beneath the welcome images.
pills_row = tk.Frame(welcome_card, bg=CARD_BG)
pills_row.pack(pady=(0, 24))

# Create one small label for each piece of information about the quiz.
for pill_text in ("10 Questions", "2 Tries Each", "100 Points"):
    tk.Label(
        pills_row,
        text=pill_text,
        font=(FONT_UI, 12, "bold"),
        bg=CARD_ALT,
        fg=INK_OUTLINE,
        padx=18,
        pady=6,
        highlightbackground=INK_OUTLINE,
        highlightthickness=2,
    ).pack(side="left", padx=8)

# Reuse the button function and connect its click action to the difficulty menu.
create_button(
    welcome_card,
    text="START QUIZ",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=30,
    pady=14,
    font_size=15,
    command=show_level_menu,
).pack()


# Build the difficulty screen, where the user chooses the size of the numbers.

# Display the stationery picture only if the image file was loaded successfully.
if stationery_img:
    tk.Label(level_screen, image=stationery_img, bg=BLUSH_BG).pack(pady=(0, 8))

tk.Label(
    level_screen,
    text="Choose Difficulty",
    font=(FONT_DISPLAY, 40, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

tk.Label(
    level_screen,
    text="Select a number range for your quiz session.",
    font=(FONT_UI, 14),
    bg=BLUSH_BG,
    fg=INK_MUTED,
).pack(pady=(4, 24))

# Use a grid frame to place the three difficulty cards next to each other.
cards_grid = tk.Frame(level_screen, bg=BLUSH_BG)
cards_grid.pack()

# Each tuple stores the card text, colours, and the settings needed to start that difficulty.
difficulty_tiers = [
    ("EASY", "Single-digit\n(1 – 9)", "Starter", ROSE_DARK, ROSE_BTN, ROSE_HOVER, ("Easy", 1, 9)),
    ("MODERATE", "Double-digit\n(10 – 99)", "Standard", LAV_DARK, LAV_BTN, LAV_HOVER, ("Moderate", 10, 99)),
    ("ADVANCED", "Four-digit\n(1000 – 9999)", "Challenge", GOLD_DARK, BOW_GOLD, "#E6BE8A", ("Advanced", 1000, 9999)),
]

# Unpack each difficulty's details and build one matching card for each level.
for col_index, (title, desc, tag, accent, btn_bg, btn_hover, tier_args) in enumerate(difficulty_tiers):
    # Give each difficulty column equal space so the cards have a consistent width.
    cards_grid.columnconfigure(col_index, weight=1, uniform="tier")

    # Create the card using the shared card function to keep its appearance consistent.
    tier_card = create_card(cards_grid, padx=28, pady=30, border_px=4)
    tier_card.grid(row=0, column=col_index, padx=12, sticky="nsew")

    tk.Label(
        tier_card,
        text=tag,
        font=(FONT_UI, 11, "bold"),
        bg=CARD_ALT,
        fg=accent,
        padx=14,
        pady=5,
        highlightbackground=INK_OUTLINE,
        highlightthickness=2,
    ).pack(pady=(0, 12))

    tk.Label(
        tier_card,
        text=title,
        font=(FONT_DISPLAY, 24, "bold"),
        bg=CARD_BG,
        fg=accent,
    ).pack(pady=(0, 10))

    tk.Label(
        tier_card,
        text=desc,
        font=(FONT_UI, 13),
        bg=CARD_BG,
        fg=INK_MUTED,
        justify="center",
    ).pack(pady=(0, 22))

    # Connect this card's button to the quiz settings stored in tier_args.
    create_button(
        tier_card,
        text="SELECT",
        bg=btn_bg,
        hover_bg=btn_hover,
        fg=INK_OUTLINE,
        width=18,
        pady=12,
        font_size=13,
        # lambda saves this card's own settings for later; *args passes the saved values into start_quiz.
        command=lambda args=tier_args: start_quiz(*args),
    ).pack()


# Add a back button so the user can return to the welcome screen.
tk.Button(
    level_screen,
    text="Back to Welcome",
    font=(FONT_UI, 11, "bold"),
    bg=BLUSH_BG,
    fg=INK_MUTED,
    activebackground=ROSE_BTN,
    activeforeground=INK_OUTLINE,
    relief="solid",
    bd=1,
    highlightthickness=0,
    padx=14,
    pady=5,
    cursor="hand2",
    command=lambda: show_screen(welcome_screen),
).pack(pady=(18, 0))

# Build the main quiz screen, including progress, the equation, answer box, and feedback.

# The top bar groups the question number, difficulty, streak, and score.
top_bar_card = create_card(quiz_screen, padx=38, pady=15, border_px=4)
top_bar_card.pack(fill="x", pady=(0, 14))

question_label = tk.Label(
    top_bar_card,
    text="Question 1 / 10",
    font=(FONT_UI, 14, "bold"),
    bg=CARD_BG,
    fg=INK_OUTLINE,
)
question_label.pack(side="left")

level_badge = tk.Label(
    top_bar_card,
    text="EASY LEVEL",
    font=(FONT_UI, 11, "bold"),
    bg=CARD_ALT,
    fg=LAV_DARK,
    padx=16,
    pady=5,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
level_badge.pack(side="left", padx=24)

streak_badge = tk.Label(
    top_bar_card,
    text="✦ Streak: 0",
    font=(FONT_UI, 11, "bold"),
    bg=CARD_ALT,
    fg=GOLD_DARK,
    padx=14,
    pady=5,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
streak_badge.pack(side="left")

score_label = tk.Label(
    top_bar_card,
    text="Score: 0",
    font=(FONT_UI, 14, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
score_label.pack(side="right")

# This frame holds ten small markers that show how far the user is through the quiz.
progress_frame = tk.Frame(quiz_screen, bg=BLUSH_BG)
progress_frame.pack(pady=(0, 14))

# Keep references to the markers so their colours can be changed for each question.
progress_pills = []

# Create ten markers because every quiz contains ten questions.
for _ in range(10):
    pill = tk.Frame(
        progress_frame,
        bg=CARD_BG,
        width=68,
        height=14,
        highlightbackground=INK_OUTLINE,
        highlightthickness=2,
    )
    pill.pack(side="left", padx=5)
    progress_pills.append(pill)

# Place the equation and hint button inside one central card.
question_card = create_card(quiz_screen, padx=72, pady=36, border_px=4)
question_card.pack(pady=(0, 12))

card_top_row = tk.Frame(question_card, bg=CARD_BG)
card_top_row.pack(fill="x", pady=(0, 12))

tk.Label(
    card_top_row,
    text="SOLVE THIS",
    font=(FONT_UI, 12, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack(side="left")

# The hint button calls show_hint when the user clicks it.
hint_button = tk.Button(
    card_top_row,
    text="💡 Hint",
    font=(FONT_UI, 11, "bold"),
    bg=CARD_ALT,
    fg=LAV_DARK,
    activebackground=BOW_GOLD,
    activeforeground=INK_OUTLINE,
    relief="solid",
    bd=2,
    padx=12,
    pady=3,
    cursor="hand2",
    command=show_hint,
)
hint_button.pack(side="left", padx=24)

lives_label = tk.Label(
    card_top_row,
    text="♥ ♥",
    font=(FONT_UI, 16, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
lives_label.pack(side="right")

# Keep the four parts of the maths equation together in one horizontal row.
equation_row = tk.Frame(question_card, bg=CARD_BG)
equation_row.pack(pady=(10, 12))
equation_row.grid_rowconfigure(0, weight=1)

# This label displays the first randomly generated number.
first_num_label = tk.Label(
    equation_row,
    text="5",
    font=EQUATION_DIGIT_FONT,
    bg=CARD_BG,
    fg=INK_OUTLINE,
    justify="center",
    pady=4,
)
first_num_label.grid(row=0, column=0, padx=(0, 18), sticky="ns")

# This label displays the addition or subtraction symbol.
operator_label = tk.Label(
    equation_row,
    text="+",
    font=EQUATION_OPERATOR_FONT,
    bg=CARD_BG,
    fg=ROSE_DARK,
    justify="center",
    pady=4,
)
operator_label.grid(row=0, column=1, padx=(0, 18), sticky="ns")

# This label displays the second randomly generated number.
second_num_label = tk.Label(
    equation_row,
    text="4",
    font=EQUATION_DIGIT_FONT,
    bg=CARD_BG,
    fg=INK_OUTLINE,
    justify="center",
    pady=4,
)
second_num_label.grid(row=0, column=2, padx=(0, 20), sticky="ns")

# This label displays the equals sign and question mark after the two numbers.
equation_tail_label = tk.Label(
    equation_row,
    text="=  ?",
    font=EQUATION_DIGIT_FONT,
    bg=CARD_BG,
    fg=INK_OUTLINE,
    justify="center",
    pady=4,
)
equation_tail_label.grid(row=0, column=3, sticky="ns")

# This label is used to display the sparkle effect after a correct answer.
sparkles_label = tk.Label(quiz_screen, bg=BLUSH_BG)
sparkles_label.pack(pady=2)

# The wrapper provides a visible border around the answer entry box.
entry_wrapper = tk.Frame(
    quiz_screen,
    bg=CARD_BG,
    highlightbackground=INK_OUTLINE,
    highlightthickness=4,
    padx=14,
    pady=6,
)
entry_wrapper.pack(pady=(4, 14))

# Let the user type their answer here; the program later reads it using answer_entry.get().
answer_entry = tk.Entry(
    entry_wrapper,
    font=(FONT_UI, 26, "bold"),
    justify="center",
    width=15,
    relief="flat",
    bg=CARD_BG,
    fg=INK_OUTLINE,
    insertbackground=ROSE_DARK,
)
answer_entry.pack()

# Submit the typed answer by calling the function that checks it.
create_button(
    quiz_screen,
    text="SUBMIT ANSWER",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=28,
    pady=12,
    font_size=14,
    command=check_answer,
).pack()

# Display instructions, hints, and messages showing whether an answer was correct.
feedback_banner = tk.Label(
    quiz_screen,
    text="Enter your answer and press Enter",
    font=(FONT_UI, 13, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
    padx=26,
    pady=10,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
feedback_banner.pack(pady=(14, 0))
tk.Button(
    quiz_screen,
    text="Back to Welcome",
    font=(FONT_UI, 11, "bold"),
    bg=BLUSH_BG,
    fg=INK_MUTED,
    activebackground=ROSE_BTN,
    activeforeground=INK_OUTLINE,
    relief="solid",
    bd=1,
    highlightthickness=0,
    padx=14,
    pady=5,
    cursor="hand2",
    command=lambda: show_screen(welcome_screen),
).pack(pady=(18, 0))

# Pressing Enter runs the same answer checking function as clicking the submit button.
root.bind("<Return>", lambda _event: check_answer())


# Build the final screen that displays the score, grade, feedback, and next actions.

# Display the trophy image only if it loaded successfully.
if trophy_img:
    tk.Label(results_screen, image=trophy_img, bg=BLUSH_BG).pack()

tk.Label(
    results_screen,
    text="Quiz Complete!",
    font=(FONT_DISPLAY, 40, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

# This label displays the confetti animation or its text alternative.
confetti_label = tk.Label(results_screen, bg=BLUSH_BG)
confetti_label.pack(pady=2)

# Group the final score and grade information inside a central results card.
result_card = create_card(results_screen, padx=72, pady=34, border_px=4)
result_card.pack(pady=6)

tk.Label(
    result_card,
    text="FINAL SCORE",
    font=(FONT_UI, 12, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack()

# Keep the score number and '/ 100' text on the same horizontal line.
score_row = tk.Frame(result_card, bg=CARD_BG)
score_row.pack(pady=(6, 12))

# This label is updated by animate_score_counter to show the counting score.
final_score_label = tk.Label(
    score_row,
    text="0",
    font=(FONT_DISPLAY, 56, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
final_score_label.pack(side="left")

tk.Label(
    score_row,
    text=" / 100",
    font=(FONT_DISPLAY, 24, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack(side="left", pady=(18, 0))

# Display the grade selected by show_results, using its matching colours.
grade_badge = tk.Label(
    result_card,
    text="GRADE  A+",
    font=(FONT_UI, 13, "bold"),
    bg=SUCCESS_BG,
    fg=SUCCESS_FG,
    padx=20,
    pady=6,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
grade_badge.pack(pady=(0, 14))

result_message = tk.Label(
    result_card,
    text="Outstanding! Sharp mental maths.",
    font=(FONT_UI, 14, "bold"),
    bg=CARD_BG,
    fg=INK_OUTLINE,
)
result_message.pack()
# Return to the welcome screen.
tk.Button(
    results_screen,
    text="Back to Welcome",
    font=(FONT_UI, 11, "bold"),
    bg=BLUSH_BG,
    fg=INK_MUTED,
    activebackground=ROSE_BTN,
    activeforeground=INK_OUTLINE,
    relief="solid",
    bd=1,
    highlightthickness=0,
    padx=14,
    pady=5,
    cursor="hand2",
    command=lambda: show_screen(welcome_screen),
).pack(pady=(6, 0))

# Keep the Play Again and Exit buttons together in one row.
result_btn_row = tk.Frame(results_screen, bg=BLUSH_BG)
result_btn_row.pack(pady=(18, 0))

# Start a new quiz by returning to the difficulty selection screen.
create_button(
    result_btn_row,
    text="PLAY AGAIN",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=18,
    pady=9,
    font_size=12,
    command=play_again,
).pack(side="left", padx=10)

# Close the application when the user clicks Exit.
create_button(
    result_btn_row,
    text="EXIT",
    bg=LAV_BTN,
    hover_bg=LAV_HOVER,
    fg=INK_OUTLINE,
    width=12,
    pady=9,
    font_size=12,
    command=root.destroy,
).pack(side="left", padx=10)
# Draw the background, show the first screen, start background movement, and run the Tkinter event loop.

# Draw the notebook background before the welcome screen appears.
draw_notebook_background()

# Add the floating maths symbols to the background.
create_floating_symbols(24)

# Display the welcome screen when the program first opens.
show_screen(welcome_screen)

# Start the repeating background animation.
update_background_motion()

# Start background music only after the interface loads.
root.after(1000, lambda: pygame.mixer.music.play(-1))

root.mainloop()