# file_operations.py
# reads and writes the text files inside data/ (one line = one record, fields split by "|")
#
#   students.txt       id | name | program | year | password
#   courses.txt        code | name | credits | days | time | capacity
#   registrations.txt  student_id | course_code
#   applications.txt   id | name | email | phone | status
#   notifications.txt  application_id | message | status
#
# the other files never open these directly, they use the read_/write_ functions below
# which work with lists of dicts
import os

# ----- settings -----

# data folder lives next to the code
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SEP = "|"  # not "," because names/days can contain commas

STUDENTS_FILE = "students.txt"
COURSES_FILE = "courses.txt"
REGISTRATIONS_FILE = "registrations.txt"
APPLICATIONS_FILE = "applications.txt"
NOTIFICATIONS_FILE = "notifications.txt"


# ----- core helpers -----

def _path(name):
    return os.path.join(DATA_DIR, name)


# returns every line as a list of fields
# missing file -> empty list, broken lines are skipped
# so one bad line doesn't crash the app
#
def _read(name, min_fields):
    rows = []
    if os.path.exists(_path(name)):
        with open(_path(name), "r", encoding="utf-8") as f:
            for line in f:
                fields = line.strip().split(SEP)
                if len(fields) >= min_fields:
                    rows.append(fields)
    return rows


# save rows to a data file
# write to a .tmp file first and then replace the real one, so a
# crash while saving can't leave a half-written file
#
def _write(name, rows):
    tmp = _path(name) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for row in rows:
            # user text can't contain the separator or newlines
            f.write(SEP.join(str(v).replace(SEP, "/").replace("\n", " ") for v in row) + "\n")
    os.replace(tmp, _path(name))


# int() that doesn't crash on bad values
def _to_int(text, default=0):
    try:
        return int(text)
    except ValueError:
        return default


# ----- students -----

def read_students():
    return [{'id': p[0], 'name': p[1], 'prog': p[2], 'year': p[3], 'pass': p[4]}
            for p in _read(STUDENTS_FILE, 5)]


def write_students(students):
    _write(STUDENTS_FILE, [[s['id'], s['name'], s['prog'], s['year'], s['pass']] for s in students])


# ----- courses -----

def read_courses():
    return [{'code': p[0], 'name': p[1], 'cred': _to_int(p[2]), 'days': p[3],
             'time': p[4], 'capacity': _to_int(p[5])}
            for p in _read(COURSES_FILE, 6)]


def write_courses(courses):
    _write(COURSES_FILE, [[c['code'], c['name'], c['cred'], c['days'], c['time'], c['capacity']]
                          for c in courses])


# ----- registrations -----

def read_registrations():
    return [{'student_id': p[0], 'course_code': p[1]} for p in _read(REGISTRATIONS_FILE, 2)]


def write_registrations(regs):
    _write(REGISTRATIONS_FILE, [[r['student_id'], r['course_code']] for r in regs])


# True if the registration existed and was removed
def drop_course(std_id, course_code):
    regs = read_registrations()
    new_regs = [r for r in regs if not (r['student_id'] == std_id and r['course_code'] == course_code)]
    if len(regs) != len(new_regs):
        write_registrations(new_regs)
        return True
    return False


# ----- applications -----

def read_applications():
    return [{'id': p[0], 'name': p[1], 'email': p[2], 'phone': p[3], 'status': p[4]}
            for p in _read(APPLICATIONS_FILE, 5)]


def write_applications(apps):
    _write(APPLICATIONS_FILE, [[a['id'], a['name'], a['email'], a['phone'], a['status']] for a in apps])


# new applications start as Pending, ids start at 1001
def submit_application(name, email, phone):
    apps = read_applications()
    new_id = str(len(apps) + 1001)
    apps.append({'id': new_id, 'name': name, 'email': email, 'phone': phone, 'status': 'Pending'})
    write_applications(apps)
    return new_id


def notify_applicant(app_id, msg):
    with open(_path(NOTIFICATIONS_FILE), "a", encoding="utf-8") as f:
        f.write(f"{app_id}{SEP}{msg}{SEP}New\n")


# ----- first-run setup -----

