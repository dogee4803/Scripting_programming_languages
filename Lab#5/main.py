import sys
import time
import json
import threading
import requests
from PyQt5 import QtWidgets, QtSql, QtCore, QtGui
from PyQt5.QtCore import QTimer, pyqtSignal, QThread

#подключение к БД
def create_connection():
    DB = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    DB.setDatabaseName('posts.db')  # Используем относительный путь
    if not DB.open():
        QtWidgets.QMessageBox.critical(None, "Ошибка!", "Не удалось подключиться к базе данных.")
        return False
    
    # Создаем таблицу, если она не существует
    query = QtSql.QSqlQuery()
    query.exec_("""\
        CREATE TABLE IF NOT EXISTS posts (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID TEXT,
            Title TEXT,
            Body TEXT
        )
    """)
    
    return True

def add_record():
    row = main_model.rowCount()
    main_model.insertRow(row)
    main_model.setData(main_model.index(row, 1), postUserID_text.text())
    main_model.setData(main_model.index(row, 2), postTitle_text.text())
    main_model.setData(main_model.index(row, 3), postBody_text.text())
    if not main_model.submitAll():
        QtWidgets.QMessageBox.warning(None, "Ошибка!", "Не удалось добавить запись.")
    else:
        postUserID_text.clear()
        postTitle_text.clear()
        postBody_text.clear()
        main_model.select()

def display_selected_row(index):
    if index.isValid():
        user_id = str(main_model.data(main_model.index(index.row(), 1)))
        title = str(main_model.data(main_model.index(index.row(), 2)))
        body = str(main_model.data(main_model.index(index.row(), 3)))

        postUserID_text.setText(user_id)
        postTitle_text.setText(title)
        postBody_text.setText(body)

def update_record(index):
    main_model.setData(main_model.index(index.row(), 1), postUserID_text.text())
    main_model.setData(main_model.index(index.row(), 2), postTitle_text.text())
    main_model.setData(main_model.index(index.row(), 3), postBody_text.text())

    if not main_model.submitAll():
        QtWidgets.QMessageBox.warning(None, "Ошибка!", "Не удалось обновить запись.")
    else:
        postUserID_text.clear()
        postTitle_text.clear()
        postBody_text.clear()
        main_model.select()

def delete_record():
    index = main_table.selectionModel().currentIndex()
    if index.isValid():
        main_model.removeRow(index.row())
        if not main_model.submitAll():
            QtWidgets.QMessageBox.warning(None, "Ошибка!", "Не удалось удалить запись.")
        else:
            postUserID_text.clear()
            postTitle_text.clear()
            postBody_text.clear()
            main_model.select()

def search_post():
    search_text = search_line.text()
    filter_str = f"Title LIKE '%{search_text}%'"
    main_model.setFilter(filter_str)
    main_model.select()

class DataFetcherThread(QThread):
    data_fetched = pyqtSignal(list)
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            response = requests.get('https://jsonplaceholder.typicode.com/posts')
            if response.status_code != 200:
                self.error_occurred.emit(f"Ошибка получения данных: {response.status_code}")
                return
                
            posts = response.json()
            
            # Имитация длительной загрузки
            for i in range(101):
                time.sleep(0.05)  # Задержка 50мс
                self.progress_updated.emit(i)
            
            self.data_fetched.emit(posts)
        except Exception as e:
            self.error_occurred.emit(f"Ошибка: {str(e)}")

class DataSaverThread(QThread):
    save_completed = pyqtSignal()
    progress_updated = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, posts):
        super().__init__()
        self.posts = posts

    def run(self):
        try:
            DB = QtSql.QSqlDatabase.addDatabase('QSQLITE', 'save_connection')
            DB.setDatabaseName('posts.db')
            if DB.open():
                query = QtSql.QSqlQuery(DB)
                
                total = len(self.posts)
                
                for i, post in enumerate(self.posts):
                    # Проверяем существование записи
                    check_query = QtSql.QSqlQuery(DB)
                    check_query.prepare("SELECT ID FROM posts WHERE UserID = ? AND Title = ? AND Body = ?")
                    check_query.addBindValue(str(post['userId']))
                    check_query.addBindValue(post['title'])
                    check_query.addBindValue(post['body'])
                    check_query.exec_()
                    
                    # Если запись не существует, добавляем её
                    if not check_query.next():
                        query.prepare("""\
                            INSERT INTO posts (UserID, Title, Body)
                            VALUES (?, ?, ?)
                        """)
                        query.addBindValue(str(post['userId']))
                        query.addBindValue(post['title'])
                        query.addBindValue(post['body'])
                        query.exec_()
                    
                    # Имитация длительного сохранения
                    time.sleep(0.05)
                    progress = int((i + 1) / total * 100)
                    self.progress_updated.emit(progress)
                
                DB.close()
                self.save_completed.emit()
            else:
                self.error_occurred.emit("Не удалось открыть базу данных")
        except Exception as e:
            self.error_occurred.emit(f"Ошибка сохранения: {str(e)}")


app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()

window.setWindowTitle("Асинхронная работа с постами")
window.setWindowIcon(QtGui.QIcon("icon.png"))
window.resize(1280, 720)

