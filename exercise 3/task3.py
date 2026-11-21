from tkinter import *
from tkinter import messagebox
import os
from datetime import datetime
import json


# Colours and fonts used throughout the application.
# Keeping them in variables makes it easier to change the design later.

NAVY = "#344054"
SIDEBAR = "#293444"
PURPLE = "#64748B"
LIGHT = "#E8EBF0"
WHITE = "#FFFFFF"
GREY = "#667085"
BORDER = "#C5CBD4"
PALE_PURPLE = "#E1E5EC"
SIDE_GREY = "#C5CBD4"

RED = "#DC5555"
ORANGE = "#D97706"
GREEN = "#16845B"

# Set different font styles so headings, buttons and information are consistent.
FONT_TITLE = ("Arial", 24, "bold")
FONT_SUBTITLE = ("Arial", 11)
FONT_BODY = ("Arial", 11)
FONT_BUTTON = ("Arial", 10, "bold")
FONT_INPUT = ("Arial", 11)
FONT_OUTPUT = ("Consolas", 9)


# JSON file management

# Find the folder where this Python program is saved.
# The JSON file is stored in the same folder so the program can locate it.
main_folder = os.path.dirname(os.path.abspath(__file__))
folder = main_folder
file_name = os.path.join(folder, "studentMarks.json")

# This list holds all student records while the program is running.
students = []


def load_students():

    # Clear the list first so existing records are not duplicated when reloaded.
    students.clear()

    # Display file information in the console to help check that the correct
    # JSON file and folder are being used.
    print("\n========== FILE CHECK ==========")
    print("Python file:", os.path.abspath(__file__))
    print("Folder:", folder)
    print("JSON path:", file_name)
    print("JSON exists:", os.path.isfile(file_name))
    print("Files in folder:", os.listdir(folder))

    # Stop loading if the JSON file cannot be found.
    if not os.path.isfile(file_name):
        print("JSON FILE NOT FOUND!")
        return

    # Open the JSON file in read mode and load its saved information.
    with open(file_name, "r") as file:
        data = json.load(file)

    print("JSON keys:", data.keys())

    # Take each student's details from the JSON file and place them into
    # a list in the same order used by the rest of the program.
    for student in data["students"]:

        students.append([
            student["number"],
            student["name"],
            student["cw1"],
            student["cw2"],
            student["cw3"],
            student["exam"]
        ])

    # Show how many student records were successfully loaded.
    print("TOTAL STUDENTS LOADED:", len(students))
    print("================================\n")


def save_students():

    # Create a dictionary with an empty student list.
    # Each student will be added to this list before saving.
    data = {"students": []}

    # Convert each student's list into a dictionary with named fields.
    # This makes the information easier to organise inside the JSON file.
    for student in students:

        data["students"].append({
            "number": student[0],
            "name": student[1],
            "cw1": student[2],
            "cw2": student[3],
            "cw3": student[4],
            "exam": student[5]
        })

    # Open the JSON file in write mode and save the updated student records.
    # indent=4 makes the saved information easier to read.
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)


# Calculate student results and grades

def calculate_results(student):

    # Add the three coursework marks together, then include the exam mark.
    coursework = student[2] + student[3] + student[4]
    total = coursework + student[5]

    # Convert the total mark out of 160 into a percentage.
    percentage = (total / 160) * 100

    # Assign a grade depending on the percentage achieved by the student.
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

    # Return all calculated results so other functions can use them.
    return coursework, total, percentage, grade


def get_mark_colour(mark, maximum):

    # Calculate the percentage of the mark to decide which colour to use.
    percentage = (mark / maximum) * 100

    # Return a colour category based on how well the student performed.
    if percentage < 50:
        return "low"
    elif percentage < 70:
        return "average"
    else:
        return "good"


def check_marks(mark1, mark2, mark3, exam):

    # Check that all three coursework marks are within the allowed range of 0–20.
    if not (0 <= mark1 <= 20 and 0 <= mark2 <= 20 and 0 <= mark3 <= 20):

        messagebox.showerror(
            "Error",
            "Coursework marks must be between 0 and 20."
        )

        # Return False to stop the record from being saved.
        return False

    # Check that the exam mark is within the allowed range of 0–100.
    if not (0 <= exam <= 100):

        messagebox.showerror(
            "Error",
            "Exam mark must be between 0 and 100."
        )

        return False

    # Return True when all marks are within their allowed ranges.
    return True


def get_mark(entry, maximum):

    # Read the mark entered by the user and remove any extra spaces.
    value = entry.get().strip()

    # Allow marks to be entered with or without their maximum value,
    # for example, 11 or 11/20.
    if "/" in value:

        parts = value.split("/")

        # Make sure the user has entered only a mark and its maximum.
        if len(parts) != 2:
            raise ValueError

        # Check that the maximum entered matches the correct assessment.
        if int(parts[1]) != maximum:
            raise ValueError

        # Extract the actual mark before the slash.
        mark = int(parts[0])

    else:
        # Convert the entered value into a whole number.
        mark = int(value)

    return mark


