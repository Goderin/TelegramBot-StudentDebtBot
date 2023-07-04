import sqlite3 as sq

from databases import users_db


async def db_debts_start():
    global db, cur
    db = sq.connect("databases/debts.db")
    cur = db.cursor()

    db.commit()


async def add_user_id_students(group, user_id):
    """
    Добавления id студента в таблицу его группы
    """
    # получаем список столбцов в таблице
    num_columns = len(cur.execute('PRAGMA table_info("{}")'.format(group)).fetchall())
    query = 'INSERT INTO "{}" VALUES (?{})'.format(group, ', ?' * (num_columns - 1))
    cur.execute(query, (user_id,) + (None,) * (num_columns - 1))
    db.commit()


async def delete_student(student_id, teacher_id):
    """
    Удаление выбранного студента
    """

    group = await users_db.get_group(teacher_id)
    cur.execute("DELETE FROM '{}' WHERE user_id = ?".format(group), (student_id,))

    db.commit()


async def is_table_exists(group) -> bool:
    """
    Проверка на существование в базе данных таблицы с именем группы
    """
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_names = cur.fetchall()
    db.commit()
    # Проверяем наличие таблицы с заданным именем
    if (group,) in table_names:
        return True
    else:
        return False


async def get_not_null_debts_student_text(teacher_id, student_id) -> str:
    """
    Получение списка всех не пустых задолженностей для выбранного студента
    """
    group = await users_db.get_group(teacher_id)

    # Получаем названия столбцов таблицы
    query = "PRAGMA table_info('{}')".format(group)
    cur.execute(query)
    columns = cur.fetchall()

    # Получаем значения ячеек для заданного user_id
    cur.execute("SELECT * FROM '{}' WHERE user_id=?".format(group), (student_id,))
    rows = cur.fetchall()

    # Формируем ответ для пользователя
    response = ""
    count = 0
    for row in rows:
        for j in range(1, len(columns)):
            column_name = columns[j][1]
            column_value = row[j]
            if column_value is not None:
                count = count + 1
                response += f"{count}. "
                response += f"<b>{column_name}:</b>\n" \
                            f"<i>{column_value}</i>\n"
        response += "\n"

    if count == 0:
        response = ""

    db.commit()

    return response


async def get_not_null_debt_of_number(teacher_id, student_id, column_number) -> str:
    """
    Получение названия задолженности по номеру  из списка заполенных задолженностей
    для выбранного студента
    Вовращает одно навзание
    """
    group = await users_db.get_group(teacher_id)

    # Получаем названия столбцов таблицы
    query = "PRAGMA table_info('{}')".format(group)
    cur.execute(query)
    columns = cur.fetchall()

    # Получаем значения ячеек для заданного user_id
    cur.execute("SELECT * FROM '{}' WHERE user_id=?".format(group), (student_id,))
    rows = cur.fetchall()

    not_empty_columns = []
    # Заполняем список названиями не пустых предметов
    for row in rows:
        for j in range(1, len(columns)):
            column_name = columns[j][1]
            column_value = row[j]
            if column_value is not None:
                not_empty_columns.append(column_name)

    return not_empty_columns[int(column_number) - 1]


async def get_all_debts_student_text(teacher_id) -> str:
    """
    Получение списка всех задолженностей в таблице
    """
    group = await users_db.get_group(teacher_id)

    # Получаем названия столбцов таблицы
    query = "PRAGMA table_info('{}')".format(group)
    cur.execute(query)
    columns = cur.fetchall()

    count = 1
    response = ""
    for column in range(1, len(columns)):
        column_name = columns[column][1]
        response += f"{count}.{column_name}\n"
        count += 1
    return response


async def get_all_debt_of_number(teacher_id, student_id, column_number):
    """
    Получение названия задолженности из списка всех задолженностей по номеру
    Вовращает одно навзание
    """
    group = await users_db.get_group(teacher_id)

    # Получаем названия столбцов таблицы
    query = "PRAGMA table_info('{}')".format(group)
    cur.execute(query)
    columns = cur.fetchall()

    # Получаем значения ячеек для заданного user_id
    cur.execute("SELECT * FROM '{}' WHERE user_id=?".format(group), (student_id,))
    rows = cur.fetchall()

    all_columns = []
    # Заполняем список названиями не пустых предметов
    for j in range(1, len(columns)):
        column_name = columns[j][1]
        all_columns.append(column_name)

    return all_columns[int(column_number) - 1]


async def delete_debt_of_name(name_debt, teacher_id, student_id):
    """
    Удаление задолженности по имени
    """
    group = await users_db.get_group(teacher_id)

    query = "UPDATE '{}' SET '{}' = NULL WHERE user_id = ?".format(group, name_debt)
    cur.execute(query, (student_id,))
    db.commit()


async def update_debt_of_name(name_debt, teacher_id, student_id, text):
    """
    Обновление задолженности в таблице по имени
    """
    group = await users_db.get_group(teacher_id)
    query = "UPDATE '{}' SET '{}' = ? WHERE user_id = ?".format(group, name_debt)
    cur.execute(query, (text, student_id,))
    db.commit()


async def add_debt_of_name(name_debt, teacher_id, student_id, text):
    """
    Добавление новой задолженности либо присвоение к уже существующей
    """
    group = await users_db.get_group(teacher_id)

    # Получаем названия столбцов таблицы
    query = "PRAGMA table_info('{}')".format(group)
    cur.execute(query)
    columns = cur.fetchall()

    # Получаем значения ячеек для заданного user_id
    cur.execute("SELECT * FROM '{}' WHERE user_id=?".format(group), (student_id,))
    rows = cur.fetchall()

    edit_text = ""
    # ищем столбец по название
    for row in rows:
        for j in range(1, len(columns)):
            column_name = columns[j][1]
            column_value = row[j]
            if column_name == name_debt:
                    if column_value is None:
                        edit_text = "" + text
                    else:
                        edit_text += column_value + "\n" + text

    await update_debt_of_name(name_debt, teacher_id, student_id, edit_text)