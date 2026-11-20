from tkinter import *
from tkinter import messagebox
import os
from datetime import datetime
import json


NAVY = "#344054"
SIDEBAR = "#293444"
PURPLE = "#64748B"
LIGHT = "#F3F5F7"
WHITE = "#FFFFFF"
GREY = "#DEE2E6"
BORDER = "#DCE1E7"
PALE_PURPLE = "#E9EDF2"
SIDE_GREY = "#D8DEE7"

RED = "#DC5555"
ORANGE = "#D97706"
GREEN = "#16845B"

FONT_TITLE = ("Arial", 24, "bold")
FONT_SUBTITLE = ("Arial", 11)
FONT_BODY = ("Arial", 11)
FONT_BUTTON = ("Arial", 10, "bold")
FONT_INPUT = ("Arial", 11)
FONT_OUTPUT = ("Consolas", 9)


main_folder = os.path.dirname(os.path.abspath(__file__))

folder = main_folder

file_name = os.path.join(folder, "studentMarks.json")

students = []
deleted_students = []

def load_students():

    students.clear()

    print("\n========== FILE CHECK ==========")
    print("Python file:", os.path.abspath(__file__))
    print("Folder:", folder)
    print("JSON path:", file_name)
    print("JSON exists:", os.path.isfile(file_name))

    print("Files in folder:", os.listdir(folder))

    if not os.path.isfile(file_name):
        print("JSON FILE NOT FOUND!")
        return

    with open(file_name, "r") as file:
        data = json.load(file)

    print("JSON keys:", data.keys())

    for student in data["students"]:
        students.append([
            student["number"],
            student["name"],
            student["cw1"],
            student["cw2"],
            student["cw3"],
            student["exam"]
        ])

    print("TOTAL STUDENTS LOADED:", len(students))
    print("================================\n")


def save_students():

    data = {"students": []}

    for student in students:
        data["students"].append({
            "number": student[0],
            "name": student[1],
            "cw1": student[2],
            "cw2": student[3],
            "cw3": student[4],
            "exam": student[5]
        })

    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)


def calculate_results(student):

    coursework = student[2] + student[3] + student[4]

    total = coursework + student[5]

    percentage = (total / 160) * 100

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

    return coursework, total, percentage, grade


def clear_page():

    output.delete("1.0", END)

    for widget in action_frame.winfo_children():
        widget.destroy()


def clear_output():

    output.delete("1.0", END)

def find_student(search):

    for student in students:

        if (student[0].lower() == search.lower()
                or student[1].lower() == search.lower()):

            return student

    return None

def get_mark(entry, maximum):

    value = entry.get().strip()

    if "/" in value:

        parts = value.split("/")

        if len(parts) != 2:
            raise ValueError

        if int(parts[1]) != maximum:
            raise ValueError

        mark = int(parts[0])

    else:

        mark = int(value)

    return mark

def get_mark_colour(mark, maximum):

    percentage = (mark / maximum) * 100

    if percentage < 50:
        return "low"

    elif percentage < 70:
        return "average"

    else:
        return "good"

def display_table(student_list):

    if len(student_list) == 0:

        output.insert(END, "No student records available.\n")

        return

    output.insert(
        END,
        "Student ID\tName\tCW1\tCW2\tCW3\tExam\tTotal\tPercentage\tGrade\n",
        "table_heading"
    )

    output.insert(END, "\n")

    for student in student_list:

        coursework, total, percentage, grade = calculate_results(student)

        output.insert(END, student[0] + "\t")

        output.insert(END, student[1][:18] + "\t")

        output.insert(
            END,
            str(student[2]) + "\t",
            get_mark_colour(student[2], 20)
        )

        output.insert(
            END,
            str(student[3]) + "\t",
            get_mark_colour(student[3], 20)
        )

        output.insert(
            END,
            str(student[4]) + "\t",
            get_mark_colour(student[4], 20)
        )

        output.insert(
            END,
            str(student[5]) + "\t",
            get_mark_colour(student[5], 100)
        )

        output.insert(
            END,
            str(total) + "\t",
            get_mark_colour(total, 160)
        )

        output.insert(
            END,
            str(round(percentage, 1)) + "%\t",
            get_mark_colour(total, 160)
        )

        output.insert(
            END,
            grade + "\n\n",
            "grade_" + grade
        )


