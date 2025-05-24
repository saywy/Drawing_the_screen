import sys
import os
import csv
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QFileDialog, QLineEdit,
                             QDialog, QColorDialog, QSpinBox, QListWidget,
                             QMessageBox, QInputDialog, QCheckBox, QComboBox)
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.image_path = None
        self.save_path = None
        self.labels = []  # Список для хранения параметров надписей
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.labels_list = QListWidget()
        self.labels_list.itemDoubleClicked.connect(self.edit_label)
        self.initUI()

    def initUI(self):
        # Кнопки
        self.select_image_btn = QPushButton("Выбрать фотографию")
        self.select_image_btn.clicked.connect(self.select_image)
        self.select_save_path_btn = QPushButton("Выбрать папку для сохранения")
        self.select_save_path_btn.clicked.connect(self.select_save_path)
        self.create_label_btn = QPushButton("Создать надпись")
        self.create_label_btn.clicked.connect(self.create_label)
        self.save_template_btn = QPushButton("Сохранить шаблон")
        self.save_template_btn.clicked.connect(self.save_template)
        self.load_template_btn = QPushButton("Загрузить шаблон")
        self.load_template_btn.clicked.connect(self.load_template)
        self.save_btn = QPushButton("Сохранить скриншоты")
        self.save_btn.clicked.connect(self.save_screenshots)
        self.preview_btn = QPushButton("Предпросмотр")
        self.preview_btn.clicked.connect(self.show_preview)

        # Поле ввода количества скриншотов
        self.screenshot_count_label = QLabel("Количество скриншотов:")
        self.screenshot_count_input = QSpinBox()
        self.screenshot_count_input.setValue(1)

        # Индикаторы выбора
        self.image_selected_label = QLabel("")
        self.save_path_selected_label = QLabel("")

        # Выпадающий список шаблонов
        self.templates_list = QListWidget()
        self.load_templates()

        # Выбор темы
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Светлая", "Темная", "Синяя", "Зеленая"])
        self.theme_combo.currentIndexChanged.connect(self.apply_theme)

        # Компоновка
        hbox = QHBoxLayout()
        hbox.addWidget(self.screenshot_count_label)
        hbox.addWidget(self.screenshot_count_input)

        vbox = QVBoxLayout()
        vbox.addWidget(self.select_image_btn)
        vbox.addWidget(self.image_selected_label)
        vbox.addWidget(self.select_save_path_btn)
        vbox.addWidget(self.save_path_selected_label)
        vbox.addWidget(self.create_label_btn)
        vbox.addWidget(self.labels_list)
        vbox.addLayout(hbox)
        vbox.addWidget(self.save_template_btn)
        vbox.addWidget(self.load_template_btn)
        vbox.addWidget(self.templates_list)
        vbox.addWidget(self.preview_btn)  # Кнопка предпросмотра
        vbox.addWidget(self.save_btn)
        vbox.addWidget(self.theme_combo)  # Выбор темы
        # vbox.addWidget(self.image_label)  # Убираем из главного окна

        self.setLayout(vbox)
        self.setWindowTitle("Image Text App")
        self.setGeometry(300, 300, 600, 600)

        # Изначально применяем светлую тему
        self.apply_theme(0)

    def select_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "",
                                                  "Images (*.png *.jpg *.jpeg *.bmp *.bmp);;All Files (*)", options=options)
        if file_path:
            self.image_path = file_path
            self.image_selected_label.setText("Фотография выбрана!")
            self.image_selected_label.setStyleSheet("color: green;")

    def select_save_path(self):
        options = QFileDialog.Options()
        save_path = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения", "", options=options)
        if save_path:
            self.save_path = save_path
            self.save_path_selected_label.setText("Папка выбрана!")
            self.save_path_selected_label.setStyleSheet("color: green;")

    def create_label(self):
        label_dialog = LabelDialog(self)
        if label_dialog.exec_() == QDialog.Accepted:
            label_data = label_dialog.get_label_data()
            self.labels.append(label_data)
            self.update_labels_list()

    def edit_label(self, item):
        index = self.labels_list.row(item)
        label_data = self.labels[index]
        edit_dialog = LabelDialog(self, label_data)
        if edit_dialog.exec_() == QDialog.Accepted:
            self.labels[index] = edit_dialog.get_label_data()
            self.update_labels_list()

    def update_labels_list(self):
        self.labels_list.clear()
        for label in self.labels:
            self.labels_list.addItem(f"Надпись: {label['text'][:10]}...")

    def save_screenshots(self):
        if not self.image_path:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите фотографию.")
            return
        if not self.save_path:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите папку для сохранения.")
            return

        try:
            count = int(self.screenshot_count_input.value())
        except ValueError:
            QMessageBox.warning(self, "Внимание", "Некорректное количество скриншотов.")
            return

        for i in range(1, count + 1):
            image = Image.open(self.image_path)
            draw = ImageDraw.Draw(image)
            for label in self.labels:
                font = ImageFont.truetype("arial.ttf", label['size'])  # Укажите путь к шрифту
                draw.text((label['x'], label['y']), label['text'], fill=label['color'], font=font)

            #  генерация уникального имени файла
            base_name = "screenshot"  # Базовое имя файла
            file_name = os.path.join(self.save_path, f"{base_name}.png")
            counter = 1

            while os.path.exists(file_name):
                file_name = os.path.join(self.save_path, f"{base_name}_{counter}.png")
                counter += 1

            image.save(file_name)

        QMessageBox.information(self, "Успех", f"{count} скриншотов сохранено в {self.save_path}")

    def save_template(self):
        template_name, ok = QInputDialog.getText(self, "Сохранить шаблон", "Введите название шаблона:")
        if ok and template_name:
            file_path = f"{template_name}.csv"
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['text', 'x', 'y', 'size', 'color']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for label in self.labels:
                    writer.writerow(label)

            self.load_templates()
            QMessageBox.information(self, "Успех", f"Шаблон '{template_name}' сохранен.")

    def load_templates(self):
        self.templates_list.clear()
        for file in os.listdir():
            if file.endswith(".csv"):
                self.templates_list.addItem(file)

    def load_template(self):
        selected_template = self.templates_list.currentItem()
        if selected_template:
            file_path = selected_template.text()
            self.labels = []  # Очищаем текущие надписи
            with open(file_path, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.labels.append({
                        'text': row['text'],
                        'x': int(row['x']),
                        'y': int(row['y']),
                        'size': int(row['size']),
                        'color': row['color']
                    })
            self.update_labels_list()

    def show_preview(self):
        if not self.image_path:
            QMessageBox.warning(self, "Внимание", "Пожалуйста, выберите фотографию.")
            return

        try:
            image = Image.open(self.image_path)
            draw = ImageDraw.Draw(image)
            for label in self.labels:
                font = ImageFont.truetype("arial.ttf", label['size'])  # Укажите путь к шрифту
                draw.text((label['x'], label['y']), label['text'], fill=label['color'], font=font)

            image.save("preview.png")
            os.startfile("preview.png")  # Открываем файл
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании предпросмотра: {e}")

    def apply_theme(self, index):
        theme_name = self.theme_combo.itemText(index)
        if theme_name == "Светлая":
            self.setStyleSheet(self.get_light_theme_style())
            QApplication.instance().setStyleSheet(self.get_light_theme_style())
        elif theme_name == "Темная":
            self.setStyleSheet(self.get_dark_theme_style())
            QApplication.instance().setStyleSheet(self.get_dark_theme_style())
        elif theme_name == "Синяя":
            self.setStyleSheet(self.get_blue_theme_style())
            QApplication.instance().setStyleSheet(self.get_blue_theme_style())
        elif theme_name == "Зеленая":
            self.setStyleSheet(self.get_green_theme_style())
            QApplication.instance().setStyleSheet(self.get_green_theme_style())

    def get_light_theme_style(self):
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f0f0, stop:1 #fff);
                color: #333;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ddd, stop:1 #eee);
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ccc, stop:1 #ddd);
            }
            QListWidget {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QSpinBox, QLineEdit {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                background-color: #f9f9f9;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
            }
        """

    def get_dark_theme_style(self):
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #222, stop:1 #333);
                color: #eee;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #444, stop:1 #555);
                border: 1px solid #666;
                border-radius: 5px;
                padding: 8px;
                color: #eee;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #555, stop:1 #666);
            }
            QListWidget {
                background-color: #444;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 5px;
                color: #eee;
            }
            QSpinBox, QLineEdit {
                background-color: #444;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 5px;
                color: #eee;
            }
            QComboBox {
                background-color: #444;
                border: 1px solid #666;
                border-radius: 5px;
                padding: 5px;
                color: #eee;
            }
        """

    def get_blue_theme_style(self):
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a6c0fe, stop:1 #f6f8fa);
                color: #2e3a87;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5f75bd, stop:1 #a6c0fe);
                border: 1px solid #879ddc;
                border-radius: 5px;
                padding: 8px;
                color: #fff;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7a91d4, stop:1 #b4c9f1);
            }
            QListWidget {
                background-color: #e0eafa;
                border: 1px solid #b4c9f1;
                border-radius: 5px;
                padding: 5px;
                color: #2e3a87;
            }
            QSpinBox, QLineEdit {
                background-color: #e0eafa;
                border: 1px solid #b4c9f1;
                border-radius: 5px;
                padding: 5px;
                color: #2e3a87;
            }
             QComboBox {
                background-color: #e0eafa;
                border: 1px solid #b4c9f1;
                border-radius: 5px;
                padding: 5px;
                color: #2e3a87;
            }
        """

    def get_green_theme_style(self):
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #c8e6c9, stop:1 #e8f5e9);
                color: #1b5e20;
                font-family: Arial;
                font-size: 14px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66bb6a, stop:1 #a5d6a7);
                border: 1px solid #81c784;
                border-radius: 5px;
                padding: 8px;
                color: #fff;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #7fca80, stop:1 #b7e1b9);
            }
            QListWidget {
                background-color: #dcedc8;
                border: 1px solid #a5d6a7;
                border-radius: 5px;
                padding: 5px;
                color: #1b5e20;
            }
            QSpinBox, QLineEdit {
                background-color: #dcedc8;
                border: 1px solid #a5d6a7;
                border-radius: 5px;
                padding: 5px;
                color: #1b5e20;
            }
            QComboBox {
                background-color: #dcedc8;
                border: 1px solid #a5d6a7;
                border-radius: 5px;
                padding: 5px;
                color: #1b5e20;
            }
        """