# Создаем компоненты интерфейса
search_layout = QtWidgets.QHBoxLayout()
search_icon = QtWidgets.QLabel()
icon_pixmap = QtGui.QPixmap("search.png")
scaled_icon = icon_pixmap.scaled(16, 16, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
search_icon.setPixmap(scaled_icon)

search_line = QtWidgets.QLineEdit()
search_line.setPlaceholderText("Поиск по названию поста...")

search_layout.addWidget(search_icon)
search_layout.addWidget(search_line)

# Создаем кнопку загрузки данных и прогресс-бар
load_btn = QtWidgets.QPushButton("Загрузить данные")
load_btn.setIcon(QtGui.QIcon("download.png"))
progress_bar = QtWidgets.QProgressBar()
progress_bar.setVisible(False)
status_label = QtWidgets.QLabel("")

# Добавляем новые компоненты в интерфейс
load_layout = QtWidgets.QHBoxLayout()
load_layout.addWidget(load_btn)
load_layout.addWidget(progress_bar)
load_layout.addWidget(status_label)

main_table = QtWidgets.QTableView()

postUserID_text = QtWidgets.QLineEdit()
postUserID_text.setPlaceholderText("Введите ID пользователя...")
postTitle_text = QtWidgets.QLineEdit()
postTitle_text.setPlaceholderText("Введите Название поста...")
postBody_text = QtWidgets.QLineEdit()
postBody_text.setPlaceholderText("Введите Содержание поста...")

add_btn = QtWidgets.QPushButton("Добавить")
add_btn.setIcon(QtGui.QIcon("add.png"))
update_btn = QtWidgets.QPushButton("Обновить")
update_btn.setIcon(QtGui.QIcon("update.png"))
del_btn = QtWidgets.QPushButton("Удалить")
del_btn.setIcon(QtGui.QIcon("delete.png"))

main_box = QtWidgets.QVBoxLayout()
btn_box = QtWidgets.QHBoxLayout()
text_box = QtWidgets.QHBoxLayout()

btn_box.addWidget(add_btn)
btn_box.addWidget(update_btn)
btn_box.addWidget(del_btn)

text_box.addWidget(postUserID_text)
text_box.addWidget(postTitle_text)
text_box.addWidget(postBody_text)

main_box.addLayout(search_layout)
main_box.addLayout(load_layout)

horizontal_layout = QtWidgets.QHBoxLayout()
horizontal_layout.addLayout(text_box)
horizontal_layout.addLayout(btn_box)

main_box.addWidget(main_table)
main_box.addLayout(horizontal_layout)

# Инициализация потоков и таймера
data_fetcher = DataFetcherThread()
data_saver = None
update_timer = QTimer()
update_timer.setInterval(10000)  # 10 секунд

def on_load_data():
    load_btn.setEnabled(False)
    progress_bar.setVisible(True)
    progress_bar.setValue(0)
    status_label.setText("Загрузка данных...")
    data_fetcher.start()

def on_data_fetched(posts):
    global data_saver
    status_label.setText("Сохранение данных...")
    progress_bar.setValue(0)
    data_saver = DataSaverThread(posts)
    data_saver.progress_updated.connect(on_save_progress)
    data_saver.save_completed.connect(on_save_completed)
    data_saver.error_occurred.connect(on_error)
    data_saver.start()

def on_fetch_progress(value):
    progress_bar.setValue(value)

def on_save_progress(value):
    progress_bar.setValue(value)

def on_save_completed():
    load_btn.setEnabled(True)
    progress_bar.setVisible(False)
    status_label.setText("Данные успешно загружены и сохранены!")
    main_model.select()

def on_error(error_message):
    load_btn.setEnabled(True)
    progress_bar.setVisible(False)
    status_label.setText(error_message)
    QtWidgets.QMessageBox.critical(None, "Ошибка!", error_message)

def check_updates():
    if not data_fetcher.isRunning() and (data_saver is None or not data_saver.isRunning()):
        status_label.setText("Проверка обновлений...")
        data_fetcher.start()

# Подключаем сигналы
load_btn.clicked.connect(on_load_data)
data_fetcher.data_fetched.connect(on_data_fetched)
data_fetcher.progress_updated.connect(on_fetch_progress)
data_fetcher.error_occurred.connect(on_error)
update_timer.timeout.connect(check_updates)

# Настраиваем базу данных и модель
connection = create_connection()
main_model = QtSql.QSqlTableModel()
main_model.setTable("posts")
main_model.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
main_model.select()

main_model.setHeaderData(0, QtCore.Qt.Horizontal, "ID")
main_model.setHeaderData(1, QtCore.Qt.Horizontal, "User ID")
main_model.setHeaderData(2, QtCore.Qt.Horizontal, "Title")
main_model.setHeaderData(3, QtCore.Qt.Horizontal, "Body")

add_btn.clicked.connect(add_record)
update_btn.clicked.connect(lambda: update_record(selection_model.currentIndex()))
del_btn.clicked.connect(delete_record)
search_line.textChanged.connect(search_post)

main_table.setModel(main_model)
selection_model = main_table.selectionModel()
selection_model.currentChanged.connect(display_selected_row)

# Запускаем таймер
update_timer.start()

window.setLayout(main_box)
window.show()
sys.exit(app.exec_())