def find_student(search):

    # Go through every student record to find a matching number or name.
    for student in students:

        # Convert both values to lowercase so the search is not affected
        # by whether the user enters uppercase or lowercase letters.
        if (student[0].lower() == search.lower()
                or student[1].lower() == search.lower()):

            # Return the matching student record when found.
            return student

    # Return None when no matching student exists.
    return None


# Clear the current page and hide unused action buttons

def clear_page():

    # Remove all text and displayed information from the output area.
    output.delete("1.0", END)

    # Destroy buttons and other widgets from the previous page.
    for widget in action_frame.winfo_children():
        widget.destroy()

    # Hide the action area when the current page does not need it.
    action_frame.pack_forget()


def clear_output():

    # Clear only the results area without changing the action buttons.
    output.delete("1.0", END)


# Display student information in a table

def display_table(student_list):

    # Check whether the list contains any student records before displaying it.
    if len(student_list) == 0:

        output.insert(END, "No student records available.\n")
        return

    # Display the column headings for the student results table.
    output.insert(
        END,
        "Student ID\tName\tCW1\tCW2\tCW3\tExam\tTotal\tPercentage\tGrade\n",
        "table_heading"
    )

    output.insert(END, "\n")

    # Go through each student and calculate their overall results.
    for student in student_list:

        coursework, total, percentage, grade = calculate_results(student)

        # Display the student's identification number and name.
        output.insert(END, student[0] + "\t")
        output.insert(END, student[1][:18] + "\t")

        # Display each coursework mark using a colour based on performance.
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

        # Display the exam mark with its performance colour.
        output.insert(
            END,
            str(student[5]) + "\t",
            get_mark_colour(student[5], 100)
        )

        # Display the total mark and percentage using the overall performance colour.
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

        # Display the final grade using its matching grade colour.
        output.insert(
            END,
            grade + "\n\n",
            "grade_" + grade
        )


def display_student(student):

    # Send one student as a list to the table function so their details
    # are displayed using the same table layout as all other records.
    display_table([student])


# Calculate and display class performance

