import sys
import os
import json
import shutil
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class FakeExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_path = os.path.expanduser("~")
        self.fake_root = os.path.join(os.path.expanduser("~"), "FakeSystem")
        self.init_fake_structure()
        self.init_ui()
        
    def init_fake_structure(self):
        """Создает фейковую структуру папок"""
        if not os.path.exists(self.fake_root):
            os.makedirs(self.fake_root)
            
        # Базовые папки
        folders = [
            "Windows", "Program Files", "Program Files (x86)", 
            "Users", "System32", "Temp", "AppData",
            "Documents", "Downloads", "Desktop", "Pictures", "Music", "Videos"
        ]
        
        for folder in folders:
            path = os.path.join(self.fake_root, folder)
            if not os.path.exists(path):
                os.makedirs(path)
        
        # Создаем некоторые фейковые файлы
        files = {
            "Windows/notepad.exe": "Fake Notepad",
            "Windows/explorer.exe": "Fake Explorer",
            "System32/kernel32.dll": "Fake Kernel",
            "Program Files/readme.txt": "This is a fake system",
            "Users/README.txt": "Fake user files"
        }
        
        for file_path, content in files.items():
            full_path = os.path.join(self.fake_root, file_path)
            if not os.path.exists(full_path):
                with open(full_path, 'w') as f:
                    f.write(content)
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Проводник")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Меню
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("&Файл")
        new_window = QAction("Новое окно", self)
        new_window.triggered.connect(self.new_window)
        file_menu.addAction(new_window)
        
        file_menu.addSeparator()
        
        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(self.delete_selected)
        file_menu.addAction(delete_action)
        
        rename_action = QAction("Переименовать", self)
        rename_action.triggered.connect(self.rename_selected)
        file_menu.addAction(rename_action)
        
        file_menu.addSeparator()
        
        new_folder = QAction("Новая папка", self)
        new_folder.triggered.connect(self.create_folder)
        file_menu.addAction(new_folder)
        
        new_file = QAction("Новый текстовый документ", self)
        new_file.triggered.connect(self.create_file)
        file_menu.addAction(new_file)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Вид
        view_menu = menubar.addMenu("&Вид")
        details_action = QAction("Таблица", self)
        details_action.triggered.connect(lambda: self.set_view_mode(0))
        view_menu.addAction(details_action)
        
        list_action = QAction("Список", self)
        list_action.triggered.connect(lambda: self.set_view_mode(1))
        view_menu.addAction(list_action)
        
        # Панель инструментов
        toolbar = self.addToolBar("Навигация")
        toolbar.setMovable(False)
        
        back_btn = QAction("←", self)
        back_btn.triggered.connect(self.go_back)
        toolbar.addAction(back_btn)
        
        forward_btn = QAction("→", self)
        forward_btn.triggered.connect(self.go_forward)
        toolbar.addAction(forward_btn)
        
        up_btn = QAction("↑", self)
        up_btn.triggered.connect(self.go_up)
        toolbar.addAction(up_btn)
        
        toolbar.addSeparator()
        
        self.address_bar = QComboBox()
        self.address_bar.setEditable(True)
        self.address_bar.setMinimumWidth(500)
        self.address_bar.currentTextChanged.connect(self.navigate_to)
        toolbar.addWidget(self.address_bar)
        
        toolbar.addSeparator()
        
        # Строка состояния
        self.status_label = QLabel("Готово")
        self.statusBar().addWidget(self.status_label)
        
        # Основной виджет с таблицей
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Имя", "Дата изменения", "Тип", "Размер"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.itemDoubleClicked.connect(self.item_double_clicked)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.table)
        
        # Загрузка начальной директории
        self.load_directory(self.current_path)
        
        # Стиль
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QTableWidget {
                gridline-color: #e0e0e0;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
                color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
            QToolBar {
                background-color: #f5f5f5;
                border: none;
                padding: 2px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
            }
            QMenuBar {
                background-color: #f5f5f5;
            }
        """)
    
    def get_fake_path(self, path):
        """Преобразует реальный путь в фейковый"""
        if path.startswith(self.fake_root):
            return path
        return os.path.join(self.fake_root, path.lstrip('/'))
    
    def load_directory(self, path):
        """Загружает содержимое директории"""
        # Проверяем, существует ли директория
        display_path = path
        if not os.path.exists(path):
            # Если путь не существует, создаем его в фейковой системе
            fake_path = self.get_fake_path(path)
            if not os.path.exists(fake_path):
                os.makedirs(fake_path)
            path = fake_path
        
        self.current_path = path
        self.table.setSortingEnabled(False)
        self.table.clearContents()
        self.table.setRowCount(0)
        
        try:
            items = os.listdir(path)
            
            # Добавляем ".." для навигации вверх
            if path != self.fake_root and path != os.path.dirname(self.fake_root):
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(".."))
                self.table.setItem(row, 1, QTableWidgetItem(""))
                self.table.setItem(row, 2, QTableWidgetItem("Папка"))
                self.table.setItem(row, 3, QTableWidgetItem(""))
            
            # Сортируем: сначала папки, потом файлы
            dirs = []
            files = []
            for item in items:
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    dirs.append(item)
                else:
                    files.append(item)
            
            # Добавляем папки
            for item in sorted(dirs):
                full_path = os.path.join(path, item)
                self.add_item_to_table(item, full_path)
            
            # Добавляем файлы
            for item in sorted(files):
                full_path = os.path.join(path, item)
                self.add_item_to_table(item, full_path)
            
            # Обновляем адресную строку
            self.address_bar.setCurrentText(path)
            
            # Обновляем статус
            total_items = len(dirs) + len(files)
            self.status_label.setText(f"Объектов: {total_items}")
            
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть папку: {str(e)}")
        
        self.table.setSortingEnabled(True)
    
    def add_item_to_table(self, name, full_path):
        """Добавляет элемент в таблицу"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Имя
        self.table.setItem(row, 0, QTableWidgetItem(name))
        
        # Дата изменения
        try:
            mtime = os.path.getmtime(full_path)
            date_str = datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M")
        except:
            date_str = ""
        self.table.setItem(row, 1, QTableWidgetItem(date_str))
        
        # Тип
        if os.path.isdir(full_path):
            self.table.setItem(row, 2, QTableWidgetItem("Папка"))
            self.table.setItem(row, 3, QTableWidgetItem(""))
        else:
            ext = os.path.splitext(name)[1].upper()
            if ext:
                self.table.setItem(row, 2, QTableWidgetItem(ext[1:] + " файл"))
            else:
                self.table.setItem(row, 2, QTableWidgetItem("Файл"))
            
            # Размер
            try:
                size = os.path.getsize(full_path)
                if size < 1024:
                    size_str = f"{size} Б"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} КБ"
                elif size < 1024 * 1024 * 1024:
                    size_str = f"{size/(1024*1024):.1f} МБ"
                else:
                    size_str = f"{size/(1024*1024*1024):.1f} ГБ"
                self.table.setItem(row, 3, QTableWidgetItem(size_str))
            except:
                self.table.setItem(row, 3, QTableWidgetItem(""))
    
    def navigate_to(self, path):
        """Навигация по указанному пути"""
        if path and path != self.current_path:
            self.load_directory(path)
    
    def go_back(self):
        """Назад"""
        # Простая навигация назад
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.load_directory(parent)
    
    def go_forward(self):
        """Вперед"""
        # В этой версии просто обновляем
        self.load_directory(self.current_path)
    
    def go_up(self):
        """Вверх"""
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.load_directory(parent)
    
    def item_double_clicked(self, item):
        """Обработка двойного клика"""
        row = item.row()
        name = self.table.item(row, 0).text()
        
        if name == "..":
            self.go_up()
            return
        
        full_path = os.path.join(self.current_path, name)
        if os.path.isdir(full_path):
            self.load_directory(full_path)
        else:
            # Показываем содержимое файла
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
                    QMessageBox.information(self, name, content[:500])
            except:
                QMessageBox.information(self, "Информация", f"Файл: {name}")
    
    def show_context_menu(self, position):
        """Контекстное меню"""
        menu = QMenu()
        
        new_folder = QAction("Создать папку", self)
        new_folder.triggered.connect(self.create_folder)
        menu.addAction(new_folder)
        
        new_file = QAction("Создать файл", self)
        new_file.triggered.connect(self.create_file)
        menu.addAction(new_file)
        
        menu.addSeparator()
        
        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        rename_action = QAction("Переименовать", self)
        rename_action.triggered.connect(self.rename_selected)
        menu.addAction(rename_action)
        
        menu.addSeparator()
        
        properties_action = QAction("Свойства", self)
        properties_action.triggered.connect(self.show_properties)
        menu.addAction(properties_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))
    
    def create_folder(self):
        """Создание папки"""
        name, ok = QInputDialog.getText(self, "Новая папка", "Введите имя папки:")
        if ok and name:
            path = os.path.join(self.current_path, name)
            try:
                os.makedirs(path)
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))
    
    def create_file(self):
        """Создание файла"""
        name, ok = QInputDialog.getText(self, "Новый файл", "Введите имя файла:")
        if ok and name:
            path = os.path.join(self.current_path, name)
            try:
                with open(path, 'w') as f:
                    f.write("")
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))
    
    def delete_selected(self):
        """Удаление выбранных элементов"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        rows = set(item.row() for item in selected)
        
        reply = QMessageBox.question(self, "Удаление", 
                                    f"Удалить {len(rows)} элемент(ов)?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for row in sorted(rows, reverse=True):
                name = self.table.item(row, 0).text()
                if name == "..":
                    continue
                path = os.path.join(self.current_path, name)
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", str(e))
            self.load_directory(self.current_path)
    
    def rename_selected(self):
        """Переименование элемента"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        name = self.table.item(row, 0).text()
        
        if name == "..":
            return
        
        new_name, ok = QInputDialog.getText(self, "Переименовать", 
                                           "Введите новое имя:", 
                                           text=name)
        if ok and new_name and new_name != name:
            old_path = os.path.join(self.current_path, name)
            new_path = os.path.join(self.current_path, new_name)
            try:
                os.rename(old_path, new_path)
                self.load_directory(self.current_path)
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))
    
    def show_properties(self):
        """Свойства элемента"""
        selected = self.table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        name = self.table.item(row, 0).text()
        
        if name == "..":
            return
        
        full_path = os.path.join(self.current_path, name)
        
        info = f"Имя: {name}\n"
        info += f"Путь: {full_path}\n"
        
        if os.path.isdir(full_path):
            info += "Тип: Папка\n"
            try:
                count = len(os.listdir(full_path))
                info += f"Содержит: {count} элементов\n"
            except:
                pass
        else:
            info += "Тип: Файл\n"
            try:
                size = os.path.getsize(full_path)
                info += f"Размер: {size} байт\n"
            except:
                pass
        
        info += f"Создан: {datetime.fromtimestamp(os.path.getctime(full_path)).strftime('%d.%m.%Y %H:%M')}\n"
        info += f"Изменен: {datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%d.%m.%Y %H:%M')}"
        
        QMessageBox.information(self, "Свойства", info)
    
    def set_view_mode(self, mode):
        """Установка режима просмотра"""
        # В этой версии просто меняем заголовки
        if mode == 0:  # Таблица
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Имя", "Дата изменения", "Тип", "Размер"])
        else:  # Список
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Имя"])
        
        self.load_directory(self.current_path)
    
    def new_window(self):
        """Создание нового окна"""
        new_window = FakeExplorer()
        new_window.show()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Иконка не нужна
    app.setWindowIcon(QIcon())
    
    window = FakeExplorer()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
