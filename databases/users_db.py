import sqlite3 as sq

from databases import debts_db


async def db_users_start():
    global db, cur
    db = sq.connect("databases/users.db")
    cur = db.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS students(user_id TEXT PRIMARY KEY, identifier TEXT, full_name TEXT, "
                "groups TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS teachers(user_id TEXT PRIMARY KEY, identifier TEXT, full_name TEXT, "
                "groups TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS employee(user_id TEXT PRIMARY KEY, identifier TEXT, full_name TEXT)")
    db.commit()


async def add_user(identifier, user_id):
    student = cur.execute(
        "SELECT identifier FROM students WHERE identifier == '{key}'".format(key=identifier)).fetchone()
    teacher = cur.execute(
        "SELECT identifier FROM teachers WHERE identifier == '{key}'".format(key=identifier)).fetchone()
    employee = cur.execute(
        "SELECT identifier FROM employee WHERE identifier == '{key}'".format(key=identifier)).fetchone()

    if student:
        query = "UPDATE students SET user_id = ? WHERE identifier = ?"
        values = (user_id, identifier)
        cur.execute(query, values)
        await debts_db.add_user_id_students(await get_group(user_id), user_id)
        db.commit()

        return 1
    elif teacher:
        query = "UPDATE teacher SET user_id = ? WHERE identifier = ?"
        values = (user_id, identifier)
        cur.execute(query, values)
        db.commit()

        return 2
    elif employee:
        query = "UPDATE employee SET user_id = ? WHERE identifier = ?"
        values = (user_id, identifier)
        cur.execute(query, values)
        db.commit()

        return 3


async def add_student(student_id, full_name, group):
    """
    Добавление студента
    """
    sqlite_insert_student = """ INSERT INTO students
                            (user_id, full_name, groups)
                            VALUES
                            (?, ?, ?);"""
    data_tuple = (student_id, full_name, group)
    cur.execute(sqlite_insert_student, data_tuple)
    db.commit()


async def delete_student(student_id):
    """
    Удаление студента
    """

    cur.execute("DELETE FROM students WHERE user_id = ?", (student_id,))

    db.commit()


async def add_teacher(teacher_id, full_name, group):
    """
    Добавление куратора в таблицу
    """
    sqlite_insert_teacher = """ INSERT INTO teachers
                               (user_id, full_name, groups)
                               VALUES
                               (?, ?, ?);"""
    data_tuple = (teacher_id, full_name, group)
    cur.execute(sqlite_insert_teacher, data_tuple)
    db.commit()


async def check_identifier(identifier) -> bool:
    """
    Проверка на зарегестрированность в системе
    """
    student = cur.execute(
        "SELECT identifier FROM students WHERE identifier == '{key}'".format(key=identifier)).fetchone()
    teacher = cur.execute(
        "SELECT identifier FROM teachers WHERE identifier == '{key}'".format(key=identifier)).fetchone()
    employee = cur.execute(
        "SELECT identifier FROM employee WHERE identifier == '{key}'".format(key=identifier)).fetchone()
    db.commit()

    if not student and not teacher and not employee:
        return False
    else:
        return True


async def check_registration(user_id) -> bool:
    """
    Проверка на регистрацию
    """

    student = cur.execute("SELECT user_id FROM students WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    teacher = cur.execute("SELECT user_id FROM teachers WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    employee = cur.execute("SELECT user_id FROM employee WHERE user_id == '{key}'".format(key=user_id)).fetchone()
    db.commit()

    if not student and not teacher and not employee:
        return False
    else:
        return True


async def get_list_students(teacher_id) -> list:
    """
    Получние списка всех студентов
    """
    group = cur.execute(
        "SELECT groups FROM teachers WHERE user_id = ?", (teacher_id,)).fetchone()

    list_students = cur.execute(
        "SELECT full_name FROM students WHERE groups IN ({})".format(','.join('?' * len(group))),
        group).fetchall()
    db.commit()

    return list_students


async def get_student_of_number(teacher_id, number) -> int:
    """
    Получние id студента по номеру из списка
    """
    group = cur.execute(
        "SELECT groups FROM teachers WHERE user_id = ?", (teacher_id,)).fetchone()[0]
    list_students = cur.execute(
        "SELECT user_id FROM students WHERE groups = ?", (group,)).fetchall()
    user_student = list_students[int(number) - 1][0]
    db.commit()

    return user_student


async def get_group(user_id) -> str:
    """
    Получение группы через id
    """
    try:
        group = cur.execute(
            "SELECT groups FROM teachers WHERE user_id = ?", (user_id,)).fetchone()[0]
        db.commit()
        return group
    except TypeError:
        group = cur.execute(
            "SELECT groups FROM students WHERE user_id = ?", (user_id,)).fetchone()[0]
        db.commit()
        return group


async def get_name_student(student_id):
    """
    Получение имени студента через id
    """
    name = cur.execute("SELECT full_name FROM students WHERE user_id = ?", (student_id,)).fetchone()[0]
    return name


async def get_teacher_id(student_id):
    """
    Получение id куратора
    """
    group = await get_group(student_id)
    teacher_id = cur.execute(
        "SELECT user_id FROM teachers WHERE groups = ?", (group,)).fetchone()[0]
    return teacher_id


async def rename_student(student_id, edit_name):
    """
    Изменение в таблице имени студента
    """
    query = "UPDATE students SET full_name = ? WHERE user_id = ?"
    cur.execute(query, (edit_name, student_id,))
    db.commit()