def display_summary():

    # There is no summary to display if the student list is empty.
    if len(students) == 0:
        return

    # Set starting values before calculating the class performance.
    total_percentage = 0
    highest_mark = 0
    lowest_mark = 160

    # Calculate the results for every student to find the class statistics.
    for student in students:

        coursework, total, percentage, grade = calculate_results(student)

        # Add each student's percentage so the class average can be calculated.
        total_percentage += percentage

        # Keep track of the highest overall mark.
        if total > highest_mark:
            highest_mark = total

        # Keep track of the lowest overall mark.
        if total < lowest_mark:
            lowest_mark = total

    # Divide the combined percentages by the number of students to find the average.
    average = total_percentage / len(students)

    output.insert(END, "\n")

    # Create a frame inside the output area to hold the class summary cards.
    summary_frame = Frame(
        output,
        bg=LIGHT,
        padx=12,
        pady=12
    )

    output.window_create(END, window=summary_frame)

    # Add a heading above the four class performance cards.
    Label(
        summary_frame,
        text="CLASS PERFORMANCE SUMMARY",
        bg=LIGHT,
        fg=NAVY,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", pady=(0, 12))

    cards_frame = Frame(summary_frame, bg=LIGHT)
    cards_frame.pack(fill=X)

    # Store the label, calculated value and colour for each summary card.
    card_details = [
        ("TOTAL STUDENTS", str(len(students)), NAVY),
        ("CLASS AVERAGE", str(round(average, 1)) + "%", PURPLE),
        ("HIGHEST MARK", str(highest_mark) + "/160", GREEN),
        ("LOWEST MARK", str(lowest_mark) + "/160", RED)
    ]

    # Create one card for each class statistic.
    for i, detail in enumerate(card_details):

        card = Frame(
            cards_frame,
            bg=WHITE,
            padx=13,
            pady=13,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        # Place the cards next to each other in the same row.
        card.grid(row=0, column=i, padx=5, sticky="nsew")

        # Display the name of the statistic at the top of each card.
        Label(
            card,
            text=detail[0],
            bg=WHITE,
            fg=GREY,
            font=("Arial", 8, "bold")
        ).pack(anchor="w")

        # Display the calculated value underneath the label.
        Label(
            card,
            text=detail[1],
            bg=WHITE,
            fg=detail[2],
            font=("Arial", 15, "bold")
        ).pack(anchor="w", pady=(7, 0))

        # Allow all four cards to share the available width equally.
        cards_frame.grid_columnconfigure(i, weight=1)

    output.insert(END, "\n\n")


# Home page

def home():

    # Clear the previous page before displaying the dashboard.
    clear_page()

    # Set the main heading and description for the home page.
    heading.config(text="Welcome to Student Manager")
    subheading.config(text="Your academic records dashboard")

    # Count how many student records are currently stored.
    total_students = len(students)

    # Set the starting values for calculating class performance.
    total_marks = 0
    highest_mark = 0
    lowest_mark = 160

    # Calculate each student's results to find the overall class statistics.
    for student in students:

        coursework, total, percentage, grade = calculate_results(student)

        # Add each student's percentage to calculate the class average.
        total_marks += percentage

        # Update the highest mark if a higher result is found.
        if total > highest_mark:
            highest_mark = total

        # Update the lowest mark if a lower result is found.
        if total < lowest_mark:
            lowest_mark = total

    # Calculate the class average only when student records exist.
    if total_students > 0:
        average = total_marks / total_students
    else:
        average = 0

    # Create a frame inside the output area to hold the dashboard cards.
    cards = Frame(output, bg=WHITE)
    output.window_create(END, window=cards)

    output.insert(END, "\n\n")

    # Store the four main dashboard statistics and their displayed values.
    card_details = [
        ("TOTAL STUDENTS", str(total_students)),
        ("CLASS AVERAGE", str(round(average, 2)) + "%"),
        ("HIGHEST MARK", str(highest_mark) + "/160"),
        ("LOWEST MARK", str(lowest_mark if total_students > 0 else 0) + "/160")
    ]

    # Create and arrange the dashboard cards in one row.
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

        # Display the statistic name in the card.
        Label(
            card,
            text=detail[0],
            bg=PALE_PURPLE,
            fg=GREY,
            font=("Arial", 8, "bold")
        ).pack(anchor="w")

        # Display the statistic value underneath its heading.
        Label(
            card,
            text=detail[1],
            bg=PALE_PURPLE,
            fg=NAVY,
            font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(7, 0))

        # Make the cards expand equally across the dashboard.
        cards.grid_columnconfigure(i, weight=1)

    # Display a short overview explaining the main features of the application.
    output.insert(END, "\n\n")
    output.insert(END, "Quick Overview\n", "overview_heading")
    output.insert(END, "Welcome to your Student Records Manager!\n\n")
    output.insert(END, "Use the navigation menu to manage academic records.\n")
    output.insert(END, "• View all student information and marks.\n")
    output.insert(END, "• Search for an individual student.\n")
    output.insert(END, "• Compare the highest and lowest marks.\n")
    output.insert(END, "• Sort students by their overall performance.\n")
    output.insert(END, "• Add, update and delete student records.\n\n")
    output.insert(END, "Select an option from the left menu to get started.")


# View all student records

def view_all():

    # Clear the current page and display the correct page heading.
    clear_page()

    heading.config(text="All Students")
    subheading.config(text="Complete list of student records and results")

    # Display a message instead of an empty table if there are no records.
    if len(students) == 0:

        output.insert(END, "No student records available yet.\n\n")
        output.insert(END, "Use Add Student to create your first record.")
        return

    # Display all student information followed by the class performance summary.
    output.insert(END, "ALL STUDENT RECORDS\n\n", "section_heading")

    display_table(students)
    display_summary()


# Find an individual student

def view_individual():

    # Clear the previous page and show instructions for searching.
    clear_page()

    heading.config(text="Find Student")
    subheading.config(text="Search using a student number or name")

    output.insert(
        END,
        "Enter a student number or name in the Quick Search box."
    )


def search_student():

    # Get the search term from the Quick Search entry box.
    search = search_entry.get().strip()

    # Clear the previous results and update the page heading.
    clear_page()

    heading.config(text="Search Results")
    subheading.config(text="Results matching your search")

    # Make sure the user has entered something before searching.
    if search == "":

        output.insert(END, "Please enter a student number or name.")
        return

    # Search for a student using their number or name.
    student = find_student(search)

    # Display the student's information if a match is found.
    if student is not None:

        output.insert(END, "STUDENT FOUND\n\n", "section_heading")
        display_student(student)

    else:
        # Display a message if no matching student exists.
        output.insert(END, "No student found.")


# Display the student with the highest mark

def highest_student():

    # Clear the page and update its heading.
    clear_page()

    heading.config(text="Highest Mark")
    subheading.config(text="Student with the highest overall mark")

    # Stop if there are no student records to compare.
    if len(students) == 0:

        output.insert(END, "No student records available.")
        return

    # Initially treat the first student as having the highest mark.
    highest = students[0]

    # Compare the total mark of every student to find the highest result.
    for student in students:

        coursework, total, percentage, grade = calculate_results(student)
        highest_coursework, highest_total, highest_percentage, highest_grade = calculate_results(highest)

        if total > highest_total:
            highest = student

    # Display the student who achieved the highest overall mark.
    output.insert(
        END,
        "STUDENT WITH HIGHEST MARK\n\n",
        "section_heading"
    )

    display_student(highest)


# Display the student with the lowest mark

def lowest_student():

    # Clear the page and update its heading.
    clear_page()

    heading.config(text="Lowest Mark")
    subheading.config(text="Student with the lowest overall mark")

    # Stop if there are no student records to compare.
    if len(students) == 0:

        output.insert(END, "No student records available.")
        return

    # Initially treat the first student as having the lowest mark.
    lowest = students[0]

    # Compare the total mark of every student to find the lowest result.
    for student in students:

        coursework, total, percentage, grade = calculate_results(student)
        lowest_coursework, lowest_total, lowest_percentage, lowest_grade = calculate_results(lowest)

        if total < lowest_total:
            lowest = student

    # Display the student who achieved the lowest overall mark.
    output.insert(
        END,
        "STUDENT WITH LOWEST MARK\n\n",
        "section_heading"
    )

    display_student(lowest)


# Sort student records

def sort_students():

    # Clear the current page and show the sorting options.
    clear_page()

    # Display the action frame above the student records area.
    action_frame.pack(
        fill=X,
        pady=(5, 12),
        before=result_frame
    )

    heading.config(text="Sort Records")
    subheading.config(text="Arrange student records by overall marks")

    # Add a label explaining what the sorting buttons will do.
    Label(
        action_frame,
        text="SORT BY OVERALL MARK",
        bg=LIGHT,
        fg=NAVY,
        font=("Arial", 10, "bold")
    ).pack(side=LEFT, padx=(0, 12))

    # Create a button to arrange students from the lowest mark to the highest.
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
        command=lambda: show_sorted("ascending")
    ).pack(side=LEFT, padx=6)

    # Create a button to arrange students from the highest mark to the lowest.
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
        command=lambda: show_sorted("descending")
    ).pack(side=LEFT, padx=6)

    output.insert(
        END,
        "Choose an order above to arrange the student records."
    )


