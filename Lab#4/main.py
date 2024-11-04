import sys
from PyQt5 import QtWidgets, QtSql, QtCore, QtGui
#подключение к БД
def create_connection():
    DB = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    DB.setDatabaseName('lab#4/posts.db')
    if not DB.open():
        QtWidgets.QMessageBox.critical(None, "Ошибка!", "Не удалось подключиться к базе данных.")
        return False
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




app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()


window.setWindowTitle("Изменение данных в БД с постами")
window.setWindowIcon(QtGui.QIcon("Lab#4/icon.png"))
window.resize(1280, 720)

search_layout = QtWidgets.QHBoxLayout()

search_icon = QtWidgets.QLabel()
icon_pixmap = QtGui.QPixmap("lab#4/search.png")
scaled_icon = icon_pixmap.scaled(16, 16, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
search_icon.setPixmap(scaled_icon)

search_line = QtWidgets.QLineEdit()
search_line.setPlaceholderText("Поиск по названию поста...")

search_layout.addWidget(search_icon)
search_layout.addWidget(search_line)

main_table = QtWidgets.QTableView()

postUserID_text = QtWidgets.QLineEdit()
postUserID_text.setPlaceholderText("Введите ID пользователя...")
postTitle_text = QtWidgets.QLineEdit()
postTitle_text.setPlaceholderText("Введите Название поста...")
postBody_text = QtWidgets.QLineEdit()
postBody_text.setPlaceholderText("Введите Содержание поста...")

add_btn = QtWidgets.QPushButton("Добавить")
add_btn.setIcon(QtGui.QIcon("lab#4/add.png"))
update_btn = QtWidgets.QPushButton("Обновить")
update_btn.setIcon(QtGui.QIcon("lab#4/update.png"))
del_btn = QtWidgets.QPushButton("Удалить")
del_btn.setIcon(QtGui.QIcon("lab#4/delete.png"))

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

horizontal_layout = QtWidgets.QHBoxLayout()
horizontal_layout.addLayout(text_box)
horizontal_layout.addLayout(btn_box)

main_box.addWidget(main_table)
main_box.addLayout(horizontal_layout)


window.setLayout(main_box)

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

window.show()
sys.exit(app.exec())