# create data/ and any missing file with starter data so
# the app doesn't crash on first run (existing files are kept)
#
def initialize_files():
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(_path(STUDENTS_FILE)):
        write_students([
            {'id': '202507440', 'name': 'Ahmed Amir Ibrahim', 'prog': 'CS', 'year': '2025', 'pass': 'pass123'},
            {'id': '202506915', 'name': 'Ahmed Hisham Saad', 'prog': 'CS', 'year': '2025', 'pass': 'pass456'},
            {'id': '202507258', 'name': 'Reda Mahmoud Ali', 'prog': 'CS', 'year': '2025', 'pass': 'pass789'},
        ])

    if not os.path.exists(_path(COURSES_FILE)):
        # rows with the same code are one course (lecture + lab, Sec1 + Sec2),
        # registering the code registers all of them
        write_courses([
            {'code': 'CSAI 100', 'name': 'Introduction to Computational Sciences and AI', 'cred': 1, 'days': 'Sun', 'time': '3:00-4:00', 'capacity': 50},
            {'code': 'CSAI 101', 'name': 'Fundamentals of Programming and Computer Science', 'cred': 2, 'days': 'Wed', 'time': '12:00-2:00', 'capacity': 50},
            {'code': 'CSAI 101', 'name': 'Fundamentals of Programming and Computer Science Lab', 'cred': 0, 'days': 'Thu', 'time': '08:00-10:00', 'capacity': 50},
            {'code': 'CSAI 102', 'name': 'Digital Logic and Computer Architecture', 'cred': 3, 'days': 'Tue', 'time': '2:00-4:00', 'capacity': 50},
            {'code': 'CSAI 102', 'name': 'Digital Logic and Computer Architecture Lab', 'cred': 0, 'days': 'Mon', 'time': '10:00-12:00', 'capacity': 50},
            {'code': 'CSAI 252', 'name': 'Introduction to Computer Networks', 'cred': 3, 'days': 'Wed', 'time': '2:00-4:00', 'capacity': 50},
            {'code': 'CSAI 252', 'name': 'Introduction to Computer Networks Lab', 'cred': 0, 'days': 'Mon', 'time': '12:00-2:00', 'capacity': 50},
            {'code': 'ENGL 002', 'name': 'Remedial English Sec1', 'cred': 0, 'days': 'Sun', 'time': '1:00-3:00', 'capacity': 50},
            {'code': 'ENGL 002', 'name': 'Remedial English Sec2', 'cred': 0, 'days': 'Thu', 'time': '10:00-12:00', 'capacity': 50},
            {'code': 'ENGL 003', 'name': 'Remedial English Sec1', 'cred': 0, 'days': 'Sun', 'time': '1:00-3:00', 'capacity': 50},
            {'code': 'ENGL 003', 'name': 'Remedial English Sec2', 'cred': 0, 'days': 'Thu', 'time': '10:00-12:00', 'capacity': 50},
            {'code': 'ENGL 004', 'name': 'Remedial English Sec1', 'cred': 0, 'days': 'Sun', 'time': '1:00-3:00', 'capacity': 50},
            {'code': 'ENGL 004', 'name': 'Remedial English Sec2', 'cred': 0, 'days': 'Thu', 'time': '10:00-12:00', 'capacity': 50},
            {'code': 'MATH 103', 'name': 'Calculus for Computational Sciences', 'cred': 3, 'days': 'Sun', 'time': '08:00-10:00', 'capacity': 50},
            {'code': 'MATH 103', 'name': 'Calculus for Computational Sciences Tut1', 'cred': 0, 'days': 'Tue', 'time': '12:00-2:00', 'capacity': 50},
            {'code': 'MATH 103', 'name': 'Calculus for Computational Sciences Tut2', 'cred': 0, 'days': 'Wed', 'time': '10:00-12:00', 'capacity': 50},
            {'code': 'SCH 163', 'name': 'Sustainability Social and Ethical Issues in Computing', 'cred': 2, 'days': 'Tue', 'time': '08:00-10:00', 'capacity': 50},
        ])

    if not os.path.exists(_path(REGISTRATIONS_FILE)):
        write_registrations([
            {'student_id': '202507440', 'course_code': 'CSAI 101'},
            {'student_id': '202507440', 'course_code': 'MATH 103'},
            {'student_id': '202506915', 'course_code': 'CSAI 101'},
        ])

    for name in (APPLICATIONS_FILE, NOTIFICATIONS_FILE):
        if not os.path.exists(_path(name)):
            open(_path(name), "w", encoding="utf-8").close()