def show_sorted(order):

    # Clear the previous results while keeping the sorting buttons visible.
    clear_output()

    # Check that there are records available to sort.
    if len(students) == 0:

        output.insert(END, "No student records available.")
        return

    # Sort the students by their total marks from lowest to highest.
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

        # Sort the students by their total marks from highest to lowest.
        # reverse=True changes the order from ascending to descending.
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

    # Display the sorted records and their class performance summary.
    display_table(sorted_students)
    display_summary()


# Create the form used for adding a student

def create_student_form(parent, values=None):

    # Store the names of the six fields needed for a student record.
    labels = [
        "Student Number",
        "Student Name",
        "Coursework 1",
        "Coursework 2",
        "Coursework 3",
        "Exam"
    ]

    # This list will hold all six entry boxes so their values can be accessed.
    entries = []

    # Create an entry box for each student detail.
    for i in range(6):

        field_frame = Frame(parent, bg=WHITE)

        # Use the row and column calculations to arrange the fields
        # in two columns instead of placing all six in one long column.
        field_frame.grid(
            row=i // 2,
            column=i % 2,
            padx=12,
            pady=9,
            sticky="ew"
        )

        # Display the field name above its entry box.
        Label(
            field_frame,
            text=labels[i],
            bg=WHITE,
            fg=NAVY,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        # Create an entry box where the user can type the information.
        entry = Entry(
            field_frame,
            font=FONT_INPUT,
            relief="solid",
            bd=1
        )

        entry.pack(fill=X, ipady=6)

        # If existing values are provided, place them into the entry boxes.
        # This is useful when displaying information that needs updating.
        if values is not None:
            entry.insert(0, str(values[i]))

        # Keep each entry box in the list so its value can be retrieved later.
        entries.append(entry)

    # Allow both form columns to expand when space is available.
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)

    # Return the entry boxes so the calling function can read their values.
    return entries


# Add a new student record

def add_student():

    # Open a separate window for entering a new student's details.
    popup = Toplevel(root)

    popup.title("Add Student Record")
    popup.geometry("600x490")
    popup.resizable(False, False)
    popup.config(bg=LIGHT)
    popup.transient(root)
    popup.grab_set()

    # Display the title banner at the top of the popup.
    Label(
        popup,
        text="＋  Add New Student",
        bg=NAVY,
        fg=WHITE,
        font=("Arial", 20, "bold"),
        padx=20,
        pady=18
    ).pack(fill=X)

    # Give the user a short instruction before displaying the form.
    Label(
        popup,
        text="Enter the student's personal and academic details below.",
        bg=LIGHT,
        fg=GREY,
        font=FONT_BODY
    ).pack(anchor="w", padx=25, pady=(18, 8))

    # Create a white frame to keep all the input fields together.
    form_frame = Frame(
        popup,
        bg=WHITE,
        padx=15,
        pady=15,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    form_frame.pack(fill=X, padx=22, pady=8)

    # Use the shared form function to create the six student entry boxes.
    entries = create_student_form(form_frame)

    def submit_student():

        # Read the student's number and name and remove extra spaces.
        number = entries[0].get().strip()
        name = entries[1].get().strip()

        # Make sure the two required personal details have been entered.
        if number == "" or name == "":

            messagebox.showerror(
                "Error",
                "Student number and name are required.",
                parent=popup
            )

            return

        # Check the existing records to prevent two students having the same ID.
        for student in students:

            if student[0] == number:

                messagebox.showerror(
                    "Error",
                    "This student number already exists.",
                    parent=popup
                )

                return

        # Try to convert all entered marks into numbers.
        # Invalid entries will be handled by the ValueError section below.
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

        # Check that the entered marks are within the correct ranges.
        if not check_marks(mark1, mark2, mark3, exam):
            return

        # Create a new student list using the details entered in the form.
        new_student = [
            number,
            name,
            mark1,
            mark2,
            mark3,
            exam
        ]

        # Add the new record to the main student list and save it to JSON.
        students.append(new_student)
        save_students()

        messagebox.showinfo(
            "Success",
            "Student added successfully.",
            parent=popup
        )

        # Close the popup and refresh the page to display the new record.
        popup.destroy()
        view_all()

    # Create the button that runs the validation and saving process.
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


# Delete a student record permanently

def delete_student():

    # Clear the previous page and display the search area for deleting records.
    clear_page()

    action_frame.pack(
        fill=X,
        pady=(5, 12),
        before=result_frame
    )

    heading.config(text="Delete Student")
    subheading.config(text="Review the student records before deleting")

    # Stop the deletion process if there are no student records.
    if len(students) == 0:

        output.insert(END, "No student records available to delete.")
        return

    # Ask the user to enter the number or name of the student to delete.
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

        # Get the search value entered by the user.
        search = delete_entry.get().strip()

        # Make sure the search box is not empty.
        if search == "":

            messagebox.showerror(
                "Error",
                "Please enter a student number or name."
            )

            return

        # Find the student whose details match the search.
        student = find_student(search)

        # Display an error if the student does not exist.
        if student is None:

            messagebox.showerror(
                "Error",
                "Student not found."
            )

            return

        # Ask for confirmation before permanently removing the record.
        confirm = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to permanently delete " + student[1] + "?"
        )

        if confirm:

            # Remove the selected student from the list and save the changes.
            students.remove(student)
            save_students()

            messagebox.showinfo(
                "Success",
                "Student permanently deleted."
            )

            # Refresh the delete page so the displayed records are up to date.
            delete_student()

    # Create the button that starts the student deletion process.
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

    # Display the current records so the user can review them before deleting.
    output.insert(END, "CURRENT STUDENT RECORDS\n\n", "section_heading")
    display_table(students)