class LabelDialog(QDialog):
    def __init__(self, parent=None, label_data=None):
        super().__init__(parent)
        self.label_data = label_data
        self.initUI()

    def initUI(self):
        self.text_label = QLabel("Текст:")
        self.text_input = QLineEdit()
        self.x_label = QLabel("Координата X:")
        self.x_input = QSpinBox()
        self.x_input.setMaximum(9999)  # Максимальное значение для X
        self.y_label = QLabel("Координата Y:")
        self.y_input = QSpinBox()
        self.y_input.setMaximum(9999)  # Максимальное значение для Y
        self.size_label = QLabel("Размер:")
        self.size_input = QSpinBox()
        self.color_label = QLabel("Цвет:")
        self.color_button = QPushButton("Выбрать цвет")
        self.color_button.clicked.connect(self.choose_color)
        self.color = QColor(0, 0, 0)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        if self.label_data:
            self.text_input.setText(self.label_data['text'])
            self.x_input.setValue(int(self.label_data['x']))
            self.y_input.setValue(int(self.label_data['y']))
            self.size_input.setValue(int(self.label_data['size']))
            self.color = QColor(self.label_data['color'])

        grid = QVBoxLayout()
        grid.addWidget(self.text_label)
        grid.addWidget(self.text_input)
        grid.addWidget(self.x_label)
        grid.addWidget(self.x_input)
        grid.addWidget(self.y_label)
        grid.addWidget(self.y_input)
        grid.addWidget(self.size_label)
        grid.addWidget(self.size_input)
        grid.addWidget(self.color_label)
        grid.addWidget(self.color_button)

        hbox = QHBoxLayout()
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.cancel_button)

        grid.addLayout(hbox)

        self.setLayout(grid)
        self.setWindowTitle("Создать/Редактировать надпись")

    def choose_color(self):
        color = QColorDialog.getColor(self.color, self)
        if color.isValid():
            self.color = color

    def get_label_data(self):
        return {
            'text': self.text_input.text(),
            'x': self.x_input.value(),
            'y': self.y_input.value(),
            'size': self.size_input.value(),
            'color': self.color.name()
        }


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    # Применяем светлую тему ко всему приложению
    app.setStyleSheet("""
        QWidget {
            background-color: #fff;
            color: #000;
        }
    """)
    main_window = MainWindow()
    MainWindow.image_path = None  # Добавляем атрибут класса
    main_window.show()
    sys.exit(app.exec_())