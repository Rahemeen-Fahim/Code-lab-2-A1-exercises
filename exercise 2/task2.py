
import json
import os
import random
import tkinter as tk
from tkinter import messagebox
import pygame


# Get the folder where this Python file is saved
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pygame.mixer.init()
# Load the laughing sound effect.
laugh_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "laugh.mp3"))

# Set the path for the jokes JSON file
JOKES_JSON = os.path.join(BASE_DIR, "jokes.json")

jokes = []
favourites = []
current_joke = None
joke_counter = 0

def load_jokes():
    """Read all jokes from jokes.json."""
    # Open the JSON file in read mode
    with open(JOKES_JSON, "r", encoding="utf-8") as file:
        jokes = json.load(file)

    return jokes


BG = "#1B1626"
SURFACE = "#261F36"
CARD = "#FFF9F5"
CARD_ALT = "#FDEBE3"
INK = "#1E1829"
LIGHT_INK = "#F8F3FF"
PEACH = "#F4A28C"
LAV = "#B9A7E8"
MINT_BG = "#E6F7F1"
MINT_FG = "#1E6F57"
GOLD_BG = "#FFF3D6"
GOLD_FG = "#8A5A00"
CORAL_BG = "#FFE3E3"
CORAL_FG = "#9B2C2C"


def show_frame(target):
    """Hide all frames and show only the selected one."""

    joke_frame.pack_forget()
    cart_frame.pack_forget()
    target.pack(fill="both", expand=True)

    # Refresh the cart whenever it is opened
    if target == cart_frame:
        refresh_cart()

def update_fav_button():
    """Update the favourite button and cart count."""

    if current_joke and current_joke in favourites:
        fav_btn.config(text="♥ Favourited", bg=GOLD_BG, fg=GOLD_FG)
    else:
        fav_btn.config(text="♡ Add Favourite", bg=SURFACE, fg=LIGHT_INK)

    open_cart_btn.config(text=f"Favourite Cart ({len(favourites)})")


def tell_joke():
    """Pick a random joke and show its setup."""

    global current_joke, joke_counter

    if not jokes:
        return

    # Avoid showing the same joke twice in a row
    pool = [j for j in jokes if j != current_joke] if len(jokes) > 1 else jokes
    current_joke = random.choice(pool)
    joke_counter += 1

    badge_label.config(text=f"JOKE #{joke_counter:02d}")
    setup_label.config(text=current_joke["setup"], fg=INK)
    punchline_label.config(text='Click "Show Punchline" to see the answer.', fg="#7A6C91")
    punchline_box.config(bg=CARD_ALT, highlightbackground=LAV)
    punchline_btn.config(state="normal")
    next_btn.config(state="normal")

    update_fav_button()


def show_punchline():
    """Show the punchline below the setup."""

    if not current_joke:
        return

    punchline_label.config(text=current_joke["punchline"], fg=INK)
    punchline_box.config(bg=MINT_BG, highlightbackground=MINT_FG)
    punchline_btn.config(state="disabled")

    # Play the laughing sound when the punchline is revealed.
    laugh_sound.play()


def toggle_favourite():
    """Add or remove the current joke from favourites."""

    if not current_joke:
        return

    if current_joke in favourites:
        favourites.remove(current_joke)
    else:
        favourites.append(current_joke)

    update_fav_button()


def refresh_cart():
    """Reload the listbox inside the Favourite Cart frame."""

    cart_listbox.delete(0, tk.END)

    # Display each saved joke in the listbox
    for i, item in enumerate(favourites, start=1):
        cart_listbox.insert(tk.END, f"{i}. {item['setup']}")

    cart_count_label.config(text=f"Saved Jokes: {len(favourites)}")
    cart_preview_setup.config(text="Select a joke from the list to view it.")
    cart_preview_punch.config(text="")


def on_select_fav(event=None):
    """Display the selected favourite joke."""

    sel = cart_listbox.curselection()

    if sel:
        item = favourites[sel[0]]
        cart_preview_setup.config(text=item["setup"])
        cart_preview_punch.config(text=item["punchline"])