# Search for a student before updating their information

def update_student():

    # Clear the current page and show the student search area.
    clear_page()

    action_frame.pack(
        fill=X,
        pady=(5, 12),
        before=result_frame
    )

    heading.config(text="Update Student")
    subheading.config(text="Search for a student to update their records")

    # Check that there are student records available to update.
    if len(students) == 0:

        output.insert(END, "No student records available to update.")
        return

    # Ask the user to enter the number or name of the student they want to update.
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

        # Read the search value and remove any extra spaces.
        search = update_search.get().strip()

        # Make sure the user has entered a search term.
        if search == "":

            messagebox.showerror(
                "Error",
                "Please enter a student number or name."
            )

            return

        # Find the student whose number or name matches the search.
        student = find_student(search)

        # Stop if no matching student is found.
        if student is None:

            messagebox.showerror(
                "Error",
                "Student not found."
            )

            return

        # Open the update window for the selected student.
        open_update_popup(student)

    # Create the button that searches for the student to update.
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

    # Display the existing records while the user selects a student.
    output.insert(END, "CURRENT STUDENT RECORDS\n\n", "section_heading")
    display_table(students)


# Popup for choosing and updating an individual student field

def open_update_popup(student):

    # Open a separate window containing the selected student's information.
    popup = Toplevel(root)

    popup.title("Update Student")
    popup.geometry("550x440")
    popup.resizable(False, False)
    popup.config(bg=LIGHT)
    popup.transient(root)
    popup.grab_set()

    # Display the heading at the top of the update window.
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
        text="Select the information you wish to update.",
        bg=LIGHT,
        fg=GREY,
        font=FONT_BODY
    ).pack(anchor="w", padx=25, pady=(18, 12))

    # Show the student selected for updating

    details_frame = Frame(
        popup,
        bg=WHITE,
        padx=18,
        pady=12,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    details_frame.pack(fill=X, padx=22, pady=5)

    # Display the selected student's name and identification number.
    Label(
        details_frame,
        text="SELECTED STUDENT",
        bg=WHITE,
        fg=PURPLE,
        font=("Arial", 9, "bold")
    ).pack(anchor="w")

    Label(
        details_frame,
        text=student[1] + "  |  " + student[0],
        bg=WHITE,
        fg=NAVY,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", pady=(5, 0))

    # Available fields the user can choose to update

    field_options = [
        "Student Number",
        "Student Name",
        "Coursework 1",
        "Coursework 2",
        "Coursework 3",
        "Exam"
    ]

    # Match each field name with its position in the student list.
    # This allows the program to identify which value needs to be changed.
    field_numbers = {
        "Student Number": 0,
        "Student Name": 1,
        "Coursework 1": 2,
        "Coursework 2": 3,
        "Coursework 3": 4,
        "Exam": 5
    }

    form_frame = Frame(
        popup,
        bg=LIGHT,
        padx=25,
        pady=12
    )

    form_frame.pack(fill=X)

    Label(
        form_frame,
        text="Choose field to update",
        bg=LIGHT,
        fg=NAVY,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(0, 6))

    # Use StringVar to keep track of the field selected in the dropdown.
    selected_field = StringVar()
    selected_field.set("Student Name")

    # Display the current value and allow a new value to be entered

    current_value = Label(
        form_frame,
        text="",
        bg=WHITE,
        fg=GREY,
        font=FONT_BODY,
        anchor="w",
        padx=10,
        pady=9,
        relief="solid",
        bd=1
    )

    new_value = Entry(
        form_frame,
        font=FONT_INPUT,
        relief="solid",
        bd=1
    )

    def change_field(choice):

        # Find the position of the selected field in the student list.
        index = field_numbers[choice]

        # Display the student's existing value for the selected field.
        current_value.config(
            text=str(student[index])
        )

        # Clear the entry box and fill it with the existing value.
        # The user can then edit it instead of typing everything again.
        new_value.delete(0, END)

        new_value.insert(
            0,
            str(student[index])
        )

    # Dropdown menu for selecting the field

    dropdown = OptionMenu(
        form_frame,
        selected_field,
        *field_options,
        command=change_field
    )

    dropdown.config(
        bg=WHITE,
        fg=NAVY,
        font=FONT_BODY,
        relief="solid",
        bd=1,
        highlightthickness=0
    )

    dropdown.pack(fill=X)

    Label(
        form_frame,
        text="Current Value",
        bg=LIGHT,
        fg=NAVY,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(15, 5))

    current_value.pack(fill=X)

    Label(
        form_frame,
        text="Enter New Value",
        bg=LIGHT,
        fg=NAVY,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(15, 5))

    new_value.pack(fill=X, ipady=6)

    # Show the current value when the popup first opens.
    # Student Name is selected as the default field.
    change_field("Student Name")

    # Validate and save the selected change

    def save_update():

        # Get the selected field, its position and the new value entered.
        choice = selected_field.get()
        index = field_numbers[choice]
        value = new_value.get().strip()

        # Make sure the new value is not empty.
        if value == "":

            messagebox.showerror(
                "Error",
                "Please enter a new value.",
                parent=popup
            )

            return

        # Prevent duplicate student numbers

        if index == 0:

            # Check all other records to make sure the new ID is not already used.
            for other_student in students:

                if other_student is not student and other_student[0] == value:

                    messagebox.showerror(
                        "Error",
                        "This student number already exists.",
                        parent=popup
                    )

                    return

        # Check that updated marks are valid

        if index >= 2:

            # Convert the new mark into a number using the correct maximum.
            try:

                if index == 5:
                    mark = get_mark(new_value, 100)
                else:
                    mark = get_mark(new_value, 20)

            except ValueError:

                messagebox.showerror(
                    "Error",
                    "Please enter a valid mark. Use 11 or 11/20 for coursework and 68 or 68/100 for the exam.",
                    parent=popup
                )

                return

            # Make a temporary list of the student's marks.
            # This allows the new mark to be checked with the other existing marks.
            new_marks = [
                student[2],
                student[3],
                student[4],
                student[5]
            ]

            # Replace only the mark that the user has selected to update.
            new_marks[index - 2] = mark

            # Check that all coursework and exam marks remain within their limits.
            if not check_marks(
                new_marks[0],
                new_marks[1],
                new_marks[2],
                new_marks[3]
            ):
                return

            # Use the validated number instead of the original text entry.
            value = mark

        # Update the chosen field and save the JSON file

        # Replace the old value with the new value in the student's record.
        student[index] = value

        # Save the updated student information to the JSON file.
        save_students()

        messagebox.showinfo(
            "Success",
            choice + " updated successfully!",
            parent=popup
        )

        # Close the update window and refresh the records page.
        popup.destroy()
        view_all()

    # Create the button that saves the updated student information.
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
    ).pack(anchor="e", padx=25, pady=12)


# Create the main application window

# Tk() creates the main window in which all other application widgets appear.
root = Tk()

root.title("Student Manager")
root.geometry("1180x780")
root.minsize(1050, 700)
root.config(bg=LIGHT)


# Load application icons

# Load each image from the application folder so it can be used in the sidebar.
home_icon = PhotoImage(file=os.path.join(folder, "home.png"))
student_icon = PhotoImage(file=os.path.join(folder, "student.png"))
search_icon = PhotoImage(file=os.path.join(folder, "search.png"))
highest_icon = PhotoImage(file=os.path.join(folder, "highest.png"))
lowest_icon = PhotoImage(file=os.path.join(folder, "lowest.png"))
sort_icon = PhotoImage(file=os.path.join(folder, "sort.png"))
add_icon = PhotoImage(file=os.path.join(folder, "add.png"))
delete_icon = PhotoImage(file=os.path.join(folder, "delete.png"))
update_icon = PhotoImage(file=os.path.join(folder, "update.png"))

# Load the main application icon and set it as the window icon.
app_icon = PhotoImage(file=os.path.join(folder, "icon.png"))

root.iconphoto(True, app_icon)

# Load the saved student records before displaying the home page.
load_students()


# Sidebar navigation

# Create the dark sidebar on the left side of the application.
# It contains the buttons used to move between the different pages.
sidebar = Frame(
    root,
    bg=SIDEBAR,
    width=245
)

sidebar.pack(side=LEFT, fill=Y)

# Prevent the sidebar from shrinking to fit the widgets inside it.
sidebar.pack_propagate(False)

# Display the application name at the top of the sidebar.
Label(
    sidebar,
    text="STUDENT\nMANAGER",
    bg=SIDEBAR,
    fg=SIDE_GREY,
    font=("Arial", 21, "bold"),
    justify=LEFT
).pack(anchor="w", padx=20, pady=(25, 25))


def create_button(text, command, icon):

    # Create a sidebar button with an icon, label and linked function.
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

    # Place the button across the available sidebar width.
    button.pack(fill=X, padx=12, pady=3)

    # Change the button's colours when the mouse moves over it.
    button.bind(
        "<Enter>",
        lambda event: button.config(bg=PURPLE, fg=WHITE)
    )

    # Return the button to its original colours when the mouse leaves it.
    button.bind(
        "<Leave>",
        lambda event: button.config(bg=SIDEBAR, fg="#E5E7EB")
    )


# Create the main navigation buttons and connect each one to its function.
create_button("Home", home, home_icon)
create_button("All Students", view_all, student_icon)
create_button("Find Student", view_individual, search_icon)
create_button("Highest Mark", highest_student, highest_icon)
create_button("Lowest Mark", lowest_student, lowest_icon)


# Add a divider to separate the main navigation options from record management.
Frame(
    sidebar,
    bg="#64748B",
    height=1
).pack(fill=X, padx=20, pady=15)


# Display a heading above the record management buttons.
Label(
    sidebar,
    text="MANAGE RECORDS",
    bg=SIDEBAR,
    fg="#AEB8C7",
    font=("Arial", 9, "bold")
).pack(anchor="w", padx=20, pady=(0, 8))


# Create buttons for sorting, adding, deleting and updating student records.
create_button("Sort Records", sort_students, sort_icon)
create_button("Add Student", add_student, add_icon)
create_button("Delete Student", delete_student, delete_icon)
create_button("Update Student", update_student, update_icon)


# Main content area

# This frame holds the main application pages and fills the space beside the sidebar.
content = Frame(root, bg=LIGHT)

content.pack(
    side=RIGHT,
    fill=BOTH,
    expand=True,
    padx=25,
    pady=18
)


# Page title section

# Create a coloured border around the title area to make it stand out.
title_border = Frame(
    content,
    bg=PURPLE,
    padx=2,
    pady=2
)

title_border.pack(fill=X, pady=(0, 10))

# Place the title and subtitle inside the bordered area.
title_row = Frame(
    title_border,
    bg=WHITE,
    padx=22,
    pady=15
)

title_row.pack(fill=X)

# Keep the page headings together on the left side of the title area.
heading_area = Frame(title_row, bg=WHITE)

heading_area.pack(side=LEFT, fill=X, expand=True)

# Display the smaller application heading above the main page title.
Label(
    heading_area,
    text="ACADEMIC MANAGEMENT SYSTEM",
    bg=WHITE,
    fg=PURPLE,
    font=("Arial", 9, "bold")
).pack(anchor="w", pady=(0, 6))

# This label is updated whenever the user opens a different page.
heading = Label(
    heading_area,
    text="Welcome to Student Manager",
    bg=WHITE,
    fg=NAVY,
    font=FONT_TITLE
)

heading.pack(anchor="w")

# This label displays a short description underneath the main heading.
subheading = Label(
    heading_area,
    text="Your academic records dashboard",
    bg=WHITE,
    fg=GREY,
    font=FONT_SUBTITLE
)

subheading.pack(anchor="w", pady=(5, 0))

# Add a short coloured line underneath the page heading for decoration.
Frame(
    heading_area,
    bg=PURPLE,
    height=3,
    width=60
).pack(anchor="w", pady=(9, 0))


# Date and time display

# Create a separate bar to show the current date and time.
datetime_bar = Frame(
    content,
    bg=PALE_PURPLE,
    padx=14,
    pady=8,
    highlightbackground=BORDER,
    highlightthickness=1
)

datetime_bar.pack(fill=X, pady=(0, 10))

# Display a label identifying the date and time section.
Label(
    datetime_bar,
    text="CURRENT DATE & TIME",
    bg=PALE_PURPLE,
    fg=PURPLE,
    font=("Arial", 9, "bold")
).pack(side=LEFT)

# This label will be updated with the current date and time.
datetime_label = Label(
    datetime_bar,
    text="",
    bg=PALE_PURPLE,
    fg=NAVY,
    font=("Arial", 10, "bold")
)

datetime_label.pack(side=RIGHT)


def update_clock():

    # Get the current date and format it into a readable form.
    current_date = datetime.now().strftime("%d %B %Y")

    # Get the current time in 12-hour format and remove an unnecessary leading zero.
    current_time = datetime.now().strftime("%I:%M:%S %p").lstrip("0")

    # Display the date and time together in the label.
    datetime_label.config(
        text=current_date + "   |   " + current_time
    )

    # Run this function again after 1000 milliseconds (one second).
    root.after(1000, update_clock)


# Start the clock so the date and time update automatically.
update_clock()


# Quick search bar

# Create a white search area near the top of the main content section.
search_frame = Frame(
    content,
    bg=WHITE,
    padx=16,
    pady=11,
    highlightbackground=BORDER,
    highlightthickness=1
)

search_frame.pack(fill=X, pady=(0, 10))

# Display the quick search label beside the entry box.
Label(
    search_frame,
    text="⌕  QUICK SEARCH",
    bg=WHITE,
    fg=NAVY,
    font=("Arial", 10, "bold")
).pack(side=LEFT, padx=(0, 15))

# Allow the user to enter a student number or name.
search_entry = Entry(
    search_frame,
    font=FONT_INPUT,
    width=32,
    bd=1,
    relief="solid"
)

search_entry.pack(side=LEFT, padx=5, ipady=5)

# Run the search function when the Search button is clicked.
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
).pack(side=LEFT, padx=5)


