# interface.py
# console menus, search/sort helpers and the matplotlib chart
import file_operations
import calculations
import matplotlib.pyplot as plt


# ----- menus -----

def display_main_menu():
    print("1. Login")
    print("2. Exit")


def display_student_menu():
    print("1. Search Course")
    print("2. Search Student")
    print("3. Show Schedule")
    print("4. Register Course")
    print("5. Logout")


def display_admin_menu():
    print("1. Search Student")
    print("2. Search Course")
    print("3. Sort Students by Credits")
    print("4. Sort Courses by Popularity")
    print("5. Add Course")
    print("6. Review Applications")
    print("7. Enrollment Report")
    print("8. Logout")


# ----- login -----

# returns (role, id) or (None, None) if the login is wrong
def login_system():
    u = input("ID: ")
    p = input("Password: ")

    students = file_operations.read_students()
    for s in students:
        if s['id'] == u and s['pass'] == p:
            return "student", s['id']

    if u == "admin" and p == "admin":
        return "admin", "admin"

    print("Wrong login")
    return None, None


# ----- search -----

# match by name (partial) or exact id
def search_student(term):
    students = file_operations.read_students()
    found = False
    for s in students:
        if term in s['name'] or term == s['id']:
            print(s)
            found = True
    if not found:
        print("Not found")


# match by name (partial) or exact code
def search_course(term):
    courses = file_operations.read_courses()
    found = False
    for c in courses:
        if term in c['name'] or term == c['code']:
            print(c)
            found = True
    if not found:
        print("Not found")


# ----- sort -----

# most credits first
def sort_students_by_credits():
    students = file_operations.read_students()
    regs = file_operations.read_registrations()
    courses = file_operations.read_courses()

    list_with_credits = []
    for s in students:
        s_regs = [r for r in regs if r['student_id'] == s['id']]
        s['total_credits'] = calculations.calculate_total_credits(s_regs, courses)
        list_with_credits.append(s)

    list_with_credits.sort(key=lambda x: x['total_credits'], reverse=True)
    for s in list_with_credits:
        print(f"{s['name']}: {s['total_credits']}")


# most popular first
def sort_courses_by_enrollment():
    courses = file_operations.read_courses()
    regs = file_operations.read_registrations()
    counts = calculations.count_students_per_course(regs)

    for c in courses:
        c['count'] = counts.get(c['code'], 0)

    courses.sort(key=lambda x: x['count'], reverse=True)
    for c in courses:
        print(f"{c['name']}: {c['count']}")


# ----- schedule -----

# all meetings of the student's courses
def display_student_schedule(student_id):
    regs = file_operations.read_registrations()
    courses = file_operations.read_courses()

    print("Schedule:")
    for r in regs:
        if r['student_id'] == student_id:
            for c in courses:
                if c['code'] == r['course_code']:
                    print(f"{c['code']} {c['name']} {c['days']} {c['time']}")


# ----- chart -----

# bar chart of students per course
def display_chart():
    regs = file_operations.read_registrations()
    counts = calculations.count_students_per_course(regs)
    if not counts:
        print("No data")
        return

    x_codes = list(counts.keys())
    y_values = list(counts.values())

    plt.bar(x_codes, y_values, color='blue')
    plt.xlabel('Course Code')
    plt.ylabel('Students Count')
    plt.title('Enrollment Statistics')
    plt.show()


# ----- admin tools -----

# console version of add course
def add_course():
    c = input("Code: ")
    n = input("Name: ")
    cr = int(input("Credits: "))
    d = input("Days: ")
    t = input("Time: ")
    cap = int(input("Capacity: "))

    courses = file_operations.read_courses()
    courses.append({'code': c, 'name': n, 'cred': cr, 'days': d, 'time': t, 'capacity': cap})
    file_operations.write_courses(courses)
    print("Course added")


# console version of the applications review
def review_applications():
    apps = file_operations.read_applications()
    for a in apps:
        if a['status'] == 'Pending':
            print(a)
            act = input("Accept/Reject (a/r): ")
            if act == 'a':
                a['status'] = 'Accepted'
            elif act == 'r':
                a['status'] = 'Rejected'
    file_operations.write_applications(apps)
    print("Reviews done")


# prints the most and least popular course
def generate_enrollment_report():
    regs = file_operations.read_registrations()
    counts = calculations.count_students_per_course(regs)
    stats = calculations.get_course_statistics(counts)
    print(f"Max: {stats[0]} Min: {stats[2]}")
