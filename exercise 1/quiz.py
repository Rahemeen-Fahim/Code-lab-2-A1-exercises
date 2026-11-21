import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import math
from pathlib import Path

root = tk.Tk()
root.title("Maths Quiz")
root.geometry("1220x880")
root.minsize(1020, 740)
root.config(bg="#F6D5DC")

BLUSH_BG = "#F6D5DC"         # Signature dusty rose backdrop
NOTEBOOK_LINE = "#EBBCC7"    # Subtle horizontal notebook rule
MARGIN_LINE = "#DF9BAE"      # Left sketchbook margin rule
CARD_BG = "#FFF8FA"          # Soft cream-pink paper card
CARD_ALT = "#FCECF0"         # Secondary pill / badge surface
INK_OUTLINE = "#3A2E39"      # Sketchbook dark plum-charcoal outline
INK_MUTED = "#72596B"        # Secondary text
ROSE_BTN = "#E99CB3"         # Pastel rose button
ROSE_HOVER = "#DC849E"
ROSE_DARK = "#9E3E5E"
LAV_BTN = "#D7C5EC"          # Pastel lavender button
LAV_HOVER = "#C3ACE0"
LAV_DARK = "#644B82"
BOW_GOLD = "#F2CFA5"         # Warm ribbon/parchment accent
GOLD_DARK = "#8E6234"
SUCCESS_FG = "#2E7D5B"
SUCCESS_BG = "#E3F5EC"
ERROR_FG = "#B53852"
ERROR_BG = "#FDE4EA"

FONT_DISPLAY = "Georgia"
FONT_UI = "Segoe UI"
EQUATION_DIGIT_FONT = (FONT_UI, 48, "bold")
EQUATION_OPERATOR_FONT = (FONT_UI, 44, "bold")

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

gif_frame_timer = None
stage_loop_timer = None
score_counter_timer = None
card_pulse_timer = None
animation_tick = 0

sparkles_frames = []
confetti_frames = []
floating_doodles = []
burst_particles = []

ASSET_FOLDER = Path(__file__).resolve().parent