def display_student(student):

    display_table([student])

def display_summary():

    if len(students) == 0:
        return

    total_percentage = 0
    highest_mark = 0
    lowest_mark = 160

    for student in students:

        coursework, total, percentage, grade = calculate_results(student)

        total_percentage += percentage

        if total > highest_mark:
            highest_mark = total

        if total < lowest_mark:
            lowest_mark = total

    average = total_percentage / len(students)

    output.insert(END, "\n")

    summary_frame = Frame(
        output,
        bg=LIGHT,
        padx=12,
        pady=12
    )

    output.window_create(END, window=summary_frame)

    Label(
        summary_frame,
        text="CLASS PERFORMANCE SUMMARY",
        bg=LIGHT,
        fg=NAVY,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", pady=(0, 12))

    cards_frame = Frame(summary_frame, bg=LIGHT)

    cards_frame.pack(fill=X)

    card_details = [
        ("TOTAL STUDENTS", str(len(students)), NAVY),
        ("CLASS AVERAGE", str(round(average, 1)) + "%", PURPLE),
        ("HIGHEST MARK", str(highest_mark) + "/160", GREEN),
        ("LOWEST MARK", str(lowest_mark) + "/160", RED)
    ]

    for i, detail in enumerate(card_details):

        card = Frame(
            cards_frame,
            bg=WHITE,
            padx=13,
            pady=13,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        card.grid(
            row=0,
            column=i,
            padx=5,
            sticky="nsew"
        )

        Label(
            card,
            text=detail[0],
            bg=WHITE,
            fg=GREY,
            font=("Arial", 8, "bold")
        ).pack(anchor="w")

        Label(
            card,
            text=detail[1],
            bg=WHITE,
            fg=detail[2],
            font=("Arial", 15, "bold")
        ).pack(anchor="w", pady=(7, 0))

        cards_frame.grid_columnconfigure(i, weight=1)

    output.insert(END, "\n\n")

def home():

    clear_page()

    heading.config(text="Welcome to Student Manager")

    subheading.config(
        text="Your academic records dashboard"
    )

    total_students = len(students)

    total_marks = 0
    highest_mark = 0
    lowest_mark = 160

    for student in students:

        coursework, total, percentage, grade = calculate_results(student)

        total_marks += percentage

        if total > highest_mark:
            highest_mark = total

        if total < lowest_mark:
            lowest_mark = total

    if total_students > 0:
        average = total_marks / total_students

    else:
        average = 0

    cards = Frame(output, bg=WHITE)

    output.window_create(END, window=cards)

    output.insert(END, "\n\n")

    card_details = [
        ("TOTAL STUDENTS", str(total_students)),
        ("CLASS AVERAGE", str(round(average, 2)) + "%"),
        ("HIGHEST MARK", str(highest_mark) + "/160"),
        ("LOWEST MARK", str(lowest_mark if total_students > 0 else 0) + "/160")
    ]

    for i, detail in enumerate(card_details):

        card = Frame(
            cards,
            bg=PALE_PURPLE,
            padx=16,
            pady=17,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        card.grid(row=0, column=i, padx=5, sticky="nsew")

        Label(
            card,
            text=detail[0],
            bg=PALE_PURPLE,
            fg=GREY,
            font=("Arial", 8, "bold")
        ).pack(anchor="w")

        Label(
            card,
            text=detail[1],
            bg=PALE_PURPLE,
            fg=NAVY,
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(7, 0))

        cards.grid_columnconfigure(i, weight=1)

    output.insert(END, "\n\n")

    output.insert(
        END,
        "Quick Overview\n",
        "overview_heading"
    )

    output.insert(
        END,
        "Welcome to your Student Records Manager!\n\n"
    )

    output.insert(
        END,
        "Use the navigation menu to manage academic records.\n"
    )

    output.insert(
        END,
        "• View all student information and marks.\n"
    )

    output.insert(
        END,
        "• Search for an individual student.\n"
    )

    output.insert(
        END,
        "• Compare the highest and lowest marks.\n"
    )

    output.insert(
        END,
        "• Sort students by their overall performance.\n"
    )

    output.insert(
        END,
        "• Add, update and delete student records.\n\n"
    )

    output.insert(
        END,
        "Select an option from the left menu to get started."
    )

def view_all():

    clear_page()

    heading.config(text="All Students")

    subheading.config(
        text="Complete list of student records and   results"
    )

    if len(students) == 0:

        output.insert(
            END,
            "No student records available yet.\n\n"
        )

        output.insert(
            END,
            "Use Add Student to create your first record."
        )

        return

    output.insert(
        END,
        "ALL STUDENT RECORDS\n\n",
        "section_heading"
    )

    display_table(students)

    display_summary()

def view_individual():

    clear_page()

    heading.config(text="Find Student")

    subheading.config(
        text="Search using a student number or name"
    )

    output.insert(
        END,
        "Enter a student number or name in the Quick Search box."
    )


def search_student():

    search = search_entry.get().strip()

    clear_page()

    heading.config(text="Search Results")

    subheading.config(
        text="Results matching your search"
    )

    if search == "":

        output.insert(
            END,
            "Please enter a student number or name."
        )

        return

    student = find_student(search)

    if student is not None:

        output.insert(
            END,
            "STUDENT FOUND\n\n",
            "section_heading"
        )

        display_student(student)

    else:

        output.insert(
            END,
            "No student found."
        )


def highest_student():

    clear_page()

    heading.config(text="Highest Mark")

    subheading.config(
        text="Student with the highest overall mark"
    )

    if len(students) == 0:

        output.insert(
            END,
            "No student records available."
        )

        return

    highest = students[0]

    for student in students:

        coursework, total, percentage, grade = calculate_results(student)

        highest_coursework, highest_total, highest_percentage, highest_grade = calculate_results(highest)

        if total > highest_total:
            highest = student

    output.insert(
        END,
        "STUDENT WITH HIGHEST MARK\n\n",
        "section_heading"
    )

    display_student(highest)

def lowest_student():

    clear_page()

    heading.config(text="Lowest Mark")

    subheading.config(
        text="Student with the lowest overall mark"
    )

    if len(students) == 0:

        output.insert(
            END,
            "No student records available."
        )

        return

    lowest = students[0]

    for student in students:

        coursework, total, percentage, grade = calculate_results(student)

        lowest_coursework, lowest_total, lowest_percentage, lowest_grade = calculate_results(lowest)

        if total < lowest_total:
            lowest = student

    output.insert(
        END,
        "STUDENT WITH LOWEST MARK\n\n",
        "section_heading"
    )

    display_student(lowest)


def sort_students():

    clear_page()

    heading.config(text="Sort Records")

    subheading.config(
        text="Arrange student records by overall marks"
    )

    Label(
        action_frame,
        text="SORT BY OVERALL MARK",
        bg=LIGHT,
        fg=NAVY,
        font=("Arial", 10, "bold")
    ).pack(side=LEFT, padx=(0, 12))

    Button(
        action_frame,
        text="↑  Ascending Order",
        bg=NAVY,
        fg=WHITE,
        font=FONT_BUTTON,
        padx=16,
        pady=9,
        relief="flat",
        cursor="hand2",
        command=lambda: show_sorted("descending")
    ).pack(side=LEFT, padx=6)

    Button(
            action_frame,
            text="↓  Descending Order",              
            bg=PURPLE,
            fg=WHITE,
            font=FONT_BUTTON,
            padx=16,
            pady=9,
            relief="flat",
            cursor="hand2",
            command=lambda: show_sorted("ascending")
        ).pack(side=LEFT, padx=6)

    output.insert(
        END,
        "Choose an order above to arrange the student records."
    )


def show_sorted(order):

    clear_output()

    if len(students) == 0:

        output.insert(
            END,
            "No student records available."
        )

        return

    if order == "ascending":

        sorted_students = sorted(
            students,
            key=lambda student: calculate_results(student)[1]
        )

        output.insert(
            END,
            "STUDENTS: LOWEST TO HIGHEST\n\n",
            "section_heading"
        )

    else:

        sorted_students = sorted(
            students,
            key=lambda student: calculate_results(student)[1],
            reverse=True
        )

        output.insert(
            END,
            "STUDENTS: HIGHEST TO LOWEST\n\n",
            "section_heading"
        )

    display_table(sorted_students)

    display_summary()


def check_marks(mark1, mark2, mark3, exam):

    if not (0 <= mark1 <= 20 and 0 <= mark2 <= 20 and 0 <= mark3 <= 20):

        messagebox.showerror(
            "Error",
            "Coursework marks must be between 0 and 20."
        )

        return False

    if not (0 <= exam <= 100):

        messagebox.showerror(
            "Error",
            "Exam mark must be between 0 and 100."
        )

        return False

    return True


def create_student_form(parent, values=None):

    labels = [
        "Student Number",
        "Student Name",
        "Coursework 1",
        "Coursework 2",
        "Coursework 3",
        "Exam"
    ]

    entries = []

    for i in range(6):

        field_frame = Frame(
            parent,
            bg=WHITE
        )

        field_frame.grid(
            row=i // 2,
            column=i % 2,
            padx=12,
            pady=9,
            sticky="ew"
        )

        Label(
            field_frame,
            text=labels[i],
            bg=WHITE,
            fg=NAVY,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        entry = Entry(
            field_frame,
            font=FONT_INPUT,
            relief="solid",
            bd=1
        )

        entry.pack(fill=X, ipady=6)

        if values is not None:
            entry.insert(0, str(values[i]))

        entries.append(entry)

    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)

    return entries

def add_student():

    popup = Toplevel(root)

    popup.title("Add Student Record")
    popup.geometry("600x490")
    popup.resizable(False, False)
    popup.config(bg=LIGHT)
    popup.transient(root)
    popup.grab_set()

    Label(
        popup,
        text="＋  Add New Student",
        bg=NAVY,
        fg=WHITE,
        font=("Arial", 20, "bold"),
        padx=20,
        pady=18
    ).pack(fill=X)

    Label(
        popup,
        text="Enter the student's personal and academic details below.",
        bg=LIGHT,
        fg=GREY,
        font=FONT_BODY
    ).pack(anchor="w", padx=25, pady=(18, 8))

    form_frame = Frame(
        popup,
        bg=WHITE,
        padx=15,
        pady=15,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    form_frame.pack(fill=X, padx=22, pady=8)

    entries = create_student_form(form_frame)

    def submit_student():

        number = entries[0].get().strip()
        name = entries[1].get().strip()

        if number == "" or name == "":

            messagebox.showerror(
                "Error",
                "Student number and name are required.",
                parent=popup
            )

            return

        for student in students + deleted_students:

            if student[0] == number:

                messagebox.showerror(
                    "Error",
                    "This student number already exists.",
                    parent=popup
                )

                return

        try:

            mark1 = get_mark(entries[2], 20)
            mark2 = get_mark(entries[3], 20)
            mark3 = get_mark(entries[4], 20)
            exam = get_mark(entries[5], 100)

        except ValueError:

            messagebox.showerror(
                "Error",
                "Enter valid marks. You can use 11 or 11/20 for coursework and 68 or 68/100 for the exam.",
                parent=popup
            )

            return

        if not check_marks(mark1, mark2, mark3, exam):
            return

        new_student = [
            number,
            name,
            mark1,
            mark2,
            mark3,
            exam
        ]

        students.append(new_student)

        save_students()

        messagebox.showinfo(
            "Success",
            "Student added successfully.",
            parent=popup
        )

        popup.destroy()

        view_all()

    Button(
        popup,
        text="＋  Add Student",
        bg=PURPLE,
        fg=WHITE,
        font=FONT_BUTTON,
        relief="flat",
        padx=22,
        pady=10,
        cursor="hand2",
        command=submit_student
    ).pack(anchor="e", padx=25, pady=15)


def delete_student():

    clear_page()

    heading.config(text="Delete Student")

    subheading.config(
        text="Review the student records before deleting"
    )

    if len(students) == 0:

        output.insert(
            END,
            "No student records available to delete."
        )

        return

    Label(
        action_frame,
        text="Student Number or Name",
        bg=LIGHT,
        fg=NAVY,
        font=FONT_BODY
    ).pack(side=LEFT, padx=(0, 10))

    delete_entry = Entry(
        action_frame,
        font=FONT_INPUT,
        width=25,
        relief="solid",
        bd=1
    )

    delete_entry.pack(side=LEFT, padx=5, ipady=5)

    def remove_student():

        search = delete_entry.get().strip()

        if search == "":

            messagebox.showerror(
                "Error",
                "Please enter a student number or name."
            )

            return

        student = find_student(search)

        if student is None:

            messagebox.showerror(
                "Error",
                "Student not found."
            )

            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to temporarily delete " + student[1] + "?"
        )

        if confirm:

            deleted_students.append(student)

            students.remove(student)

            save_students()

            messagebox.showinfo(
                "Success",
                "Student deleted for this session."
            )

            delete_student()

    Button(
        action_frame,
        text="Delete Student",
        bg=RED,
        fg=WHITE,
        font=FONT_BUTTON,
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
        command=remove_student
    ).pack(side=LEFT, padx=10)

    output.insert(
        END,
        "CURRENT STUDENT RECORDS\n\n",
        "section_heading"
    )

    display_table(students)

def update_student():

    clear_page()

    heading.config(text="Update Student")

    subheading.config(
        text="Review records and search for a student to update"
    )

    if len(students) == 0:

        output.insert(
            END,
            "No student records available to update."
        )

        return

    Label(
        action_frame,
        text="Student Number or Name",
        bg=LIGHT,
        fg=NAVY,
        font=FONT_BODY
    ).pack(side=LEFT, padx=(0, 10))

    update_search = Entry(
        action_frame,
        font=FONT_INPUT,
        width=25,
        relief="solid",
        bd=1
    )

    update_search.pack(side=LEFT, padx=5, ipady=5)

    def search_for_update():

        search = update_search.get().strip()

        if search == "":

            messagebox.showerror(
                "Error",
                "Please enter a student number or name."
            )

            return

        student = find_student(search)

        if student is None:

            messagebox.showerror(
                "Error",
                "Student not found."
            )

            return

        open_update_popup(student)

    Button(
        action_frame,
        text="Find Student",
        bg=PURPLE,
        fg=WHITE,
        font=FONT_BUTTON,
        relief="flat",
        cursor="hand2",
        padx=15,
        pady=8,
        command=search_for_update
    ).pack(side=LEFT, padx=10)

    output.insert(
        END,
        "CURRENT STUDENT RECORDS\n\n",
        "section_heading"
    )

    display_table(students)

def open_update_popup(student):

    popup = Toplevel(root)

    popup.title("Update Student")
    popup.geometry("600x490")
    popup.resizable(False, False)
    popup.config(bg=LIGHT)
    popup.transient(root)
    popup.grab_set()

    Label(
        popup,
        text="✎  Update Student Details",
        bg=NAVY,
        fg=WHITE,
        font=("Arial", 20, "bold"),
        padx=20,
        pady=18
    ).pack(fill=X)

    Label(
        popup,
        text="Edit the information and save your changes.",
        bg=LIGHT,
        fg=GREY,
        font=FONT_BODY
    ).pack(anchor="w", padx=25, pady=(18, 8))

    form_frame = Frame(
        popup,
        bg=WHITE,
        padx=15,
        pady=15,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    form_frame.pack(fill=X, padx=22, pady=8)

    entries = create_student_form(form_frame, student)

    def save_update():

        number = entries[0].get().strip()
        name = entries[1].get().strip()

        if number == "" or name == "":

            messagebox.showerror(
                "Error",
                "Student number and name are required.",
                parent=popup
            )

            return

        for other_student in students + deleted_students:

            if other_student is not student and other_student[0] == number:

                messagebox.showerror(
                    "Error",
                    "This student number already exists.",
                    parent=popup
                )

                return

        try:

            mark1 = get_mark(entries[2], 20)
            mark2 = get_mark(entries[3], 20)
            mark3 = get_mark(entries[4], 20)
            exam = get_mark(entries[5], 100)

        except ValueError:

            messagebox.showerror(
                "Error",
                "Enter valid marks. You can use 11 or 11/20 for coursework and 68 or 68/100 for the exam.",
                parent=popup
            )

            return

        if not check_marks(mark1, mark2, mark3, exam):
            return

        student[0] = number
        student[1] = name
        student[2] = mark1
        student[3] = mark2
        student[4] = mark3
        student[5] = exam

        save_students()

        messagebox.showinfo(
            "Success",
            "Student updated successfully.",
            parent=popup
        )

        popup.destroy()

        view_all()

    Button(
        popup,
        text="Save Changes",
        bg=PURPLE,
        fg=WHITE,
        font=FONT_BUTTON,
        relief="flat",
        cursor="hand2",
        padx=22,
        pady=10,
        command=save_update
    ).pack(anchor="e", padx=25, pady=15)

root = Tk()

root.title("Student Manager")
root.geometry("1180x780")
root.minsize(1050, 700)
root.config(bg=LIGHT)


home_icon = PhotoImage(file=os.path.join(folder, "home.png"))
student_icon = PhotoImage(file=os.path.join(folder, "student.png"))
search_icon = PhotoImage(file=os.path.join(folder, "search.png"))
highest_icon = PhotoImage(file=os.path.join(folder, "highest.png"))
lowest_icon = PhotoImage(file=os.path.join(folder, "lowest.png"))
sort_icon = PhotoImage(file=os.path.join(folder, "sort.png"))
add_icon = PhotoImage(file=os.path.join(folder, "add.png"))
delete_icon = PhotoImage(file=os.path.join(folder, "delete.png"))
update_icon = PhotoImage(file=os.path.join(folder, "update.png"))

app_icon = PhotoImage(file=os.path.join(folder, "icon.png"))
root.iconphoto(True, app_icon)

load_students()

sidebar = Frame(
    root,
    bg=SIDEBAR,
    width=245
)

sidebar.pack(side=LEFT, fill=Y)

sidebar.pack_propagate(False)

Label(
    sidebar,
    text="STUDENT\nMANAGER",
    bg=SIDEBAR,
    fg=SIDE_GREY,
    font=("Arial", 21, "bold"),
    justify=LEFT
).pack(anchor="w", padx=20, pady=(25, 25))


def create_button(text, command, icon):

    button = Button(
        sidebar,
        text=text,
        image=icon,
        compound=LEFT,
        bg=SIDEBAR,
        fg="#E5E7EB",
        activebackground=PURPLE,
        activeforeground=WHITE,
        font=FONT_BODY,
        anchor="w",
        relief="flat",
        bd=0,
        padx=18,
        pady=10,
        command=command,
        cursor="hand2"
    )

    button.pack(fill=X, padx=12, pady=3)

    button.bind(
        "<Enter>",
        lambda event: button.config(bg=PURPLE, fg=WHITE)
    )

    button.bind(
        "<Leave>",
        lambda event: button.config(bg=SIDEBAR, fg="#E5E7EB")
    )


create_button("Home", home, home_icon)
create_button("All Students", view_all, student_icon)
create_button("Find Student", view_individual, search_icon)
create_button("Highest Mark", highest_student, highest_icon)
create_button("Lowest Mark", lowest_student, lowest_icon)

Frame(
    sidebar,
    bg="#64748B",
    height=1
).pack(
    fill=X,
    padx=20,
    pady=15
)

Label(
    sidebar,
    text="MANAGE RECORDS",
    bg=SIDEBAR,
    fg="#AEB8C7",
    font=("Arial", 9, "bold")
).pack(
    anchor="w",
    padx=20,
    pady=(0, 8)
)

create_button("Sort Records", sort_students, sort_icon)
create_button("Add Student", add_student, add_icon)
create_button("Delete Student", delete_student, delete_icon)
create_button("Update Student", update_student, update_icon)


content = Frame(
    root,
    bg=LIGHT
)

content.pack(
    side=RIGHT,
    fill=BOTH,
    expand=True,
    padx=25,
    pady=18
)


title_border = Frame(
    content,
    bg=PURPLE,
    padx=2,
    pady=2
)

title_border.pack(
    fill=X,
    pady=(0, 10)
)

title_row = Frame(
    title_border,
    bg=WHITE,
    padx=22,
    pady=15
)

title_row.pack(fill=X)

heading_area = Frame(
    title_row,
    bg=WHITE
)

heading_area.pack(
    side=LEFT,
    fill=X,
    expand=True
)

Label(
    heading_area,
    text="ACADEMIC MANAGEMENT SYSTEM",
    bg=WHITE,
    fg=PURPLE,
    font=("Arial", 9, "bold")
).pack(
    anchor="w",
    pady=(0, 6)
)

heading = Label(
    heading_area,
    text="Welcome to Student Manager",
    bg=WHITE,
    fg=NAVY,
    font=FONT_TITLE
)

heading.pack(anchor="w")

subheading = Label(
    heading_area,
    text="Your academic records dashboard",
    bg=WHITE,
    fg=GREY,
    font=FONT_SUBTITLE
)

subheading.pack(
    anchor="w",
    pady=(5, 0)
)

Frame(
    heading_area,
    bg=PURPLE,
    height=3,
    width=60
).pack(
    anchor="w",
    pady=(9, 0)
)

datetime_bar = Frame(
    content,
    bg=PALE_PURPLE,
    padx=14,
    pady=8,
    highlightbackground=BORDER,
    highlightthickness=1
)

datetime_bar.pack(
    fill=X,
    pady=(0, 10)
)

Label(
    datetime_bar,
    text="CURRENT DATE & TIME",
    bg=PALE_PURPLE,
    fg=PURPLE,
    font=("Arial", 9, "bold")
).pack(side=LEFT)

datetime_label = Label(
    datetime_bar,
    text="",
    bg=PALE_PURPLE,
    fg=NAVY,
    font=("Arial", 10, "bold")
)

datetime_label.pack(side=RIGHT)


def update_clock():

    current_date = datetime.now().strftime("%d %B %Y")

    current_time = datetime.now().strftime("%I:%M:%S %p").lstrip("0")

    datetime_label.config(
        text=current_date + "   |   " + current_time
    )

    root.after(1000, update_clock)


update_clock()


search_frame = Frame(
    content,
    bg=WHITE,
    padx=16,
    pady=11,
    highlightbackground=BORDER,
    highlightthickness=1
)

search_frame.pack(
    fill=X,
    pady=(0, 10)
)

Label(
    search_frame,
    text="⌕  QUICK SEARCH",
    bg=WHITE,
    fg=NAVY,
    font=("Arial", 10, "bold")
).pack(
    side=LEFT,
    padx=(0, 15)
)

search_entry = Entry(
    search_frame,
    font=FONT_INPUT,
    width=32,
    bd=1,
    relief="solid"
)

search_entry.pack(
    side=LEFT,
    padx=5,
    ipady=5
)

Button(
    search_frame,
    text="Search  →",
    bg=PURPLE,
    fg=WHITE,
    font=FONT_BUTTON,
    relief="flat",
    padx=18,
    pady=7,
    cursor="hand2",
    activebackground=NAVY,
    activeforeground=WHITE,
    command=search_student
).pack(
    side=LEFT,
    padx=5
)


action_frame = Frame(
    content,
    bg=LIGHT
)

action_frame.pack(
    fill=X,
    pady=(5, 12)
)


result_frame = Frame(
    content,
    bg=PURPLE,
    padx=2,
    pady=2
)

result_frame.pack(
    fill=BOTH,
    expand=True,
    pady=(0, 5)
)

records_panel = Frame(
    result_frame,
    bg=WHITE
)

records_panel.pack(
    fill=BOTH,
    expand=True
)

Frame(
    records_panel,
    bg=NAVY,
    height=5
).pack(fill=X)

records_header = Frame(
    records_panel,
    bg=PALE_PURPLE,
    padx=18,
    pady=11
)

records_header.pack(fill=X)

records_heading_area = Frame(
    records_header,
    bg=PALE_PURPLE
)

records_heading_area.pack(
    side=LEFT,
    fill=X,
    expand=True
)

Label(
    records_heading_area,
    text="STUDENT RECORDS",
    bg=PALE_PURPLE,
    fg=NAVY,
    font=("Arial", 14, "bold")
).pack(anchor="w")

Label(
    records_heading_area,
    text="Academic information and performance overview",
    bg=PALE_PURPLE,
    fg=GREY,
    font=("Arial", 10)
).pack(
    anchor="w",
    pady=(3, 0)
)

Label(
    records_header,
    text="ACADEMIC DATABASE",
    bg=PURPLE,
    fg=WHITE,
    font=("Arial", 9, "bold"),
    padx=12,
    pady=7
).pack(side=RIGHT)

Frame(
    records_panel,
    bg=BORDER,
    height=1
).pack(fill=X)


output_area = Frame(
    records_panel,
    bg=WHITE,
    padx=15,
    pady=13
)

output_area.pack(
    fill=BOTH,
    expand=True
)

output = Text(
    output_area,
    bg=WHITE,
    fg=NAVY,
    font=FONT_OUTPUT,
    wrap="none",
    bd=0,
    padx=14,
    pady=14,
    spacing1=4,
    spacing3=4
)

output.pack(
    side=LEFT,
    fill=BOTH,
    expand=True
)

output.configure(
    tabs=(100, 260, 325, 390, 455, 520, 595, 675, 755)
)

output.tag_configure(
    "table_heading",
    font=("Consolas", 9, "bold"),
    foreground=NAVY,
    spacing1=8,
    spacing3=8
)

output.tag_configure(
    "low",
    foreground="#DC2626",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "average",
    foreground="#D97706",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "good",
    foreground="#16845B",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "grade_A",
    foreground="#16845B",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "grade_B",
    foreground="#16845B",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "grade_C",
    foreground="#D97706",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "grade_D",
    foreground="#EA580C",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "grade_F",
    foreground="#DC2626",
    font=("Consolas", 9, "bold")
)

output.tag_configure(
    "summary_heading",
    font=("Arial", 12, "bold"),
    foreground=NAVY
)

output.tag_configure(
    "overview_heading",
    font=("Arial", 13, "bold"),
    foreground=NAVY,
    spacing1=10,
    spacing3=10
)

output.tag_configure(
    "section_heading",
    font=("Arial", 12, "bold"),
    foreground=NAVY,
    spacing1=8,
    spacing3=8
)


scrollbar = Scrollbar(
    output_area,
    command=output.yview
)

scrollbar.pack(
    side=RIGHT,
    fill=Y
)

horizontal_scrollbar = Scrollbar(
    records_panel,
    orient=HORIZONTAL,
    command=output.xview
)

horizontal_scrollbar.pack(
    side=BOTTOM,
    fill=X
)

output.config(
    yscrollcommand=scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)


Frame(
    records_panel,
    bg=PURPLE,
    height=4
).pack(fill=X)


home()

print("Folder:", folder)
print("JSON file exists:", os.path.exists(file_name))
print("Files in exercise 3:", os.listdir(folder))

root.mainloop()