# This frame is only displayed on pages that need extra action buttons,
# such as the sorting, deleting and updating pages.
action_frame = Frame(
    content,
    bg=LIGHT
)


# Student records panel

# Create the outer frame with a purple border around the records section.
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

# Create the white panel that holds the records heading and output area.
records_panel = Frame(result_frame, bg=WHITE)
records_panel.pack(fill=BOTH, expand=True)

# Add a dark line across the top of the records panel.
Frame(
    records_panel,
    bg=NAVY,
    height=5
).pack(fill=X)

# Create the header area above the student records.
records_header = Frame(
    records_panel,
    bg=PALE_PURPLE,
    padx=18,
    pady=11
)

records_header.pack(fill=X)

# Keep the records heading and its description together on the left.
records_heading_area = Frame(records_header, bg=PALE_PURPLE)

records_heading_area.pack(side=LEFT, fill=X, expand=True)

# Display the main heading for the student records panel.
Label(
    records_heading_area,
    text="STUDENT RECORDS",
    bg=PALE_PURPLE,
    fg=NAVY,
    font=("Arial", 14, "bold")
).pack(anchor="w")

# Explain what information is shown in the records section.
Label(
    records_heading_area,
    text="Academic information and performance overview",
    bg=PALE_PURPLE,
    fg=GREY,
    font=("Arial", 10)
).pack(anchor="w", pady=(3, 0))