def load_picture(filename, width, height):
    try:
        picture = Image.open(ASSET_FOLDER / filename).convert("RGBA")
        picture.thumbnail((width, height), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(picture)
    except Exception:
        return None


def load_gif(filename, width, height):
    try:
        gif = Image.open(ASSET_FOLDER / filename)
        frames = []
        for frame in ImageSequence.Iterator(gif):
            rgba = frame.convert("RGBA")
            rgba.thumbnail((width, height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(rgba)
            duration = frame.info.get("duration", 95)
            frames.append((photo, duration))
        return frames
    except Exception:
        return []


calculator_img = load_picture("calculator.png", 145, 145)
books_img = load_picture("books.png", 140, 140)
trophy_img = load_picture("trophy.png", 136, 136)
stationary_img = load_picture("stationary.png", 116, 116)

sparkles_frames = load_gif("sparkles.gif", 160, 95)
confetti_frames = load_gif("confetti.gif", 250, 125)


def make_sketch_button(parent, text, bg, hover_bg, fg=INK_OUTLINE, width=24, pady=12, font_size=13, command=None):
    btn = tk.Button(
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
    btn.bind("<Enter>", lambda _event: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda _event: btn.config(bg=bg))
    return btn


def make_sketch_card(parent, padx=48, pady=34, bg=CARD_BG, border_px=4):
    return tk.Frame(
        parent,
        bg=bg,
        padx=padx,
        pady=pady,
        highlightbackground=INK_OUTLINE,
        highlightcolor=INK_OUTLINE,
        highlightthickness=border_px,
    )


stage_canvas = tk.Canvas(root, bg=BLUSH_BG, highlightthickness=0, bd=0)
stage_canvas.pack(fill="both", expand=True)


def sync_canvas_layers():
    has_lines = bool(stage_canvas.find_withtag("lines"))
    has_doodle = bool(stage_canvas.find_withtag("doodle"))
    has_burst = bool(stage_canvas.find_withtag("burst"))
    has_decor = bool(stage_canvas.find_withtag("decor"))

    if has_lines:
        stage_canvas.tag_lower("lines")
    if has_doodle and has_lines:
        stage_canvas.tag_raise("doodle", "lines")
    if has_burst and has_doodle:
        stage_canvas.tag_raise("burst", "doodle")
    elif has_burst and has_lines:
        stage_canvas.tag_raise("burst", "lines")

    if has_decor and has_burst:
        stage_canvas.tag_raise("decor", "burst")
    elif has_decor and has_doodle:
        stage_canvas.tag_raise("decor", "doodle")
    elif has_decor and has_lines:
        stage_canvas.tag_raise("decor", "lines")

    for window_id in screen_windows.values():
        stage_canvas.tag_raise(window_id)


def draw_notebook_and_corners(_event=None):
    stage_canvas.delete("decor")
    stage_canvas.delete("lines")
    canvas_w = max(root.winfo_width(), 920)
    canvas_h = max(root.winfo_height(), 700)

    # Horizontal notebook lines & left margin rule
    for y in range(44, canvas_h, 44):
        stage_canvas.create_line(0, y, canvas_w, y, fill=NOTEBOOK_LINE, width=1, tags="lines")
    stage_canvas.create_line(74, 0, 74, canvas_h, fill=MARGIN_LINE, width=3, tags="lines")

    # Top-left formula card with bold border
    stage_canvas.create_rectangle(28, 28, 246, 142, fill=INK_OUTLINE, outline="", tags="decor")
    stage_canvas.create_rectangle(22, 22, 240, 136, fill=CARD_BG, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_text(131, 48, text="x² + y² = r²", fill=INK_OUTLINE, font=(FONT_DISPLAY, 13, "bold"), tags="decor")
    stage_canvas.create_text(131, 78, text="π ≈ 3.14159", fill=ROSE_DARK, font=(FONT_DISPLAY, 12, "italic"), tags="decor")
    stage_canvas.create_text(131, 109, text="sin²α + cos²α = 1", fill=LAV_DARK, font=(FONT_DISPLAY, 11, "bold"), tags="decor")

    # Top-right calculator sketch with thick border
    calc_x = canvas_w - 190
    calc_y = 26
    stage_canvas.create_rectangle(calc_x + 7, calc_y + 7, calc_x + 161, calc_y + 211, fill=INK_OUTLINE, outline="", tags="decor")
    stage_canvas.create_rectangle(calc_x, calc_y, calc_x + 154, calc_y + 204, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_rectangle(calc_x + 18, calc_y + 18, calc_x + 136, calc_y + 56, fill="#DCE5DF", outline=INK_OUTLINE, width=2, tags="decor")
    stage_canvas.create_text(calc_x + 77, calc_y + 37, text="GIRL MATH", fill=INK_OUTLINE, font=(FONT_UI, 10, "bold"), tags="decor")
    keypad = ["7", "8", "9", "+", "4", "5", "6", "−", "1", "2", "3", "♡"]
    for idx, key in enumerate(keypad):
        col = idx % 4
        row = idx // 4
        key_x1 = calc_x + 18 + col * 30
        key_y1 = calc_y + 70 + row * 39
        key_fill = LAV_BTN if key in ("+", "−", "♡") else CARD_BG
        stage_canvas.create_rectangle(key_x1, key_y1, key_x1 + 25, key_y1 + 31, fill=key_fill, outline=INK_OUTLINE, width=2, tags="decor")
        stage_canvas.create_text(key_x1 + 12, key_y1 + 15, text=key, fill=INK_OUTLINE, font=(FONT_UI, 9, "bold"), tags="decor")

    # Bottom-left open math notebook sketch (kept clear of centered cards)
    book_x = 20
    book_y = canvas_h - 166
    stage_canvas.create_rectangle(book_x + 5, book_y + 5, book_x + 205, book_y + 144, fill=INK_OUTLINE, outline="", tags="decor")
    stage_canvas.create_rectangle(book_x, book_y, book_x + 200, book_y + 139, fill=CARD_BG, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_line(book_x + 100, book_y, book_x + 100, book_y + 139, fill=INK_OUTLINE, width=3, tags="decor")
    for line_y in range(book_y + 22, book_y + 128, 20):
        stage_canvas.create_line(book_x + 14, line_y, book_x + 88, line_y, fill=NOTEBOOK_LINE, width=1, tags="decor")
        stage_canvas.create_line(book_x + 112, line_y, book_x + 186, line_y, fill=NOTEBOOK_LINE, width=1, tags="decor")
    stage_canvas.create_text(book_x + 51, book_y + 40, text="∑ n = n(n+1)/2", fill=INK_OUTLINE, font=(FONT_DISPLAY, 9, "bold"), tags="decor")
    stage_canvas.create_text(book_x + 51, book_y + 78, text="a² + b² = c²", fill=ROSE_DARK, font=(FONT_DISPLAY, 10, "bold"), tags="decor")
    stage_canvas.create_text(book_x + 149, book_y + 48, text="♡  ✦  ♡", fill=LAV_DARK, font=(FONT_DISPLAY, 12, "bold"), tags="decor")
    stage_canvas.create_text(book_x + 149, book_y + 88, text="100% SLAY", fill=INK_OUTLINE, font=(FONT_UI, 9, "bold"), tags="decor")

    # Bottom-right ribbon bow & stacked books sketch with thick outlines
    stack_x = canvas_w - 214
    stack_y = canvas_h - 178
    for band_idx, (band_color, band_width) in enumerate([(LAV_BTN, 168), (BOW_GOLD, 152), (ROSE_BTN, 178)]):
        shelf_y = stack_y + 56 + band_idx * 29
        stage_canvas.create_rectangle(stack_x, shelf_y, stack_x + band_width, shelf_y + 27, fill=band_color, outline=INK_OUTLINE, width=3, tags="decor")
    bow_center_x = stack_x + 86
    bow_center_y = stack_y + 32
    stage_canvas.create_oval(bow_center_x - 48, bow_center_y - 19, bow_center_x - 6, bow_center_y + 19, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_oval(bow_center_x + 6, bow_center_y - 19, bow_center_x + 48, bow_center_y + 19, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_polygon(bow_center_x - 8, bow_center_y + 10, bow_center_x - 28, bow_center_y + 38, bow_center_x - 6, bow_center_y + 29, fill=ROSE_DARK, outline=INK_OUTLINE, width=2, tags="decor")
    stage_canvas.create_polygon(bow_center_x + 8, bow_center_y + 10, bow_center_x + 28, bow_center_y + 38, bow_center_x + 6, bow_center_y + 29, fill=ROSE_DARK, outline=INK_OUTLINE, width=2, tags="decor")
    stage_canvas.create_oval(bow_center_x - 12, bow_center_y - 12, bow_center_x + 12, bow_center_y + 12, fill=ROSE_DARK, outline=INK_OUTLINE, width=3, tags="decor")

    sync_canvas_layers()


DOODLE_GLYPHS = [
    ("🎀", "#C86D8B", 21),
    ("♡", "#B85577", 25),
    ("✦", "#8E6BB8", 21),
    ("+", "#8C5A72", 22),
    ("−", "#8C5A72", 22),
    ("=", "#9A6B82", 21),
    ("π", "#7E5D9E", 20),
    ("∞", "#A3637D", 21),
]


def populate_doodles(count=30):
    stage_canvas.delete("doodle")
    floating_doodles.clear()
    canvas_w = max(root.winfo_width(), 1220)
    canvas_h = max(root.winfo_height(), 880)
    min_x = 96
    max_x = max(min_x + 40, canvas_w - 96)
    for index in range(count):
        glyph, color, size = DOODLE_GLYPHS[index % len(DOODLE_GLYPHS)]
        x = random.randint(min_x, max_x)
        y = random.randint(40, canvas_h - 40)
        vy = random.uniform(-0.55, -0.2)
        base_vx = random.uniform(-0.3, 0.3)
        phase = random.uniform(0, math.pi * 2)
        item_id = stage_canvas.create_text(
            x,
            y,
            text=glyph,
            fill=color,
            font=(FONT_DISPLAY, size, "bold"),
            tags="doodle",
        )
        stage_canvas.tag_bind(
            item_id,
            "<Button-1>",
            lambda _event, doodle_id=item_id: on_doodle_click(doodle_id),
        )
        floating_doodles.append({
            "id": item_id,
            "vy": vy,
            "base_vx": base_vx,
            "phase": phase,
        })
    sync_canvas_layers()


def on_doodle_click(doodle_id):
    coords = stage_canvas.coords(doodle_id)
    if coords:
        spawn_burst(coords[0], coords[1], count=14, colors=(ROSE_DARK, LAV_DARK, BOW_GOLD))


def spawn_burst(x, y, count=30, colors=(ROSE_DARK, LAV_DARK, BOW_GOLD, SUCCESS_FG)):
    for _ in range(count):
        speed = random.uniform(2.5, 7.5)
        vx = speed * random.uniform(-1.0, 1.0)
        vy = speed * random.uniform(-1.35, 0.1)
        size = random.randint(7, 12)
        color = random.choice(colors)
        if random.random() < 0.5:
            particle_id = stage_canvas.create_oval(x, y, x + size, y + size, fill=color, outline=INK_OUTLINE, width=2, tags="burst")
        else:
            particle_id = stage_canvas.create_rectangle(x, y, x + size, y + size * 0.75, fill=color, outline=INK_OUTLINE, width=2, tags="burst")
        burst_particles.append({"id": particle_id, "vx": vx, "vy": vy, "life": random.randint(26, 44)})
    sync_canvas_layers()


def animate_stage():
    global stage_loop_timer, animation_tick
    animation_tick += 1
    canvas_w = max(root.winfo_width(), 200)
    canvas_h = max(root.winfo_height(), 200)
    min_x = 96
    max_x = max(min_x + 40, canvas_w - 96)

    for doodle in floating_doodles:
        sway = math.sin(animation_tick * 0.035 + doodle["phase"]) * 0.35
        stage_canvas.move(doodle["id"], doodle["base_vx"] + sway, doodle["vy"])
        coords = stage_canvas.coords(doodle["id"])
        if coords:
            cx, cy = coords[0], coords[1]
            if cy < -30:
                stage_canvas.coords(doodle["id"], random.randint(min_x, max_x), canvas_h + 25)
            elif cx < min_x:
                stage_canvas.coords(doodle["id"], max_x, cy)
            elif cx > max_x:
                stage_canvas.coords(doodle["id"], min_x, cy)

    active_particles = []
    for particle in burst_particles:
        particle["vy"] += 0.18
        stage_canvas.move(particle["id"], particle["vx"], particle["vy"])
        particle["life"] -= 1
        if particle["life"] > 0:
            active_particles.append(particle)
        else:
            stage_canvas.delete(particle["id"])
    burst_particles[:] = active_particles

    sync_canvas_layers()
    stage_loop_timer = root.after(28, animate_stage)


# ---------------- GIF & CARD PULSE ANIMATIONS ----------------


def animate_gif(label, frames, frame_index=0):
    global gif_frame_timer
    if not frames:
        return
    picture, duration = frames[frame_index]
    label.config(image=picture)
    label.image = picture
    next_index = (frame_index + 1) % len(frames)
    gif_frame_timer = root.after(max(duration, 30), lambda: animate_gif(label, frames, next_index))


def stop_effects():
    global gif_frame_timer, score_counter_timer
    if gif_frame_timer is not None:
        root.after_cancel(gif_frame_timer)
        gif_frame_timer = None
    if score_counter_timer is not None:
        root.after_cancel(score_counter_timer)
        score_counter_timer = None
    sparkles_label.config(image="", text="")
    confetti_label.config(image="", text="")


def pulse_problem_card(step=0):
    global card_pulse_timer
    if card_pulse_timer is not None:
        root.after_cancel(card_pulse_timer)
        card_pulse_timer = None
    pulse_colors = [CARD_ALT, BOW_GOLD, CARD_BG]
    if step < len(pulse_colors):
        question_card.config(bg=pulse_colors[step])
        card_pulse_timer = root.after(90, lambda: pulse_problem_card(step + 1))


welcome_box = tk.Frame(stage_canvas, bg=BLUSH_BG)
menu_box = tk.Frame(stage_canvas, bg=BLUSH_BG)
quiz_box = tk.Frame(stage_canvas, bg=BLUSH_BG)
result_box = tk.Frame(stage_canvas, bg=BLUSH_BG)

screen_windows = {
    welcome_box: stage_canvas.create_window(0, 0, window=welcome_box, anchor="center"),
    menu_box: stage_canvas.create_window(0, 0, window=menu_box, anchor="center"),
    quiz_box: stage_canvas.create_window(0, 0, window=quiz_box, anchor="center"),
    result_box: stage_canvas.create_window(0, 0, window=result_box, anchor="center"),
}

active_screen = welcome_box


def on_resize(_event=None):
    canvas_w = max(root.winfo_width(), 200)
    canvas_h = max(root.winfo_height(), 200)
    draw_notebook_and_corners()
    for frame_box, window_id in screen_windows.items():
        stage_canvas.coords(window_id, canvas_w // 2, canvas_h // 2)
        stage_canvas.itemconfigure(window_id, state="normal" if frame_box is active_screen else "hidden")
    sync_canvas_layers()


root.bind("<Configure>", on_resize)


def show_frame(frame_box):
    global active_screen
    stop_effects()
    active_screen = frame_box
    on_resize()
    stage_canvas.tag_raise(screen_windows[frame_box])


def randomInt(low, high):
    return random.randint(low, high)


def decideOperation():
    return random.choice(["+", "-"])


def displayMenu():
    show_frame(menu_box)


def start_quiz(level_name, low, high):
    global score, streak, question_number, attempts, minimum_value, maximum_value, difficulty_level
    score = 0
    streak = 0
    question_number = 0
    attempts = 0
    difficulty_level = level_name
    minimum_value = low
    maximum_value = high
    displayProblem()


def update_progress_bar(current_question):
    for index, pill in enumerate(progress_pills):
        if index < current_question - 1:
            pill.config(bg=SUCCESS_FG)
        elif index == current_question - 1:
            pill.config(bg=ROSE_DARK)
        else:
            pill.config(bg=CARD_BG)


def set_equation_display(num_a, op_symbol, num_b):
    first_num_label.config(text=f"{num_a}")
    operator_label.config(text=f"{op_symbol}")
    second_num_label.config(text=f"{num_b}")
    equation_tail_label.config(text="=  ?")


def displayProblem():
    global correct_answer, question_number, attempts, answer_locked, hint_used
    global first_number, second_number, current_operation

    if question_number == 10:
        displayResults()
        return

    stop_effects()
    attempts = 0
    hint_used = False
    answer_locked = False

    first_number = randomInt(minimum_value, maximum_value)
    second_number = randomInt(minimum_value, maximum_value)
    current_operation = decideOperation()

    correct_answer = (first_number + second_number) if current_operation == "+" else (first_number - second_number)
    question_number += 1

    show_frame(quiz_box)
    update_progress_bar(question_number)
    pulse_problem_card(0)

    question_label.config(text=f"Question {question_number} / 10")
    score_label.config(text=f"Score: {score}")
    streak_badge.config(text=f"✦ Streak: {streak}")
    level_badge.config(text=f"🎀 {difficulty_level.upper()} EDITION")
    lives_label.config(text="♥ ♥", fg=ROSE_DARK)
    set_equation_display(first_number, current_operation, second_number)

    hint_btn.config(state="normal", text="💡 Girl-Math Hint")
    entry_wrapper.config(highlightbackground=INK_OUTLINE, bg=CARD_BG)
    answer_entry.config(bg=CARD_BG)
    answer_entry.delete(0, tk.END)

    feedback_banner.config(text="Write your answer and press Enter ♡", bg=CARD_BG, fg=INK_MUTED)
    answer_entry.focus_set()


def show_hint():
    global hint_used
    if hint_used or answer_locked:
        return
    hint_used = True
    hint_btn.config(state="disabled", text="💡 Hint Used")
    if current_operation == "+":
        tip_text = f"Tip: Add the tens first, then units — around {round(correct_answer, -1) if abs(correct_answer) >= 10 else correct_answer}."
    else:
        tip_text = f"Tip: Count the gap between {second_number} and {first_number} (sign matters!)."
    feedback_banner.config(text=tip_text, bg=CARD_ALT, fg=LAV_DARK)


def isCorrect():
    global score, streak, attempts, answer_locked

    if answer_locked or active_screen is not quiz_box:
        return

    raw_input = answer_entry.get().strip()
    try:
        user_guess = int(raw_input)
    except ValueError:
        entry_wrapper.config(highlightbackground=ERROR_FG)
        feedback_banner.config(text="Please type a valid whole number!", bg=ERROR_BG, fg=ERROR_FG)
        return

    if user_guess == correct_answer:
        answer_locked = True
        earned_points = 10 if attempts == 0 else 5
        score += earned_points
        streak += 1

        entry_wrapper.config(highlightbackground=SUCCESS_FG, bg=SUCCESS_BG)
        answer_entry.config(bg=SUCCESS_BG)
        score_label.config(text=f"Score: {score}")
        streak_badge.config(text=f"✦ Streak: {streak}")
        feedback_banner.config(
            text=f"🎀 Iconic! +{earned_points} points earned!",
            bg=SUCCESS_BG,
            fg=SUCCESS_FG,
        )

        root.update_idletasks()
        burst_x = entry_wrapper.winfo_rootx() - root.winfo_rootx() + entry_wrapper.winfo_width() // 2
        burst_y = entry_wrapper.winfo_rooty() - root.winfo_rooty() + entry_wrapper.winfo_height() // 2
        spawn_burst(burst_x, burst_y, count=28, colors=(ROSE_DARK, LAV_DARK, BOW_GOLD, SUCCESS_FG))

        if sparkles_frames:
            animate_gif(sparkles_label, sparkles_frames)
        else:
            sparkles_label.config(text="🎀  ✦  ♡  ✦  🎀", font=(FONT_DISPLAY, 16, "bold"), fg=ROSE_DARK)

        root.after(1350, displayProblem)

    else:
        attempts += 1
        if attempts == 1:
            lives_label.config(text="♥ ♡", fg=ERROR_FG)
            entry_wrapper.config(highlightbackground=ERROR_FG)
            feedback_banner.config(
                text="Almost! One more try left ♡",
                bg=ERROR_BG,
                fg=ERROR_FG,
            )
            answer_entry.delete(0, tk.END)
            answer_entry.focus_set()
        else:
            streak = 0
            streak_badge.config(text="✦ Streak: 0")
            answer_locked = True
            lives_label.config(text="♡ ♡", fg=INK_MUTED)
            entry_wrapper.config(highlightbackground=ERROR_FG, bg=ERROR_BG)
            answer_entry.config(bg=ERROR_BG)
            feedback_banner.config(
                text=f"No tries left — answer was {correct_answer}.",
                bg=ERROR_BG,
                fg=ERROR_FG,
            )
            root.after(1650, displayProblem)


def animate_score_counter(target_score, current_score=0):
    global score_counter_timer
    final_score_label.config(text=f"{current_score}")
    if current_score < target_score:
        step = max(1, (target_score - current_score) // 6)
        next_val = min(target_score, current_score + step)
        score_counter_timer = root.after(30, lambda: animate_score_counter(target_score, next_val))


def displayResults():
    show_frame(result_box)

    if score >= 90:
        grade, message, badge_bg, badge_fg = "A+", "Iconic! Pure math genius.", SUCCESS_BG, SUCCESS_FG
    elif score >= 80:
        grade, message, badge_bg, badge_fg = "A", "Gorgeous work! Super sharp numbers.", SUCCESS_BG, SUCCESS_FG
    elif score >= 70:
        grade, message, badge_bg, badge_fg = "B", "Lovely job! You're doing great.", CARD_ALT, LAV_DARK
    elif score >= 60:
        grade, message, badge_bg, badge_fg = "C", "Sweet effort! Keep practising daily.", CARD_ALT, LAV_DARK
    elif score >= 50:
        grade, message, badge_bg, badge_fg = "D", "Cute progress! One more round?", BOW_GOLD, GOLD_DARK
    else:
        grade, message, badge_bg, badge_fg = "F", "Its okay! try again ♡", ERROR_BG, ERROR_FG

    animate_score_counter(score, 0)
    grade_badge.config(text=f"GRADE  {grade}", bg=badge_bg, fg=badge_fg)
    result_message.config(text=message)

    canvas_w = max(root.winfo_width(), 600)
    spawn_burst(canvas_w * 0.30, 170, count=32)
    spawn_burst(canvas_w * 0.70, 170, count=32)

    if confetti_frames:
        animate_gif(confetti_label, confetti_frames)
    else:
        confetti_label.config(
            text="🎀  ✦  ♡  CELEBRATION  ♡  ✦  🎀",
            font=(FONT_DISPLAY, 15, "bold"),
            fg=ROSE_DARK,
        )


def play_again():
    displayMenu()


# ---------------- WELCOME SCREEN ----------------

tk.Label(
    welcome_box,
    text="🎀 Arithmetic Calculations Edition  🎀",
    font=(FONT_UI, 13, "bold"),
    bg=BLUSH_BG,
    fg=LAV_DARK,
).pack()

tk.Label(
    welcome_box,
    text="Maths Magic",
    font=(FONT_DISPLAY, 54, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

tk.Label(
    welcome_box,
    text="Cute equations, notebook vibes & quick mental maths ♡",
    font=(FONT_UI, 14),
    bg=BLUSH_BG,
    fg=INK_MUTED,
).pack(pady=(4, 18))

welcome_card = make_sketch_card(welcome_box, padx=72, pady=40, border_px=4)
welcome_card.pack()

img_row = tk.Frame(welcome_card, bg=CARD_BG)
img_row.pack(pady=(0, 16))

if books_img:
    tk.Label(img_row, image=books_img, bg=CARD_BG).grid(row=0, column=0, padx=28)
if calculator_img:
    tk.Label(img_row, image=calculator_img, bg=CARD_BG).grid(row=0, column=1, padx=28)

tk.Label(
    welcome_card,
    text="Ready for the Quiz?",
    font=(FONT_DISPLAY, 25, "bold"),
    bg=CARD_BG,
    fg=INK_OUTLINE,
).pack(pady=(2, 14))

pills_row = tk.Frame(welcome_card, bg=CARD_BG)
pills_row.pack(pady=(0, 24))

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

make_sketch_button(
    welcome_card,
    text="START QUIZ  ♡",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=30,
    pady=14,
    font_size=15,
    command=displayMenu,
).pack()


# ---------------- LEVEL MENU SCREEN ----------------

if stationary_img:
    tk.Label(menu_box, image=stationary_img, bg=BLUSH_BG).pack(pady=(0, 8))

tk.Label(
    menu_box,
    text="Pick Your Level",
    font=(FONT_DISPLAY, 40, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

tk.Label(
    menu_box,
    text="Choose a number set for your 10-question round.",
    font=(FONT_UI, 14),
    bg=BLUSH_BG,
    fg=INK_MUTED,
).pack(pady=(4, 24))

cards_grid = tk.Frame(menu_box, bg=BLUSH_BG)
cards_grid.pack()

difficulty_tiers = [
    ("EASY", "Single-digit\n(1 – 9)", "♡ Soft Start", ROSE_DARK, ROSE_BTN, ROSE_HOVER, ("Easy", 1, 9)),
    ("MODERATE", "Double-digit\n(10 – 99)", "✦ Study Mode", LAV_DARK, LAV_BTN, LAV_HOVER, ("Moderate", 10, 99)),
    ("ADVANCED", "Four-digit\n(1000 – 9999)", "🎀 Pro Math", GOLD_DARK, BOW_GOLD, "#E6BE8A", ("Advanced", 1000, 9999)),
]

for col_index, (title, desc, tag, accent, btn_bg, btn_hover, tier_args) in enumerate(difficulty_tiers):
    cards_grid.columnconfigure(col_index, weight=1, uniform="tier")
    tier_card = make_sketch_card(cards_grid, padx=28, pady=30, border_px=4)
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

    make_sketch_button(
        tier_card,
        text="SELECT",
        bg=btn_bg,
        hover_bg=btn_hover,
        fg=INK_OUTLINE,
        width=18,
        pady=12,
        font_size=13,
        command=lambda args=tier_args: start_quiz(*args),
    ).pack()

tk.Button(
    menu_box,
    text="← Back to Welcome",
    font=(FONT_UI, 13, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
    activebackground=BLUSH_BG,
    activeforeground=ROSE_DARK,
    relief="flat",
    cursor="hand2",
    command=lambda: show_frame(welcome_box),
).pack(pady=(22, 0))


# ---------------- QUIZ SCREEN ----------------

top_bar_card = make_sketch_card(quiz_box, padx=38, pady=15, border_px=4)
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
    text="🎀 EASY EDITION",
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

progress_frame = tk.Frame(quiz_box, bg=BLUSH_BG)
progress_frame.pack(pady=(0, 14))

progress_pills = []
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

question_card = make_sketch_card(quiz_box, padx=72, pady=36, border_px=4)
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

hint_btn = tk.Button(
    card_top_row,
    text="💡 Girl-Math Hint",
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
hint_btn.pack(side="left", padx=24)

lives_label = tk.Label(
    card_top_row,
    text="♥ ♥",
    font=(FONT_UI, 16, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
lives_label.pack(side="right")

equation_row = tk.Frame(question_card, bg=CARD_BG)
equation_row.pack(pady=(10, 12))
equation_row.grid_rowconfigure(0, weight=1)

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

sparkles_label = tk.Label(quiz_box, bg=BLUSH_BG)
sparkles_label.pack(pady=2)

entry_wrapper = tk.Frame(
    quiz_box,
    bg=CARD_BG,
    highlightbackground=INK_OUTLINE,
    highlightthickness=4,
    padx=14,
    pady=6,
)
entry_wrapper.pack(pady=(4, 14))

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

make_sketch_button(
    quiz_box,
    text="SUBMIT ANSWER",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=28,
    pady=12,
    font_size=14,
    command=isCorrect,
).pack()

feedback_banner = tk.Label(
    quiz_box,
    text="Write your answer and press Enter ♡",
    font=(FONT_UI, 13, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
    padx=26,
    pady=10,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
feedback_banner.pack(pady=(14, 0))

root.bind("<Return>", lambda _event: isCorrect())


# ---------------- RESULTS SCREEN ----------------

if trophy_img:
    tk.Label(result_box, image=trophy_img, bg=BLUSH_BG).pack()

tk.Label(
    result_box,
    text="Quiz Complete!",
    font=(FONT_DISPLAY, 40, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

confetti_label = tk.Label(result_box, bg=BLUSH_BG)
confetti_label.pack(pady=2)

result_card = make_sketch_card(result_box, padx=72, pady=34, border_px=4)
result_card.pack(pady=10)

tk.Label(
    result_card,
    text="FINAL SCORE",
    font=(FONT_UI, 12, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack()

score_row = tk.Frame(result_card, bg=CARD_BG)
score_row.pack(pady=(4, 12))

final_score_label = tk.Label(
    score_row,
    text="0",
    font=(FONT_DISPLAY, 52, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
final_score_label.pack(side="left")

tk.Label(
    score_row,
    text=" / 100",
    font=(FONT_UI, 22, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack(side="left", pady=(20, 0))

grade_badge = tk.Label(
    result_card,
    text="GRADE  A+",
    font=(FONT_UI, 14, "bold"),
    bg=SUCCESS_BG,
    fg=SUCCESS_FG,
    padx=20,
    pady=7,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
grade_badge.pack(pady=(0, 12))

result_message = tk.Label(
    result_card,
    text="Iconic work!",
    font=(FONT_UI, 13),
    bg=CARD_BG,
    fg=INK_OUTLINE,
)
result_message.pack()

action_row = tk.Frame(result_box, bg=BLUSH_BG)
action_row.pack(pady=(18, 0))

make_sketch_button(
    action_row,
    text="PLAY AGAIN",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=22,
    pady=12,
    font_size=14,
    command=play_again,
).pack(side="left", padx=12)

make_sketch_button(
    action_row,
    text="EXIT",
    bg=LAV_BTN,
    hover_bg=LAV_HOVER,
    fg=INK_OUTLINE,
    width=17,
    pady=12,
    font_size=14,
    command=root.destroy,
).pack(side="left", padx=12)

populate_doodles()
draw_notebook_and_corners()
animate_stage()
show_frame(welcome_box)
root.mainloop()