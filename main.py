# main.py
# tkinter GUI, connects the other files together
# run this file to start the app:  python main.py
import tkinter as tk
from tkinter import ttk, messagebox

import file_operations
import calculations
import interface


# ----- global state -----

root = None             # the main window
current_user_id = None  # who is logged in ("admin" or a student ID)
content_frame = None    # the area under the buttons that shows tables


# ----- helpers -----

# wipe the window before showing another screen
def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


def set_user(uid):
    global current_user_id
    current_user_id = uid


# clear the area under the buttons
def clear_content():
    for widget in content_frame.winfo_children():
        widget.destroy()


# table with the given columns
def make_table(columns):
    tree = ttk.Treeview(content_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
    tree.pack(fill="both", expand=True)
    return tree


# ----- login screen -----

def show_login_screen():
    clear_window()
    root.title("University Login")
    root.geometry("400x300")

    tk.Label(root, text="University System", font=("Arial", 20, "bold")).pack(pady=20)

    frame = tk.Frame(root)
    frame.pack(pady=10)
    tk.Label(frame, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
    entry_user = tk.Entry(frame)
    entry_user.grid(row=0, column=1, padx=5, pady=5)
    tk.Label(frame, text="Password:").grid(row=1, column=0, padx=5, pady=5)
    entry_pass = tk.Entry(frame, show="*")
    entry_pass.grid(row=1, column=1, padx=5, pady=5)

    def perform_login():
        u = entry_user.get()
        p = entry_pass.get()

        if u == "admin" and p == "admin":
            set_user("admin")
            show_admin_screen()
            return

        for s in file_operations.read_students():
            if s['id'] == u and s['pass'] == p:
                set_user(s['id'])
                show_student_screen()
                return

        messagebox.showerror("Error", "Invalid Credentials")

    tk.Button(root, text="Login", command=perform_login, bg="lightblue", width=15).pack(pady=10)
    tk.Button(root, text="New Applicant", command=show_applicant_screen, width=15).pack()


# ----- student screen -----

# student dashboard
def show_student_screen():
    global content_frame
    clear_window()
    root.title(f"Student Portal - {current_user_id}")
    root.geometry("800x600")

    header = tk.Frame(root, bg="lightgray", height=40)
    header.pack(fill="x")
    tk.Label(header, text="Student Dashboard", bg="lightgray", font=("Arial", 14)).pack(side="left", padx=10)
    tk.Button(header, text="Logout", command=show_login_screen, bg="red", fg="white").pack(side="right", padx=10, pady=5)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def view_courses():
        clear_content()
        tree = make_table(("Code", "Name", "Credits", "Time"))
        for c in file_operations.read_courses():
            tree.insert("", "end", values=(c['code'], c['name'], c['cred'], f"{c['days']} {c['time']}"))

    # only this student's courses
    def view_schedule():
        clear_content()
        tree = make_table(("Code", "Name", "Time"))
        regs = file_operations.read_registrations()
        courses = file_operations.read_courses()
        for r in regs:
            if r['student_id'] == current_user_id:
                for c in courses:
                    if c['code'] == r['course_code']:
                        tree.insert("", "end", values=(c['code'], c['name'], f"{c['days']} {c['time']}"))

    def register_popup():
        win = tk.Toplevel(root)
        win.title("Register")
        tk.Label(win, text="Course Code:").pack(pady=5)
        e = tk.Entry(win)
        e.pack(pady=5)

        # validate, then save
        def confirm():
            code = e.get()
            regs = file_operations.read_registrations()
            courses = file_operations.read_courses()

            ok, msg = calculations.validate_registration(current_user_id, code, regs, courses)
            if not ok:
                messagebox.showerror("Error", msg)
                return

            regs.append({'student_id': current_user_id, 'course_code': code})
            file_operations.write_registrations(regs)
            messagebox.showinfo("Success", "Registered")
            win.destroy()
            view_schedule()

        tk.Button(win, text="Add", command=confirm).pack(pady=5)

    def drop_popup():
        win = tk.Toplevel(root)
        win.title("Drop")
        tk.Label(win, text="Course Code:").pack(pady=5)
        e = tk.Entry(win)
        e.pack(pady=5)

        def confirm():
            if file_operations.drop_course(current_user_id, e.get()):
                messagebox.showinfo("Success", "Dropped")
                win.destroy()
                view_schedule()
            else:
                messagebox.showerror("Error", "Not Found")

        tk.Button(win, text="Drop", command=confirm).pack(pady=5)

    tk.Button(btn_frame, text="All Courses", command=view_courses).pack(side="left", padx=5)
    tk.Button(btn_frame, text="My Schedule", command=view_schedule).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Register", command=register_popup).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Drop", command=drop_popup).pack(side="left", padx=5)

    view_schedule()


# ----- admin screen -----

# admin dashboard
def show_admin_screen():
    global content_frame
    clear_window()
    root.title("Admin Dashboard")
    root.geometry("800x600")

    header = tk.Frame(root, bg="gray", height=40)
    header.pack(fill="x")
    tk.Label(header, text="Admin Control", bg="gray", fg="white", font=("Arial", 14)).pack(side="left", padx=10)
    tk.Button(header, text="Logout", command=show_login_screen, bg="red", fg="white").pack(side="right", padx=10, pady=5)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    content_frame = tk.Frame(root)
    content_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def show_students():
        clear_content()
        tree = make_table(("ID", "Name", "Major", "Year"))
        for s in file_operations.read_students():
            tree.insert("", "end", values=(s['id'], s['name'], s['prog'], s['year']))

    def show_courses():
        clear_content()
        tree = make_table(("Code", "Name", "Cred", "Cap"))
        for c in file_operations.read_courses():
            tree.insert("", "end", values=(c['code'], c['name'], c['cred'], c['capacity']))

    def show_stats():
        clear_content()
        counts = calculations.count_students_per_course(file_operations.read_registrations())
        txt = tk.Text(content_frame)
        txt.pack(fill="both", expand=True)
        for k, v in counts.items():
            txt.insert("end", f"{k}: {v} Students\n")

    def open_chart():
        interface.display_chart()

    # pending applications only
    def review_apps():
        clear_content()
        tree = make_table(("ID", "Name", "Status"))
        apps = file_operations.read_applications()
        for a in apps:
            if a['status'] == 'Pending':
                tree.insert("", "end", values=(a['id'], a['name'], a['status']))

        # accepting also creates the student account
        def action(new_status):
            sel = tree.selection()
            if not sel:
                return
            aid = tree.item(sel[0])['values'][0]
            target = next((a for a in apps if str(a['id']) == str(aid)), None)
            if not target:
                return

            target['status'] = new_status
            if new_status == 'Accepted':
                students = file_operations.read_students()
                ids = [int(s['id']) for s in students if s['id'].isdigit()]
                new_id = str(max(ids) + 1) if ids else "20250001"
                students.append({'id': new_id, 'name': target['name'], 'prog': 'CS', 'year': '2025', 'pass': '123456'})
                file_operations.write_students(students)
                messagebox.showinfo("Done", f"Student ID: {new_id}")

            file_operations.write_applications(apps)
            review_apps()

        tk.Button(content_frame, text="Accept", command=lambda: action("Accepted"), bg="green").pack(side="left")
        tk.Button(content_frame, text="Reject", command=lambda: action("Rejected"), bg="red").pack(side="left")

    def add_course_popup():
        win = tk.Toplevel(root)
        win.title("Add Course")
        entries = {}
        for field in ["Code", "Name", "Credits", "Days", "Time", "Capacity"]:
            tk.Label(win, text=field).pack()
            entries[field] = tk.Entry(win)
            entries[field].pack()

        # a lab or section can reuse an existing code
        def save():
            try:
                course = {'code': entries["Code"].get(), 'name': entries["Name"].get(),
                          'cred': int(entries["Credits"].get()), 'days': entries["Days"].get(),
                          'time': entries["Time"].get(), 'capacity': int(entries["Capacity"].get())}
            except ValueError:
                messagebox.showerror("Error", "Invalid Data")
                return

            courses = file_operations.read_courses()
            courses.append(course)
            file_operations.write_courses(courses)
            messagebox.showinfo("Success", "Added")
            win.destroy()
            show_courses()

        tk.Button(win, text="Save", command=save).pack(pady=5)

    tk.Button(btn_frame, text="Students", command=show_students).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Courses", command=show_courses).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Add Course", command=add_course_popup).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Apps", command=review_apps).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Stats", command=show_stats).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Chart", command=open_chart, bg="orange").pack(side="left", padx=5)

    show_students()