# Add a small label on the right to identify the records database.
Label(
    records_header,
    text="ACADEMIC DATABASE",
    bg=PURPLE,
    fg=WHITE,
    font=("Arial", 9, "bold"),
    padx=12,
    pady=7
).pack(side=RIGHT)

# Add a thin divider underneath the records heading.
Frame(
    records_panel,
    bg=BORDER,
    height=1
).pack(fill=X)


# Student records output area

# Create a frame to hold the text output and its scrollbars.
output_area = Frame(
    records_panel,
    bg=WHITE,
    padx=15,
    pady=13
)

output_area.pack(fill=BOTH, expand=True)

# The Text widget displays student records, search results and dashboard information.
# It also allows tables and coloured text to be inserted.
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

output.pack(side=LEFT, fill=BOTH, expand=True)

# Set tab positions so each column in the student table lines up correctly.
output.configure(
    tabs=(100, 260, 325, 390, 455, 520, 595, 675, 755)
)


# Text formatting styles

# Set the appearance of the table headings.
output.tag_configure(
    "table_heading",
    font=("Consolas", 9, "bold"),
    foreground=NAVY,
    spacing1=8,
    spacing3=8
)

# Set the colours used to identify low, average and good marks.
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

# Set the colours used for each final grade.
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

# Set the font and colour for the class summary heading.
output.tag_configure(
    "summary_heading",
    font=("Arial", 12, "bold"),
    foreground=NAVY
)