def remove_fav():
    """Remove the selected joke from favourites."""

    sel = cart_listbox.curselection()

    if not sel:
        messagebox.showinfo("Select Joke", "Please pick a joke from the list first!")
        return

    favourites.pop(sel[0])

    update_fav_button()
    refresh_cart()

root = tk.Tk()
root.title("Alexa Tell Me a Joke")

icon = tk.PhotoImage(file=os.path.join(BASE_DIR, "app.png"))
root.iconphoto(True, icon)

root.geometry("860x600")
root.minsize(700, 500)
root.config(bg=BG)

joke_frame = tk.Frame(root, bg=BG, padx=36, pady=24)

top_bar = tk.Frame(joke_frame, bg=BG)
top_bar.pack(fill="x", pady=(0, 14))

tk.Label(
    top_bar,
    text="Alexa's Joke Telling Studio",
    font=("Georgia", 26, "bold"),
    bg=BG,
    fg=LIGHT_INK,
).pack(side="left")

right_bar = tk.Frame(top_bar, bg=BG)
right_bar.pack(side="right")

badge_label = tk.Label(
    right_bar,
    text="READY",
    font=("Segoe UI", 10, "bold"),
    bg=SURFACE,
    fg=PEACH,
    padx=12,
    pady=6,
    highlightbackground=PEACH,
    highlightthickness=1,
)
badge_label.pack(side="left", padx=(0, 10))

open_cart_btn = tk.Button(
    right_bar,
    text="Favourite Cart (0)",
    font=("Segoe UI", 10, "bold"),
    bg=LAV,
    fg=INK,
    relief="solid",
    bd=2,
    padx=14,
    pady=6,
    cursor="hand2",
    command=lambda: show_frame(cart_frame),
)
open_cart_btn.pack(side="left")


# Setup card
setup_box = tk.Frame(
    joke_frame,
    bg=CARD,
    padx=26,
    pady=20,
    highlightbackground=INK,
    highlightthickness=3,
)
setup_box.pack(fill="both", expand=True, pady=(0, 12))

tk.Label(
    setup_box,
    text="SETUP",
    font=("Segoe UI", 10, "bold"),
    bg=CARD,
    fg="#8C5A4B",
).pack(anchor="w")

setup_label = tk.Label(
    setup_box,
    text='Click "Alexa tell me a Joke" to start!',
    font=("Georgia", 20, "bold"),
    bg=CARD,
    fg=INK,
    wraplength=700,
    justify="left",
    anchor="w",
)
setup_label.pack(fill="both", expand=True, pady=(8, 0))


# Punchline card
punchline_box = tk.Frame(
    joke_frame,
    bg=CARD_ALT,
    padx=26,
    pady=18,
    highlightbackground=LAV,
    highlightthickness=3,
)
punchline_box.pack(fill="both", expand=True)

tk.Label(
    punchline_box,
    text="PUNCHLINE",
    font=("Segoe UI", 10, "bold"),
    bg=CARD_ALT,
    fg="#5D498C",
).pack(anchor="w")

punchline_label = tk.Label(
    punchline_box,
    text="Waiting for punchline...",
    font=("Georgia", 17, "italic"),
    bg=CARD_ALT,
    fg="#7A6C91",
    wraplength=700,
    justify="left",
    anchor="w",
)
punchline_label.pack(fill="both", expand=True, pady=(8, 0))


# Buttons row
btns = tk.Frame(joke_frame, bg=BG)
btns.pack(fill="x", pady=(16, 0))

tk.Button(
    btns,
    text="Alexa tell me a Joke",
    font=("Segoe UI", 11, "bold"),
    bg=PEACH,
    fg=INK,
    relief="solid",
    bd=2,
    padx=14,
    pady=10,
    cursor="hand2",
    command=tell_joke,
).pack(side="left", padx=(0, 8))

punchline_btn = tk.Button(
    btns,
    text="Show Punchline",
    font=("Segoe UI", 11, "bold"),
    bg=LAV,
    fg=INK,
    relief="solid",
    bd=2,
    padx=14,
    pady=10,
    cursor="hand2",
    state="disabled",
    command=show_punchline,
)
punchline_btn.pack(side="left", padx=(0, 8))