# ----- applicant screen -----

# application form
def show_applicant_screen():
    clear_window()
    root.title("New Application")
    tk.Label(root, text="New Application", font=("Arial", 16)).pack(pady=20)

    frame = tk.Frame(root)
    frame.pack(pady=10)
    tk.Label(frame, text="Name:").pack()
    en = tk.Entry(frame)
    en.pack()
    tk.Label(frame, text="Email:").pack()
    ee = tk.Entry(frame)
    ee.pack()
    tk.Label(frame, text="Phone:").pack()
    ep = tk.Entry(frame)
    ep.pack()

    def submit():
        n, e, p = en.get(), ee.get(), ep.get()
        valid, msg = calculations.validate_application(n, e, p)
        if valid:
            app_id = file_operations.submit_application(n, e, p)
            messagebox.showinfo("Success", f"ID: {app_id}")
            show_login_screen()
        else:
            messagebox.showerror("Error", msg)

    tk.Button(root, text="Submit", command=submit, bg="green").pack(pady=10)
    tk.Button(root, text="Back", command=show_login_screen).pack()


# ----- entry point -----

# start here
def main():
    global root
    file_operations.initialize_files()
    root = tk.Tk()
    show_login_screen()
    root.mainloop()


if __name__ == "__main__":
    main()