# Set the style for the Quick Overview heading on the home page.
output.tag_configure(
    "overview_heading",
    font=("Arial", 13, "bold"),
    foreground=NAVY,
    spacing1=10,
    spacing3=10
)

# Set the style for section headings displayed above student results.
output.tag_configure(
    "section_heading",
    font=("Arial", 12, "bold"),
    foreground=NAVY,
    spacing1=8,
    spacing3=8
)


# Scrollbars for the records table

# Add a vertical scrollbar so the user can move up and down through the records.
scrollbar = Scrollbar(
    output_area,
    command=output.yview
)

scrollbar.pack(side=RIGHT, fill=Y)

# Add a horizontal scrollbar so the user can view columns that extend beyond the screen.
horizontal_scrollbar = Scrollbar(
    records_panel,
    orient=HORIZONTAL,
    command=output.xview
)

horizontal_scrollbar.pack(side=BOTTOM, fill=X)

# Connect both scrollbars to the Text widget so they move with the displayed content.
output.config(
    yscrollcommand=scrollbar.set,
    xscrollcommand=horizontal_scrollbar.set
)

# Add a coloured line at the bottom of the records panel.
Frame(
    records_panel,
    bg=PURPLE,
    height=4
).pack(fill=X)


# Start the application

# Display the home dashboard when the program first opens.
home()

# Print the JSON folder and file details in the console for checking.
print("Folder:", folder)
print("JSON file exists:", os.path.exists(file_name))
print("Files in exercise 3:", os.listdir(folder))

# Keep the application window open and listen for user actions.
root.mainloop()