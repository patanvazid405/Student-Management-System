import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

from database import StudentDatabase


class StudentManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("900x560")
        self.root.minsize(820, 520)
        self.root.configure(bg="#f4f7fb")

        self.database = StudentDatabase()
        self.selected_student_id = None

        self.name_var = tk.StringVar()
        self.age_var = tk.StringVar()
        self.course_var = tk.StringVar()
        self.email_var = tk.StringVar()

        self._configure_styles()
        self._build_layout()
        self._load_students()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10))

    def _build_layout(self):
        header = tk.Label(
            self.root,
            text="Student Management System",
            font=("Georgia", 22, "bold"),
            bg="#f4f7fb",
            fg="#1d3557",
            pady=16,
        )
        header.pack()

        container = tk.Frame(self.root, bg="#f4f7fb", padx=18, pady=8)
        container.pack(fill="both", expand=True)

        form_card = tk.Frame(
            container,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=18,
            pady=18,
        )
        form_card.pack(side="left", fill="y", padx=(0, 14))

        table_card = tk.Frame(
            container,
            bg="#ffffff",
            bd=1,
            relief="solid",
            padx=14,
            pady=14,
        )
        table_card.pack(side="right", fill="both", expand=True)

        tk.Label(
            form_card,
            text="Student Details",
            font=("Georgia", 16, "bold"),
            bg="#ffffff",
            fg="#243b53",
        ).pack(anchor="w", pady=(0, 16))

        self._create_input(form_card, "Name", self.name_var)
        self._create_input(form_card, "Age", self.age_var)
        self._create_input(form_card, "Course", self.course_var)
        self._create_input(form_card, "Email", self.email_var)

        button_row = tk.Frame(form_card, bg="#ffffff")
        button_row.pack(fill="x", pady=(18, 0))

        self._create_button(button_row, "Add", "#2a9d8f", self.add_student).pack(
            fill="x", pady=4
        )
        self._create_button(button_row, "Update", "#e9c46a", self.update_student).pack(
            fill="x", pady=4
        )
        self._create_button(button_row, "Delete", "#e76f51", self.delete_student).pack(
            fill="x", pady=4
        )
        self._create_button(button_row, "Clear", "#577590", self.clear_form).pack(
            fill="x", pady=4
        )

        tk.Label(
            table_card,
            text="Student List",
            font=("Georgia", 16, "bold"),
            bg="#ffffff",
            fg="#243b53",
        ).pack(anchor="w", pady=(0, 10))

        columns = ("id", "name", "age", "course", "email")
        self.student_table = ttk.Treeview(
            table_card,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        headings = {
            "id": "ID",
            "name": "Name",
            "age": "Age",
            "course": "Course",
            "email": "Email",
        }
        widths = {"id": 70, "name": 150, "age": 70, "course": 140, "email": 220}

        for key in columns:
            self.student_table.heading(key, text=headings[key])
            self.student_table.column(key, width=widths[key], anchor="center")

        scrollbar = ttk.Scrollbar(
            table_card, orient="vertical", command=self.student_table.yview
        )
        self.student_table.configure(yscrollcommand=scrollbar.set)

        self.student_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.student_table.bind("<<TreeviewSelect>>", self.on_student_select)

    def _create_input(self, parent, label_text, variable):
        frame = tk.Frame(parent, bg="#ffffff")
        frame.pack(fill="x", pady=6)

        tk.Label(
            frame,
            text=label_text,
            font=("Segoe UI", 10, "bold"),
            bg="#ffffff",
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        tk.Entry(
            frame,
            textvariable=variable,
            font=("Segoe UI", 11),
            bd=1,
            relief="solid",
        ).pack(fill="x", ipady=6)

    def _create_button(self, parent, text, bg_color, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, "bold"),
            bg=bg_color,
            fg="white",
            activebackground=bg_color,
            activeforeground="white",
            bd=0,
            padx=12,
            pady=10,
            cursor="hand2",
        )

    def _load_students(self):
        for item in self.student_table.get_children():
            self.student_table.delete(item)

        for student in self.database.fetch_students():
            self.student_table.insert("", "end", values=student)

    def _validate_form(self):
        name = self.name_var.get().strip()
        age_text = self.age_var.get().strip()
        course = self.course_var.get().strip()
        email = self.email_var.get().strip()

        if not all([name, age_text, course, email]):
            messagebox.showerror("Missing Data", "All fields are required.")
            return None

        if not age_text.isdigit() or int(age_text) <= 0:
            messagebox.showerror("Invalid Age", "Age must be a positive number.")
            return None

        if "@" not in email or "." not in email:
            messagebox.showerror("Invalid Email", "Enter a valid email address.")
            return None

        return name, int(age_text), course, email

    def add_student(self):
        values = self._validate_form()
        if not values:
            return

        try:
            self.database.add_student(*values)
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Email", "This email already exists.")
            return

        self._load_students()
        self.clear_form()
        messagebox.showinfo("Success", "Student added successfully.")

    def update_student(self):
        if self.selected_student_id is None:
            messagebox.showwarning("No Selection", "Select a student to update.")
            return

        values = self._validate_form()
        if not values:
            return

        try:
            self.database.update_student(self.selected_student_id, *values)
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Email", "This email already exists.")
            return

        self._load_students()
        self.clear_form()
        messagebox.showinfo("Success", "Student updated successfully.")

    def delete_student(self):
        if self.selected_student_id is None:
            messagebox.showwarning("No Selection", "Select a student to delete.")
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            "Are you sure you want to delete this student?",
        )
        if not confirmed:
            return

        self.database.delete_student(self.selected_student_id)
        self._load_students()
        self.clear_form()
        messagebox.showinfo("Success", "Student deleted successfully.")

    def clear_form(self):
        self.selected_student_id = None
        self.name_var.set("")
        self.age_var.set("")
        self.course_var.set("")
        self.email_var.set("")
        self.student_table.selection_remove(self.student_table.selection())

    def on_student_select(self, _event):
        selected = self.student_table.selection()
        if not selected:
            return

        values = self.student_table.item(selected[0], "values")
        self.selected_student_id = int(values[0])
        self.name_var.set(values[1])
        self.age_var.set(values[2])
        self.course_var.set(values[3])
        self.email_var.set(values[4])


def main():
    root = tk.Tk()
    StudentManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
