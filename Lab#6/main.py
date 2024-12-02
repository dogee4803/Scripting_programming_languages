import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QComboBox, QTextEdit, QFileDialog, 
                           QLabel, QHBoxLayout, QLineEdit, QSizePolicy)
from matplotlib.figure import Figure

class DataAnalyzerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Анализатор данных')
        self.setGeometry(100, 100, 1200, 800)
        
        # Инициализация данных
        self.df = None
        
        # Создание главного виджета и компоновки
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Создание элементов управления
        controls_layout = QHBoxLayout()
        
        # Левая панель управления
        left_panel = QVBoxLayout()
        
        # Кнопка загрузки данных
        self.load_button = QPushButton('Загрузить CSV файл')
        self.load_button.clicked.connect(self.load_data)
        left_panel.addWidget(self.load_button)
        
        # Выбор типа графика
        self.graph_type = QComboBox()
        self.graph_type.addItems(['Линейный график', 'Гистограмма', 'Круговая диаграмма'])
        self.graph_type.currentIndexChanged.connect(self.update_plot)
        left_panel.addWidget(QLabel('Выберите тип графика:'))
        left_panel.addWidget(self.graph_type)
        
        # Ручной ввод данных
        manual_entry_layout = QHBoxLayout()
        self.value_input = QLineEdit()
        self.add_value_button = QPushButton('Добавить значение')
        self.add_value_button.clicked.connect(self.add_manual_value)
        manual_entry_layout.addWidget(QLabel('Добавить значение:'))
        manual_entry_layout.addWidget(self.value_input)
        manual_entry_layout.addWidget(self.add_value_button)
        left_panel.addLayout(manual_entry_layout)
        
        # Отображение статистики
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMinimumHeight(400)  # Увеличиваем минимальную высоту
        self.stats_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Разрешаем расширение во всех направлениях
        left_panel.addWidget(QLabel('Статистика:'))
        left_panel.addWidget(self.stats_display)
        
        # Добавление левой панели в основной layout
        controls_layout.addLayout(left_panel)
        
        # Создание области для графика matplotlib
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        controls_layout.addWidget(self.canvas)
        
        # Добавление layout с элементами управления в главный layout
        layout.addLayout(controls_layout)
        
    def load_data(self):
        try:
            file_path = "data.csv"  # Использование предопределенного файла data.csv
            self.df = pd.read_csv(file_path)
            # Преобразование столбца Date в datetime и затем в строковый формат
            self.df['Date'] = pd.to_datetime(self.df['Date']).dt.strftime('%Y-%m-%d')
            self.update_statistics()
            self.update_plot()
        except Exception as e:
            self.stats_display.setText(f"Ошибка загрузки данных: {str(e)}")
    
    def update_statistics(self):
        if self.df is not None:
            stats = f"Статистика набора данных:\n\n"
            stats += f"Количество строк: {len(self.df)}\n"
            stats += f"Количество столбцов: {len(self.df.columns)}\n\n"
            
            for column in self.df.columns:
                if pd.api.types.is_numeric_dtype(self.df[column]):
                    stats += f"{column}:\n"
                    stats += f"  Минимум: {self.df[column].min()}\n"
                    stats += f"  Максимум: {self.df[column].max()}\n"
                    stats += f"  Среднее: {self.df[column].mean():.2f}\n\n"
            
            self.stats_display.setText(stats)
    
    def update_plot(self):
        if self.df is None:
            return
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        graph_type = self.graph_type.currentText()
        
        try:
            if graph_type == 'Линейный график':
                ax.plot(self.df['Date'], self.df['Value1'])
                ax.set_title('Линейный график: Дата и Значение1')
                ax.set_xlabel('Дата')
                ax.set_ylabel('Значение1')
            
            elif graph_type == 'Гистограмма':
                ax.bar(self.df['Date'], self.df['Value2'])
                ax.set_title('Гистограмма: Дата и Значение2')
                ax.set_xlabel('Дата')
                ax.set_ylabel('Значение2')
                # Поворот подписей дат для лучшей читаемости
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            elif graph_type == 'Круговая диаграмма':
                category_counts = self.df['Category'].value_counts()
                ax.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%')
                ax.set_title('Распределение категорий')
            
            self.figure.tight_layout()
            self.canvas.draw()
        
        except Exception as e:
            self.stats_display.setText(f"Ошибка обновления графика: {str(e)}")
    
    def add_manual_value(self):
        try:
            new_value = float(self.value_input.text())
            current_date = pd.Timestamp.now().strftime('%Y-%m-%d')
            
            # Определяем, какое значение обновлять в зависимости от типа графика
            graph_type = self.graph_type.currentText()
            
            new_row = pd.DataFrame({
                'Date': [current_date],
                'Value1': [new_value if graph_type == 'Линейный график' else 0],
                'Value2': [new_value if graph_type == 'Гистограмма' else 0],
                'Category': ['Ручной ввод']
            })
            
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.update_statistics()
            self.update_plot()
            self.value_input.clear()
        except ValueError:
            self.stats_display.setText("Пожалуйста, введите корректное число")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataAnalyzerApp()
    window.show()
    sys.exit(app.exec_())
