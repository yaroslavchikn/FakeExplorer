import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor

class FakeChrome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = []
        self.current_tab_index = 0
        self.history = []
        self.bookmarks = []
        self.downloads = []
        self.init_ui()
        self.load_settings()
        self.create_new_tab("https://www.google.com")
        
    def init_ui(self):
        """Инициализация интерфейса - точная копия Chrome"""
        self.setWindowTitle("Google Chrome")
        self.setGeometry(50, 50, 1400, 900)
        
        # Устанавливаем иконку Chrome (встроенная)
        self.setWindowIcon(QIcon())
        
        # Стиль - точная копия Chrome
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QMenuBar {
                background-color: #f1f3f4;
                border: none;
                color: #202124;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #e8eaed;
                border-radius: 4px;
            }
            QToolBar {
                background-color: #f1f3f4;
                border: none;
                spacing: 3px;
                padding: 2px 8px;
            }
            QTabBar::tab {
                background-color: #dee1e6;
                border: none;
                padding: 6px 15px;
                margin: 2px 0px;
                border-radius: 6px 6px 0 0;
                min-width: 100px;
                color: #202124;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #e8eaed;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
                color: #202124;
                selection-background-color: #1a73e8;
            }
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                background-color: #ffffff;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 6px 8px;
                border-radius: 4px;
                color: #5f6368;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QPushButton:pressed {
                background-color: #dadce0;
            }
            QStatusBar {
                background-color: #f1f3f4;
                color: #5f6368;
                border-top: 1px solid #dadce0;
            }
            QWidget#tab_container {
                background-color: #f1f3f4;
                border: none;
            }
            QWidget#content_widget {
                background-color: #ffffff;
                border: none;
            }
        """)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Меню
        self.create_menu()
        
        # Основной контейнер
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        main_layout.addWidget(container)
        
        # Верхняя панель (табы + управление)
        top_panel = QWidget()
        top_panel.setObjectName("tab_container")
        top_panel_layout = QHBoxLayout(top_panel)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)
        top_panel_layout.setSpacing(0)
        container_layout.addWidget(top_panel)
        
        # Панель вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
        """)
        top_panel_layout.addWidget(self.tab_widget)
        
        # Панель инструментов
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        container_layout.addWidget(toolbar)
        
        # Кнопки навигации
        self.back_btn = QAction("◀", self)
        self.back_btn.triggered.connect(self.go_back)
        self.back_btn.setToolTip("Назад")
        toolbar.addAction(self.back_btn)
        
        self.forward_btn = QAction("▶", self)
        self.forward_btn.triggered.connect(self.go_forward)
        self.forward_btn.setToolTip("Вперед")
        toolbar.addAction(self.forward_btn)
        
        self.refresh_btn = QAction("⟳", self)
        self.refresh_btn.triggered.connect(self.refresh_page)
        self.refresh_btn.setToolTip("Обновить")
        toolbar.addAction(self.refresh_btn)
        
        toolbar.addSeparator()
        
        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Поиск в Google или введите адрес")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        toolbar.addSeparator()
        
        # Кнопка закладок
        self.bookmark_btn = QAction("☆", self)
        self.bookmark_btn.triggered.connect(self.toggle_bookmark)
        self.bookmark_btn.setToolTip("Добавить в закладки")
        toolbar.addAction(self.bookmark_btn)
        
        # Кнопка меню (три точки)
        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(36, 36)
        menu_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
            }
        """)
        menu_btn.clicked.connect(self.show_chrome_menu)
        toolbar.addWidget(menu_btn)
        
        # Контент (веб-страница)
        self.content_widget = QWidget()
        self.content_widget.setObjectName("content_widget")
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.content_widget)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
        
        # Загружаем первую вкладку
        self.add_new_tab()
        
    def create_menu(self):
        """Создание меню как в Chrome"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("Файл")
        new_tab = QAction("Новая вкладка", self)
        new_tab.setShortcut("Ctrl+T")
        new_tab.triggered.connect(lambda: self.add_new_tab())
        file_menu.addAction(new_tab)
        
        new_window = QAction("Новое окно", self)
        new_window.setShortcut("Ctrl+N")
        new_window.triggered.connect(self.new_window)
        file_menu.addAction(new_window)
        
        file_menu.addSeparator()
        
        open_file = QAction("Открыть файл...", self)
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self.open_file)
        file_menu.addAction(open_file)
        
        file_menu.addSeparator()
        
        save_page = QAction("Сохранить страницу как...", self)
        save_page.setShortcut("Ctrl+S")
        save_page.triggered.connect(self.save_page)
        file_menu.addAction(save_page)
        
        file_menu.addSeparator()
        
        print_action = QAction("Печать...", self)
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_page)
        file_menu.addAction(print_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Shift+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Правка
        edit_menu = menubar.addMenu("Правка")
        cut = QAction("Вырезать", self)
        cut.setShortcut("Ctrl+X")
        cut.triggered.connect(lambda: self.current_webview().triggerPageAction(QWebEnginePage.Cut))
        edit_menu.addAction(cut)
        
        copy = QAction("Копировать", self)
        copy.setShortcut("Ctrl+C")
        copy.triggered.connect(lambda: self.current_webview().triggerPageAction(QWebEnginePage.Copy))
        edit_menu.addAction(copy)
        
        paste = QAction("Вставить", self)
        paste.setShortcut("Ctrl+V")
        paste.triggered.connect(lambda: self.current_webview().triggerPageAction(QWebEnginePage.Paste))
        edit_menu.addAction(paste)
        
        edit_menu.addSeparator()
        
        find = QAction("Найти...", self)
        find.setShortcut("Ctrl+F")
        find.triggered.connect(self.show_find)
        edit_menu.addAction(find)
        
        # Вид
        view_menu = menubar.addMenu("Вид")
        zoom_in = QAction("Увеличить", self)
        zoom_in.setShortcut("Ctrl++")
        zoom_in.triggered.connect(lambda: self.current_webview().setZoomFactor(
            self.current_webview().zoomFactor() + 0.1
        ))
        view_menu.addAction(zoom_in)
        
        zoom_out = QAction("Уменьшить", self)
        zoom_out.setShortcut("Ctrl+-")
        zoom_out.triggered.connect(lambda: self.current_webview().setZoomFactor(
            self.current_webview().zoomFactor() - 0.1
        ))
        view_menu.addAction(zoom_out)
        
        reset_zoom = QAction("Обычный размер", self)
        reset_zoom.setShortcut("Ctrl+0")
        reset_zoom.triggered.connect(lambda: self.current_webview().setZoomFactor(1.0))
        view_menu.addAction(reset_zoom)
        
        view_menu.addSeparator()
        
        fullscreen = QAction("Полноэкранный режим", self)
        fullscreen.setShortcut("F11")
        fullscreen.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen)
        
        # Закладки
        bookmarks_menu = menubar.addMenu("Закладки")
        show_bookmarks = QAction("Показать закладки", self)
        show_bookmarks.setShortcut("Ctrl+Shift+O")
        show_bookmarks.triggered.connect(self.show_bookmarks)
        bookmarks_menu.addAction(show_bookmarks)
        
        bookmarks_menu.addSeparator()
        
        add_bookmark = QAction("Добавить в закладки", self)
        add_bookmark.setShortcut("Ctrl+D")
        add_bookmark.triggered.connect(self.toggle_bookmark)
        bookmarks_menu.addAction(add_bookmark)
        
        # История
        history_menu = menubar.addMenu("История")
        show_history = QAction("Показать историю", self)
        show_history.setShortcut("Ctrl+H")
        show_history.triggered.connect(self.show_history)
        history_menu.addAction(show_history)
        
        # Дополнительно
        more_menu = menubar.addMenu("Дополнительно")
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.show_settings)
        more_menu.addAction(settings_action)
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        more_menu.addAction(about_action)
    
    def create_new_tab(self, url=None):
        """Создание новой вкладки"""
        if url is None:
            url = "https://www.google.com"
        
        # Создаем виджет для вкладки
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # WebView
        webview = QWebEngineView()
        webview.setUrl(QUrl(url))
        webview.loadFinished.connect(lambda: self.on_load_finished(webview))
        webview.urlChanged.connect(lambda url: self.on_url_changed(webview, url))
        webview.titleChanged.connect(lambda title: self.update_tab_title(webview, title))
        
        tab_layout.addWidget(webview)
        
        # Добавляем вкладку
        index = self.tab_widget.addTab(tab_widget, "Новая вкладка")
        self.tab_widget.setCurrentIndex(index)
        self.current_tab_index = index
        
        # Сохраняем ссылку на webview
        self.tabs.append(webview)
        
        # Обновляем адресную строку
        self.url_bar.setText(url)
        
        return webview
    
    def current_webview(self):
        """Получение текущего webview"""
        if self.tab_widget.count() > 0:
            current_widget = self.tab_widget.currentWidget()
            if current_widget:
                return current_widget.findChild(QWebEngineView)
        return None
    
    def add_new_tab(self, url=None):
        """Добавление новой вкладки"""
        if url is None:
            url = "https://www.google.com"
        self.create_new_tab(url)
    
    def close_tab(self, index):
        """Закрытие вкладки"""
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            widget.deleteLater()
            self.tabs.pop(index)
        else:
            # Если это последняя вкладка, создаем новую вместо закрытия
            self.create_new_tab("https://www.google.com")
    
    def on_tab_changed(self, index):
        """При смене вкладки"""
        if index >= 0 and index < len(self.tabs):
            self.current_tab_index = index
            webview = self.tabs[index]
            self.url_bar.setText(webview.url().toString())
    
    def on_url_changed(self, webview, url):
        """При изменении URL"""
        if webview == self.current_webview():
            self.url_bar.setText(url.toString())
            # Добавляем в историю
            if url.toString() not in [h[0] for h in self.history]:
                self.history.append((url.toString(), datetime.now().strftime("%d.%m.%Y %H:%M")))
    
    def on_load_finished(self, webview):
        """Когда страница загружена"""
        if webview == self.current_webview():
            self.status_bar.showMessage("Готово")
    
    def update_tab_title(self, webview, title):
        """Обновление заголовка вкладки"""
        index = self.tabs.index(webview) if webview in self.tabs else -1
        if index >= 0:
            if len(title) > 30:
                title = title[:27] + "..."
            self.tab_widget.setTabText(index, title)
    
    def navigate_to_url(self):
        """Навигация по URL или поиск"""
        text = self.url_bar.text().strip()
        if not text:
            return
        
        # Проверяем, является ли текст URL
        if text.startswith(("http://", "https://")):
            url = QUrl(text)
        elif "." in text and not " " in text:
            url = QUrl("https://" + text)
        else:
            # Поиск в Google
            search_text = text.replace(" ", "+")
            url = QUrl(f"https://www.google.com/search?q={search_text}")
        
        webview = self.current_webview()
        if webview:
            webview.setUrl(url)
            self.url_bar.setText(url.toString())
    
    def go_back(self):
        """Назад"""
        webview = self.current_webview()
        if webview and webview.history().canGoBack():
            webview.back()
    
    def go_forward(self):
        """Вперед"""
        webview = self.current_webview()
        if webview and webview.history().canGoForward():
            webview.forward()
    
    def refresh_page(self):
        """Обновить страницу"""
        webview = self.current_webview()
        if webview:
            webview.reload()
    
    def toggle_bookmark(self):
        """Добавить/удалить закладку"""
        webview = self.current_webview()
        if not webview:
            return
        
        url = webview.url().toString()
        title = webview.title()
        
        # Проверяем, есть ли уже в закладках
        for i, (bookmark_url, bookmark_title) in enumerate(self.bookmarks):
            if bookmark_url == url:
                self.bookmarks.pop(i)
                self.bookmark_btn.setText("☆")
                self.status_bar.showMessage("Закладка удалена")
                return
        
        # Добавляем закладку
        self.bookmarks.append((url, title))
        self.bookmark_btn.setText("★")
        self.status_bar.showMessage("Закладка добавлена")
    
    def show_bookmarks(self):
        """Показать закладки"""
        if not self.bookmarks:
            QMessageBox.information(self, "Закладки", "Нет закладок")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Закладки")
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        
        for url, title in self.bookmarks:
            item = QListWidgetItem(f"{title}\n{url}")
            item.setData(Qt.UserRole, url)
            list_widget.addItem(item)
        
        list_widget.itemDoubleClicked.connect(lambda item: self.open_bookmark(item.data(Qt.UserRole)))
        
        layout.addWidget(list_widget)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def open_bookmark(self, url):
        """Открыть закладку"""
        self.add_new_tab(url)
    
    def show_history(self):
        """Показать историю"""
        if not self.history:
            QMessageBox.information(self, "История", "История пуста")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("История")
        dialog.setGeometry(200, 200, 600, 400)
        
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        
        for url, date in self.history[-50:]:  # Показываем последние 50
            item = QListWidgetItem(f"{date}\n{url}")
            item.setData(Qt.UserRole, url)
            list_widget.addItem(item)
        
        list_widget.itemDoubleClicked.connect(lambda item: self.open_history(item.data(Qt.UserRole)))
        
        layout.addWidget(list_widget)
        
        clear_btn = QPushButton("Очистить историю")
        clear_btn.clicked.connect(lambda: self.clear_history(list_widget))
        layout.addWidget(clear_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def clear_history(self, list_widget):
        """Очистить историю"""
        self.history.clear()
        list_widget.clear()
        QMessageBox.information(self, "История", "История очищена")
    
    def open_history(self, url):
        """Открыть из истории"""
        self.add_new_tab(url)
    
    def show_find(self):
        """Поиск на странице"""
        webview = self.current_webview()
        if webview:
            webview.findText("")
            # Простой диалог поиска
            text, ok = QInputDialog.getText(self, "Поиск", "Найти:")
            if ok and text:
                webview.findText(text)
    
    def open_file(self):
        """Открыть файл"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "HTML Files (*.html *.htm);;All Files (*.*)")
        if file_path:
            webview = self.current_webview()
            if webview:
                webview.setUrl(QUrl.fromLocalFile(file_path))
    
    def save_page(self):
        """Сохранить страницу"""
        webview = self.current_webview()
        if webview:
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить страницу", "", "HTML Files (*.html);;All Files (*.*)")
            if file_path:
                webview.page().toHtml(lambda html: self.save_html(html, file_path))
    
    def save_html(self, html, file_path):
        """Сохранение HTML"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.status_bar.showMessage(f"Страница сохранена: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить: {str(e)}")
    
    def print_page(self):
        """Печать страницы"""
        webview = self.current_webview()
        if webview:
            webview.page().printToPdf("page.pdf")
            self.status_bar.showMessage("PDF создан: page.pdf")
    
    def toggle_fullscreen(self):
        """Полноэкранный режим"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_settings(self):
        """Настройки"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки")
        dialog.setGeometry(300, 300, 400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Выбор поисковика
        group = QGroupBox("Поисковая система")
        group_layout = QVBoxLayout(group)
        
        search_engines = ["Google", "Yandex", "Bing", "DuckDuckGo"]
        self.search_combo = QComboBox()
        self.search_combo.addItems(search_engines)
        group_layout.addWidget(self.search_combo)
        
        layout.addWidget(group)
        
        # Домашняя страница
        home_group = QGroupBox("Домашняя страница")
        home_layout = QVBoxLayout(home_group)
        home_input = QLineEdit("https://www.google.com")
        home_layout.addWidget(home_input)
        layout.addWidget(home_group)
        
        # Кнопка сохранения
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(dialog.close)
        layout.addWidget(save_btn)
        
        dialog.exec_()
    
    def show_about(self):
        """О программе"""
        QMessageBox.about(self, "О программе", 
            "Google Chrome\nВерсия 120.0.6099.216\n\n"
            "© 2024 Google Inc. Все права защищены.\n"
            "Это копия Chrome, созданная для демонстрации.")
    
    def show_chrome_menu(self):
        """Меню с тремя точками"""
        menu = QMenu(self)
        
        new_tab = menu.addAction("Новая вкладка")
        new_tab.triggered.connect(lambda: self.add_new_tab())
        
        new_window = menu.addAction("Новое окно")
        new_window.triggered.connect(self.new_window)
        
        menu.addSeparator()
        
        history_action = menu.addAction("История")
        history_action.triggered.connect(self.show_history)
        
        bookmarks_action = menu.addAction("Закладки")
        bookmarks_action.triggered.connect(self.show_bookmarks)
        
        menu.addSeparator()
        
        downloads_action = menu.addAction("Загрузки")
        downloads_action.triggered.connect(self.show_downloads)
        
        menu.addSeparator()
        
        settings_action = menu.addAction("Настройки")
        settings_action.triggered.connect(self.show_settings)
        
        about_action = menu.addAction("О программе")
        about_action.triggered.connect(self.show_about)
        
        menu.exec_(QCursor.pos())
    
    def show_downloads(self):
        """Показать загрузки"""
        if not self.downloads:
            QMessageBox.information(self, "Загрузки", "Нет загрузок")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Загрузки")
        dialog.setGeometry(200, 200, 400, 300)
        
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        
        for url in self.downloads[-10:]:
            list_widget.addItem(url)
        
        layout.addWidget(list_widget)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def load_settings(self):
        """Загрузка настроек"""
        settings_file = "chrome_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.bookmarks = settings.get("bookmarks", [])
                    self.history = settings.get("history", [])
            except:
                pass
    
    def save_settings(self):
        """Сохранение настроек"""
        settings = {
            "bookmarks": self.bookmarks,
            "history": self.history
        }
        try:
            with open("chrome_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def new_window(self):
        """Новое окно"""
        new_window = FakeChrome()
        new_window.show()
    
    def closeEvent(self, event):
        """При закрытии"""
        self.save_settings()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setWindowIcon(QIcon())
    
    # Включаем поддержку HTTPS
    os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
    
    window = FakeChrome()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
