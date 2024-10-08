import sqlite3
import requests

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('Lab#3\lab3.db')
cursor = connection.cursor()

# Создание таблицы Posts
cursor.execute('''
CREATE TABLE IF NOT EXISTS Posts (
id INTEGER PRIMARY KEY,
userId INTEGER,
title TEXT NOT NULL,
body TEXT NOT NULL
)
''')

# Получение данных с сервера
get_response = requests.get("https://jsonplaceholder.typicode.com/posts").json()

# Запись данных в БД
for rec in get_response:
    cursor.execute('INSERT INTO Posts (userId, title, body) VALUES (?, ?, ?)', (rec["userId"], rec["title"], rec["body"]))
    print(f"Пост {rec["id"]}: {rec}")

# Чтение данных с БД
cursor.execute('''
SELECT *
FROM Posts               
''')

posts = cursor.fetchall()

for post in posts:
    print(f"Пост из БД {post}")

# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()
