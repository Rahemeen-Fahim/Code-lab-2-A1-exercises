import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import random
import math
from pathlib import Path

root = tk.Tk()
root.title("Maths Quiz")
root.geometry("1080x800")
root.minsize(940, 700)
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

score = 0
streak = 0
question_number = 0
attempts = 0
hint_used = False
minimum = 1
maximum = 9
difficulty = ""
number1 = 0
number2 = 0
operation = "+"
answer = 0
answer_locked = False

gif_job = None
anim_job = None
score_anim_job = None
pulse_job = None
tick = 0

sparkles_frames = []
confetti_frames = []
doodle_items = []
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


calculator_img = load_picture("calculator.jpg", 125, 125)
books_img = load_picture("books.jpg", 120, 120)
trophy_img = load_picture("trophy.jpg", 120, 120)
stationary_img = load_picture("stationary.jpg", 100, 100)

sparkles_frames = load_gif("sparkles.gif", 145, 85)
confetti_frames = load_gif("confetti.gif", 230, 115)


def make_sketch_button(parent, text, bg, hover_bg, fg=INK_OUTLINE, width=22, pady=11, font_size=13, command=None):
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
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def make_sketch_card(parent, padx=38, pady=28, bg=CARD_BG, border_px=4):
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


def draw_notebook_and_corners(event=None):
    stage_canvas.delete("decor")
    w = max(root.winfo_width(), 920)
    h = max(root.winfo_height(), 700)

    # Horizontal notebook lines & left margin rule
    for y in range(44, h, 44):
        stage_canvas.create_line(0, y, w, y, fill=NOTEBOOK_LINE, width=1, tags="decor")
    stage_canvas.create_line(74, 0, 74, h, fill=MARGIN_LINE, width=3, tags="decor")

    # Top-left formula card with bold border
    stage_canvas.create_rectangle(28, 28, 246, 142, fill=INK_OUTLINE, outline="", tags="decor")
    stage_canvas.create_rectangle(22, 22, 240, 136, fill=CARD_BG, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_text(131, 48, text="x² + y² = r²", fill=INK_OUTLINE, font=(FONT_DISPLAY, 13, "bold"), tags="decor")
    stage_canvas.create_text(131, 78, text="π ≈ 3.14159", fill=ROSE_DARK, font=(FONT_DISPLAY, 12, "italic"), tags="decor")
    stage_canvas.create_text(131, 109, text="sin²α + cos²α = 1", fill=LAV_DARK, font=(FONT_DISPLAY, 11, "bold"), tags="decor")

    # Top-right calculator sketch with thick border
    rx = w - 190
    ry = 26
    stage_canvas.create_rectangle(rx + 7, ry + 7, rx + 161, ry + 211, fill=INK_OUTLINE, outline="", tags="decor")
    stage_canvas.create_rectangle(rx, ry, rx + 154, ry + 204, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_rectangle(rx + 18, ry + 18, rx + 136, ry + 56, fill="#DCE5DF", outline=INK_OUTLINE, width=2, tags="decor")
    stage_canvas.create_text(rx + 77, ry + 37, text="GIRL MATH", fill=INK_OUTLINE, font=(FONT_UI, 10, "bold"), tags="decor")
    keypad = ["7", "8", "9", "+", "4", "5", "6", "−", "1", "2", "3", "♡"]
    for idx, key in enumerate(keypad):
        col = idx % 4
        row = idx // 4
        kx1 = rx + 18 + col * 30
        ky1 = ry + 70 + row * 39
        key_fill = LAV_BTN if key in ("+", "−", "♡") else CARD_BG
        stage_canvas.create_rectangle(kx1, ky1, kx1 + 25, ky1 + 31, fill=key_fill, outline=INK_OUTLINE, width=2, tags="decor")
        stage_canvas.create_text(kx1 + 12, ky1 + 15, text=key, fill=INK_OUTLINE, font=(FONT_UI, 9, "bold"), tags="decor")

    # Bottom-left open math notebook sketch with thick border
    bx = 24
    by = h - 188
    stage_canvas.create_rectangle(bx + 6, by + 6, bx + 230, by + 164, fill=INK_OUTLINE, outline="", tags="decor")
    stage_canvas.create_rectangle(bx, by, bx + 224, by + 158, fill=CARD_BG, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_line(bx + 112, by, bx + 112, by + 158, fill=INK_OUTLINE, width=3, tags="decor")
    for ly in range(by + 24, by + 144, 22):
        stage_canvas.create_line(bx + 16, ly, bx + 100, ly, fill=NOTEBOOK_LINE, width=1, tags="decor")
        stage_canvas.create_line(bx + 124, ly, bx + 208, ly, fill=NOTEBOOK_LINE, width=1, tags="decor")
    stage_canvas.create_text(bx + 58, by + 46, text="∑ n = n(n+1)/2", fill=INK_OUTLINE, font=(FONT_DISPLAY, 10, "bold"), tags="decor")
    stage_canvas.create_text(bx + 58, by + 88, text="a² + b² = c²", fill=ROSE_DARK, font=(FONT_DISPLAY, 11, "bold"), tags="decor")
    stage_canvas.create_text(bx + 166, by + 56, text="♡  ✦  ♡", fill=LAV_DARK, font=(FONT_DISPLAY, 13, "bold"), tags="decor")
    stage_canvas.create_text(bx + 166, by + 100, text="100% SLAY", fill=INK_OUTLINE, font=(FONT_UI, 10, "bold"), tags="decor")

    # Bottom-right ribbon bow & stacked books sketch with thick outlines
    px = w - 214
    py = h - 178
    for b_idx, (b_col, b_w) in enumerate([(LAV_BTN, 168), (BOW_GOLD, 152), (ROSE_BTN, 178)]):
        sy = py + 56 + b_idx * 29
        stage_canvas.create_rectangle(px, sy, px + b_w, sy + 27, fill=b_col, outline=INK_OUTLINE, width=3, tags="decor")
    cx_bow = px + 86
    cy_bow = py + 32
    stage_canvas.create_oval(cx_bow - 48, cy_bow - 19, cx_bow - 6, cy_bow + 19, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_oval(cx_bow + 6, cy_bow - 19, cx_bow + 48, cy_bow + 19, fill=ROSE_BTN, outline=INK_OUTLINE, width=3, tags="decor")
    stage_canvas.create_polygon(cx_bow - 8, cy_bow + 10, cx_bow - 28, cy_bow + 38, cx_bow - 6, cy_bow + 29, fill=ROSE_DARK, outline=INK_OUTLINE, width=2, tags="decor")
    stage_canvas.create_polygon(cx_bow + 8, cy_bow + 10, cx_bow + 28, cy_bow + 38, cx_bow + 6, cy_bow + 29, fill=ROSE_DARK, outline=INK_OUTLINE, width=2, tags="decor")
    stage_canvas.create_oval(cx_bow - 12, cy_bow - 12, cx_bow + 12, cy_bow + 12, fill=ROSE_DARK, outline=INK_OUTLINE, width=3, tags="decor")

    stage_canvas.tag_lower("decor")


DOODLES = [
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
    doodle_items.clear()
    w = max(root.winfo_width(), 1080)
    h = max(root.winfo_height(), 800)
    for i in range(count):
        glyph, color, size = DOODLES[i % len(DOODLES)]
        x = random.randint(90, w - 90)
        y = random.randint(40, h - 40)
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
            lambda e, cid=item_id: on_doodle_click(cid),
        )
        doodle_items.append({
            "id": item_id,
            "vy": vy,
            "base_vx": base_vx,
            "phase": phase,
        })


def on_doodle_click(item_id):
    coords = stage_canvas.coords(item_id)
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
            pid = stage_canvas.create_oval(x, y, x + size, y + size, fill=color, outline=INK_OUTLINE, width=2, tags="burst")
        else:
            pid = stage_canvas.create_rectangle(x, y, x + size, y + size * 0.75, fill=color, outline=INK_OUTLINE, width=2, tags="burst")
        burst_particles.append({"id": pid, "vx": vx, "vy": vy, "life": random.randint(26, 44)})


def animate_stage():
    global anim_job, tick
    tick += 1
    w = max(root.winfo_width(), 200)
    h = max(root.winfo_height(), 200)

    for d in doodle_items:
        sway = math.sin(tick * 0.035 + d["phase"]) * 0.35
        stage_canvas.move(d["id"], d["base_vx"] + sway, d["vy"])
        coords = stage_canvas.coords(d["id"])
        if coords:
            cx, cy = coords[0], coords[1]
            if cy < -30:
                stage_canvas.coords(d["id"], random.randint(90, max(130, w - 90)), h + 25)
            elif cx < 78:
                stage_canvas.coords(d["id"], max(130, w - 90), cy)
            elif cx > w - 78:
                stage_canvas.coords(d["id"], 90, cy)

    kept = []
    for p in burst_particles:
        p["vy"] += 0.18
        stage_canvas.move(p["id"], p["vx"], p["vy"])
        p["life"] -= 1
        if p["life"] > 0:
            kept.append(p)
        else:
            stage_canvas.delete(p["id"])
    burst_particles[:] = kept

    stage_canvas.tag_lower("doodle")
    stage_canvas.tag_lower("burst")
    stage_canvas.tag_lower("decor")

    anim_job = root.after(28, animate_stage)


# ---------------- GIF & CARD PULSE ANIMATIONS ----------------


def animate_gif(label, frames, index=0):
    global gif_job
    if not frames:
        return
    picture, duration = frames[index]
    label.config(image=picture)
    label.image = picture
    next_index = (index + 1) % len(frames)
    gif_job = root.after(max(duration, 30), lambda: animate_gif(label, frames, next_index))


def stop_effects():
    global gif_job, score_anim_job
    if gif_job is not None:
        root.after_cancel(gif_job)
        gif_job = None
    if score_anim_job is not None:
        root.after_cancel(score_anim_job)
        score_anim_job = None
    sparkles_label.config(image="", text="")
    confetti_label.config(image="", text="")


def pulse_problem_card(step=0):
    global pulse_job
    if pulse_job is not None:
        root.after_cancel(pulse_job)
        pulse_job = None
    sequence = [CARD_ALT, BOW_GOLD, CARD_BG]
    if step < len(sequence):
        question_card.config(bg=sequence[step])
        pulse_job = root.after(90, lambda: pulse_problem_card(step + 1))

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


def on_resize(event=None):
    w = max(root.winfo_width(), 200)
    h = max(root.winfo_height(), 200)
    draw_notebook_and_corners()
    for box, win_id in screen_windows.items():
        stage_canvas.coords(win_id, w // 2, h // 2)
        stage_canvas.itemconfigure(win_id, state="normal" if box is active_screen else "hidden")


root.bind("<Configure>", on_resize)


def show_frame(frame_box):
    global active_screen
    stop_effects()
    active_screen = frame_box
    on_resize()
    stage_canvas.tag_raise(screen_windows[frame_box])


def randomInt(minimum, maximum):
    return random.randint(minimum, maximum)


def decideOperation():
    return random.choice(["+", "-"])


def displayMenu():
    show_frame(menu_box)


def startQuiz(level, low, high):
    global score, streak, question_number, attempts, minimum, maximum, difficulty
    score = 0
    streak = 0
    question_number = 0
    attempts = 0
    difficulty = level
    minimum = low
    maximum = high
    displayProblem()


def update_progress_bar(current_q):
    for i, pill in enumerate(progress_pills):
        if i < current_q - 1:
            pill.config(bg=SUCCESS_FG)
        elif i == current_q - 1:
            pill.config(bg=ROSE_DARK)
        else:
            pill.config(bg=CARD_BG)


def set_equation_display(n1, op, n2):
    num1_label.config(text=f"{n1}")
    op_label.config(text=f"{op}")
    num2_label.config(text=f"{n2}")
    eq_tail_label.config(text="=  ?")


def displayProblem():
    global answer, question_number, attempts, answer_locked, hint_used
    global number1, number2, operation

    if question_number == 10:
        displayResults()
        return

    stop_effects()
    attempts = 0
    hint_used = False
    answer_locked = False

    number1 = randomInt(minimum, maximum)
    number2 = randomInt(minimum, maximum)
    operation = decideOperation()

    answer = (number1 + number2) if operation == "+" else (number1 - number2)
    question_number += 1

    show_frame(quiz_box)
    update_progress_bar(question_number)
    pulse_problem_card(0)

    question_label.config(text=f"Question {question_number} / 10")
    score_label.config(text=f"Score: {score}")
    streak_badge.config(text=f"✦ Streak: {streak}")
    level_badge.config(text=f"🎀 {difficulty.upper()} EDITION")
    lives_label.config(text="♥ ♥", fg=ROSE_DARK)
    set_equation_display(number1, operation, number2)

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
    if operation == "+":
        tip = f"Tip: Add the tens first, then units — around {round(answer, -1) if abs(answer) >= 10 else answer}."
    else:
        tip = f"Tip: Count the gap between {number2} and {number1} (sign matters!)."
    feedback_banner.config(text=tip, bg=CARD_ALT, fg=LAV_DARK)


def isCorrect():
    global score, streak, attempts, answer_locked

    if answer_locked or active_screen is not quiz_box:
        return

    user_answer = answer_entry.get().strip()
    try:
        user_answer = int(user_answer)
    except ValueError:
        entry_wrapper.config(highlightbackground=ERROR_FG)
        feedback_banner.config(text="Please type a valid whole number!", bg=ERROR_BG, fg=ERROR_FG)
        return

    if user_answer == answer:
        answer_locked = True
        points = 10 if attempts == 0 else 5
        score += points
        streak += 1

        entry_wrapper.config(highlightbackground=SUCCESS_FG, bg=SUCCESS_BG)
        answer_entry.config(bg=SUCCESS_BG)
        score_label.config(text=f"Score: {score}")
        streak_badge.config(text=f"✦ Streak: {streak}")
        feedback_banner.config(
            text=f"🎀 Iconic! +{points} points earned!",
            bg=SUCCESS_BG,
            fg=SUCCESS_FG,
        )

        root.update_idletasks()
        cx = entry_wrapper.winfo_rootx() - root.winfo_rootx() + entry_wrapper.winfo_width() // 2
        cy = entry_wrapper.winfo_rooty() - root.winfo_rooty() + entry_wrapper.winfo_height() // 2
        spawn_burst(cx, cy, count=28, colors=(ROSE_DARK, LAV_DARK, BOW_GOLD, SUCCESS_FG))

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
                text=f"No tries left — answer was {answer}.",
                bg=ERROR_BG,
                fg=ERROR_FG,
            )
            root.after(1650, displayProblem)


def animate_score_counter(target, current=0):
    global score_anim_job
    final_score_label.config(text=f"{current}")
    if current < target:
        step = max(1, (target - current) // 6)
        next_val = min(target, current + step)
        score_anim_job = root.after(30, lambda: animate_score_counter(target, next_val))


def displayResults():
    show_frame(result_box)

    if score >= 90:
        grade, message, badge_bg, badge_fg = "A+", "Iconic! Pure girl-math genius.", SUCCESS_BG, SUCCESS_FG
    elif score >= 80:
        grade, message, badge_bg, badge_fg = "A", "Gorgeous work! Super sharp numbers.", SUCCESS_BG, SUCCESS_FG
    elif score >= 70:
        grade, message, badge_bg, badge_fg = "B", "Lovely job! You're doing great.", CARD_ALT, LAV_DARK
    elif score >= 60:
        grade, message, badge_bg, badge_fg = "C", "Sweet effort! Keep practising daily.", CARD_ALT, LAV_DARK
    elif score >= 50:
        grade, message, badge_bg, badge_fg = "D", "Cute progress! One more round?", BOW_GOLD, GOLD_DARK
    else:
        grade, message, badge_bg, badge_fg = "F", "Shake it off & try again ♡", ERROR_BG, ERROR_FG

    animate_score_counter(score, 0)
    grade_badge.config(text=f"GRADE  {grade}", bg=badge_bg, fg=badge_fg)
    result_message.config(text=message)

    w = max(root.winfo_width(), 600)
    spawn_burst(w * 0.30, 170, count=32)
    spawn_burst(w * 0.70, 170, count=32)

    if confetti_frames:
        animate_gif(confetti_label, confetti_frames)
    else:
        confetti_label.config(
            text="🎀  ✦  ♡  CELEBRATION  ♡  ✦  🎀",
            font=(FONT_DISPLAY, 15, "bold"),
            fg=ROSE_DARK,
        )


def playAgain():
    displayMenu()

tk.Label(
    welcome_box,
    text="🎀 Arithmetic Calculations Edition  🎀",
    font=(FONT_UI, 12, "bold"),
    bg=BLUSH_BG,
    fg=LAV_DARK,
).pack()

tk.Label(
    welcome_box,
    text="Maths Magic",
    font=(FONT_DISPLAY, 48, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

tk.Label(
    welcome_box,
    text="Cute equations, notebook vibes & quick mental maths ♡",
    font=(FONT_UI, 13),
    bg=BLUSH_BG,
    fg=INK_MUTED,
).pack(pady=(4, 16))

welcome_card = make_sketch_card(welcome_box, padx=50, pady=30, border_px=4)
welcome_card.pack()

img_row = tk.Frame(welcome_card, bg=CARD_BG)
img_row.pack(pady=(0, 14))

if books_img:
    tk.Label(img_row, image=books_img, bg=CARD_BG).grid(row=0, column=0, padx=22)
if calculator_img:
    tk.Label(img_row, image=calculator_img, bg=CARD_BG).grid(row=0, column=1, padx=22)

tk.Label(
    welcome_card,
    text="Ready for the Quiz?",
    font=(FONT_DISPLAY, 22, "bold"),
    bg=CARD_BG,
    fg=INK_OUTLINE,
).pack(pady=(2, 12))

pills_row = tk.Frame(welcome_card, bg=CARD_BG)
pills_row.pack(pady=(0, 20))

for pill_text in ("10 Questions", "2 Tries Each", "100 Points"):
    tk.Label(
        pills_row,
        text=pill_text,
        font=(FONT_UI, 11, "bold"),
        bg=CARD_ALT,
        fg=INK_OUTLINE,
        padx=14,
        pady=5,
        highlightbackground=INK_OUTLINE,
        highlightthickness=2,
    ).pack(side="left", padx=6)

make_sketch_button(
    welcome_card,
    text="START QUIZ  ♡",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=26,
    pady=12,
    font_size=14,
    command=displayMenu,
).pack()

if stationary_img:
    tk.Label(menu_box, image=stationary_img, bg=BLUSH_BG).pack(pady=(0, 6))

tk.Label(
    menu_box,
    text="Pick Your Level",
    font=(FONT_DISPLAY, 36, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

tk.Label(
    menu_box,
    text="Choose a number set for your 10-question round.",
    font=(FONT_UI, 13),
    bg=BLUSH_BG,
    fg=INK_MUTED,
).pack(pady=(4, 22))

cards_grid = tk.Frame(menu_box, bg=BLUSH_BG)
cards_grid.pack()

tiers = [
    ("EASY", "Single-digit\n(1 – 9)", "♡ Soft Start", ROSE_DARK, ROSE_BTN, ROSE_HOVER, ("Easy", 1, 9)),
    ("MODERATE", "Double-digit\n(10 – 99)", "✦ Study Mode", LAV_DARK, LAV_BTN, LAV_HOVER, ("Moderate", 10, 99)),
    ("ADVANCED", "Four-digit\n(1000 – 9999)", "🎀 Pro Math", GOLD_DARK, BOW_GOLD, "#E6BE8A", ("Advanced", 1000, 9999)),
]

for col, (title, desc, tag, accent, btn_bg, btn_hover, args) in enumerate(tiers):
    cards_grid.columnconfigure(col, weight=1, uniform="tier")
    card = make_sketch_card(cards_grid, padx=30, pady=26, border_px=4)
    card.grid(row=0, column=col, padx=14, sticky="nsew")

    tk.Label(
        card,
        text=tag,
        font=(FONT_UI, 10, "bold"),
        bg=CARD_ALT,
        fg=accent,
        padx=12,
        pady=4,
        highlightbackground=INK_OUTLINE,
        highlightthickness=2,
    ).pack(pady=(0, 10))

    tk.Label(
        card,
        text=title,
        font=(FONT_DISPLAY, 21, "bold"),
        bg=CARD_BG,
        fg=accent,
    ).pack(pady=(0, 8))

    tk.Label(
        card,
        text=desc,
        font=(FONT_UI, 12),
        bg=CARD_BG,
        fg=INK_MUTED,
        justify="center",
    ).pack(pady=(0, 18))

    make_sketch_button(
        card,
        text="SELECT",
        bg=btn_bg,
        hover_bg=btn_hover,
        fg=INK_OUTLINE,
        width=18,
        pady=10,
        font_size=12,
        command=lambda a=args: startQuiz(*a),
    ).pack()

tk.Button(
    menu_box,
    text="← Back to Welcome",
    font=(FONT_UI, 12, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
    activebackground=BLUSH_BG,
    activeforeground=ROSE_DARK,
    relief="flat",
    cursor="hand2",
    command=lambda: show_frame(welcome_box),
).pack(pady=(20, 0))

top_bar_card = make_sketch_card(quiz_box, padx=30, pady=13, border_px=4)
top_bar_card.pack(fill="x", pady=(0, 12))

question_label = tk.Label(
    top_bar_card,
    text="Question 1 / 10",
    font=(FONT_UI, 13, "bold"),
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
    padx=14,
    pady=4,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
level_badge.pack(side="left", padx=22)

streak_badge = tk.Label(
    top_bar_card,
    text="✦ Streak: 0",
    font=(FONT_UI, 11, "bold"),
    bg=CARD_ALT,
    fg=GOLD_DARK,
    padx=12,
    pady=4,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
streak_badge.pack(side="left")

score_label = tk.Label(
    top_bar_card,
    text="Score: 0",
    font=(FONT_UI, 13, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
score_label.pack(side="right")

progress_frame = tk.Frame(quiz_box, bg=BLUSH_BG)
progress_frame.pack(pady=(0, 12))

progress_pills = []
for _ in range(10):
    pill = tk.Frame(
        progress_frame,
        bg=CARD_BG,
        width=58,
        height=12,
        highlightbackground=INK_OUTLINE,
        highlightthickness=2,
    )
    pill.pack(side="left", padx=4)
    progress_pills.append(pill)

question_card = make_sketch_card(quiz_box, padx=52, pady=26, border_px=4)
question_card.pack(pady=(0, 10))

card_top_row = tk.Frame(question_card, bg=CARD_BG)
card_top_row.pack(fill="x", pady=(0, 8))

tk.Label(
    card_top_row,
    text="SOLVE THIS",
    font=(FONT_UI, 11, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack(side="left")

hint_btn = tk.Button(
    card_top_row,
    text="💡 Girl-Math Hint",
    font=(FONT_UI, 10, "bold"),
    bg=CARD_ALT,
    fg=LAV_DARK,
    activebackground=BOW_GOLD,
    activeforeground=INK_OUTLINE,
    relief="solid",
    bd=2,
    padx=10,
    pady=2,
    cursor="hand2",
    command=show_hint,
)
hint_btn.pack(side="left", padx=20)

lives_label = tk.Label(
    card_top_row,
    text="♥ ♥",
    font=(FONT_UI, 15, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
lives_label.pack(side="right")

# Equation row: first number large, second number smaller
eq_row = tk.Frame(question_card, bg=CARD_BG)
eq_row.pack(pady=(8, 10))

num1_label = tk.Label(
    eq_row,
    text="5",
    font=(FONT_DISPLAY, 48, "bold"),
    bg=CARD_BG,
    fg=INK_OUTLINE,
)
num1_label.pack(side="left", padx=(0, 14))

op_label = tk.Label(
    eq_row,
    text="+",
    font=(FONT_DISPLAY, 40, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
op_label.pack(side="left", padx=(0, 14))

num2_label = tk.Label(
    eq_row,
    text="4",
    font=(FONT_DISPLAY, 28, "bold"),
    bg=CARD_BG,
    fg=LAV_DARK,
)
num2_label.pack(side="left", padx=(0, 16))

eq_tail_label = tk.Label(
    eq_row,
    text="=  ?",
    font=(FONT_DISPLAY, 46, "bold"),
    bg=CARD_BG,
    fg=INK_OUTLINE,
)
eq_tail_label.pack(side="left")

sparkles_label = tk.Label(quiz_box, bg=BLUSH_BG)
sparkles_label.pack(pady=2)

entry_wrapper = tk.Frame(
    quiz_box,
    bg=CARD_BG,
    highlightbackground=INK_OUTLINE,
    highlightthickness=4,
    padx=10,
    pady=5,
)
entry_wrapper.pack(pady=(2, 12))

answer_entry = tk.Entry(
    entry_wrapper,
    font=(FONT_UI, 24, "bold"),
    justify="center",
    width=13,
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
    width=24,
    pady=11,
    font_size=13,
    command=isCorrect,
).pack()

feedback_banner = tk.Label(
    quiz_box,
    text="Write your answer and press Enter ♡",
    font=(FONT_UI, 12, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
    padx=22,
    pady=8,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
feedback_banner.pack(pady=(12, 0))

root.bind("<Return>", lambda event: isCorrect())

if trophy_img:
    tk.Label(result_box, image=trophy_img, bg=BLUSH_BG).pack()

tk.Label(
    result_box,
    text="Quiz Complete!",
    font=(FONT_DISPLAY, 36, "bold"),
    bg=BLUSH_BG,
    fg=INK_OUTLINE,
).pack()

confetti_label = tk.Label(result_box, bg=BLUSH_BG)
confetti_label.pack(pady=2)

result_card = make_sketch_card(result_box, padx=54, pady=26, border_px=4)
result_card.pack(pady=8)

tk.Label(
    result_card,
    text="FINAL SCORE",
    font=(FONT_UI, 11, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack()

score_row = tk.Frame(result_card, bg=CARD_BG)
score_row.pack(pady=(2, 10))

final_score_label = tk.Label(
    score_row,
    text="0",
    font=(FONT_DISPLAY, 48, "bold"),
    bg=CARD_BG,
    fg=ROSE_DARK,
)
final_score_label.pack(side="left")

tk.Label(
    score_row,
    text=" / 100",
    font=(FONT_UI, 20, "bold"),
    bg=CARD_BG,
    fg=INK_MUTED,
).pack(side="left", pady=(18, 0))

grade_badge = tk.Label(
    result_card,
    text="GRADE  A+",
    font=(FONT_UI, 13, "bold"),
    bg=SUCCESS_BG,
    fg=SUCCESS_FG,
    padx=18,
    pady=6,
    highlightbackground=INK_OUTLINE,
    highlightthickness=2,
)
grade_badge.pack(pady=(0, 10))

result_message = tk.Label(
    result_card,
    text="Iconic work!",
    font=(FONT_UI, 12),
    bg=CARD_BG,
    fg=INK_OUTLINE,
)
result_message.pack()

action_row = tk.Frame(result_box, bg=BLUSH_BG)
action_row.pack(pady=(16, 0))

make_sketch_button(
    action_row,
    text="PLAY AGAIN",
    bg=ROSE_BTN,
    hover_bg=ROSE_HOVER,
    fg=INK_OUTLINE,
    width=20,
    pady=10,
    font_size=13,
    command=playAgain,
).pack(side="left", padx=10)

make_sketch_button(
    action_row,
    text="EXIT",
    bg=LAV_BTN,
    hover_bg=LAV_HOVER,
    fg=INK_OUTLINE,
    width=15,
    pady=10,
    font_size=13,
    command=root.destroy,
).pack(side="left", padx=10)

draw_notebook_and_corners()
populate_doodles()
animate_stage()
show_frame(welcome_box)
root.mainloop()