next_btn = tk.Button(
    btns,
    text="Next Joke",
    font=("Segoe UI", 11, "bold"),
    bg=SURFACE,
    fg=LIGHT_INK,
    relief="solid",
    bd=2,
    padx=14,
    pady=10,
    cursor="hand2",
    state="disabled",
    command=tell_joke,
)
next_btn.pack(side="left", padx=(0, 8))

fav_btn = tk.Button(
    btns,
    text="♡ Add Favourite",
    font=("Segoe UI", 11, "bold"),
    bg=SURFACE,
    fg=LIGHT_INK,
    relief="solid",
    bd=2,
    padx=14,
    pady=10,
    cursor="hand2",
    command=toggle_favourite,
)
fav_btn.pack(side="left")

tk.Button(
    btns,
    text="Quit",
    font=("Segoe UI", 11, "bold"),
    bg=CORAL_BG,
    fg=CORAL_FG,
    relief="solid",
    bd=2,
    padx=14,
    pady=10,
    cursor="hand2",
    command=root.destroy,
).pack(side="right")

cart_frame = tk.Frame(root, bg=BG, padx=36, pady=24)

cart_top = tk.Frame(cart_frame, bg=BG)
cart_top.pack(fill="x", pady=(0, 12))

tk.Label(
    cart_top,
    text="FAVOURITE CART",
    font=("Georgia", 26, "bold"),
    bg=BG,
    fg=LIGHT_INK,
).pack(side="left")

cart_count_label = tk.Label(
    cart_top,
    text="Saved Jokes: 0",
    font=("Segoe UI", 11, "bold"),
    bg=SURFACE,
    fg=PEACH,
    padx=12,
    pady=6,
)
cart_count_label.pack(side="right")

cart_listbox = tk.Listbox(
    cart_frame,
    font=("Segoe UI", 12),
    bg=CARD,
    fg=INK,
    selectbackground=PEACH,
    selectforeground=INK,
    height=7,
)
cart_listbox.pack(fill="x", pady=(0, 12))
cart_listbox.bind("<<ListboxSelect>>", on_select_fav)

cart_preview = tk.Frame(
    cart_frame,
    bg=CARD_ALT,
    padx=20,
    pady=14,
    highlightbackground=LAV,
    highlightthickness=2,
)
cart_preview.pack(fill="x", pady=(0, 14))

cart_preview_setup = tk.Label(
    cart_preview,
    text="Select a joke from the list to view it.",
    font=("Georgia", 15, "bold"),
    bg=CARD_ALT,
    fg=INK,
    wraplength=720,
    justify="left",
    anchor="w",
)
cart_preview_setup.pack(fill="x")

cart_preview_punch = tk.Label(
    cart_preview,
    text="",
    font=("Segoe UI", 13, "italic"),
    bg=CARD_ALT,
    fg="#5D498C",
    wraplength=720,
    justify="left",
    anchor="w",
)
cart_preview_punch.pack(fill="x", pady=(6, 0))

cart_btns = tk.Frame(cart_frame, bg=BG)
cart_btns.pack(fill="x")

tk.Button(
    cart_btns,
    text="Remove Selected",
    font=("Segoe UI", 11, "bold"),
    bg=CORAL_BG,
    fg=CORAL_FG,
    relief="solid",
    bd=2,
    padx=14,
    pady=9,
    cursor="hand2",
    command=remove_fav,
).pack(side="left", padx=(0, 10))

tk.Button(
    cart_btns,
    text="← Back to Jokes",
    font=("Segoe UI", 11, "bold"),
    bg=LAV,
    fg=INK,
    relief="solid",
    bd=2,
    padx=14,
    pady=9,
    cursor="hand2",
    command=lambda: show_frame(joke_frame),
).pack(side="left")

# Load the jokes from jokes.json
try:
    jokes = load_jokes()
except FileNotFoundError:
    messagebox.showerror("Missing File", "Please put jokes.json beside this Python file.")
    root.destroy()
    raise SystemExit

# Show the main joke screen
show_frame(joke_frame)

root.mainloop()
