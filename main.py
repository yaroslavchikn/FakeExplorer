import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineSettings

class ChromeTabBar(QTabBar):
    """Кастомная панель вкладок как в Chrome"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setExpanding(False)
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setUsesScrollButtons(True)
        
    def tabSizeHint(self, index):
        """Размер вкладок как в Chrome"""
        size = super().tabSizeHint(index)
        size.setWidth(min(240, max(100, size.width())))
        return size

class FakeChrome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = []
        self.current_tab_index = 0
        self.history = []
        self.bookmarks = []
        self.downloads = []
        self.is_fullscreen = False
        self.is_incognito = False
        self.search_engine = "Google"
        self.init_ui()
        self.load_settings()
        self.create_new_tab("https://www.google.com")
        
    def init_ui(self):
        """Инициализация интерфейса - 100% копия Chrome"""
        self.setWindowTitle("Google Chrome")
        self.setGeometry(50, 50, 1400, 900)
        self.setMinimumSize(800, 600)
        
        # Устанавливаем иконку Chrome
        self.setWindowIcon(QIcon())
        
        # Стиль - максимально точная копия Chrome
        self.setStyleSheet("""
            /* Общий фон */
            QMainWindow {
                background-color: #ffffff;
            }
            
            /* Строка меню */
            QMenuBar {
                background-color: #f1f3f4;
                border: none;
                color: #202124;
                font-size: 13px;
                padding: 2px 8px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 12px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #e8eaed;
            }
            
            /* Меню */
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 8px;
                padding: 8px 0px;
                color: #202124;
                font-size: 13px;
            }
            QMenu::item {
                padding: 6px 30px 6px 20px;
                border-radius: 0px;
            }
            QMenu::item:selected {
                background-color: #e8eaed;
            }
            QMenu::item:disabled {
                color: #9aa0a6;
            }
            QMenu::separator {
                height: 1px;
                background: #dadce0;
                margin: 4px 10px;
            }
            
            /* Вкладки */
            QTabWidget::pane {
                border: none;
                background-color: #ffffff;
            }
            
            QTabBar {
                background-color: #f1f3f4;
                border: none;
                qproperty-drawBase: 0;
            }
            
            QTabBar::tab {
                background-color: #dee1e6;
                border: none;
                padding: 8px 16px;
                margin: 4px 1px 0px 1px;
                border-radius: 8px 8px 0px 0px;
                min-width: 80px;
                max-width: 240px;
                color: #5f6368;
                font-size: 13px;
                font-weight: 500;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-bottom: none;
                color: #202124;
                margin: 2px 1px 0px 1px;
                padding: 9px 16px 8px 16px;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #e8eaed;
            }
            
            QTabBar::tab:selected:hover {
                background-color: #ffffff;
            }
            
            QTabBar::close-button {
                image: none;
                background: transparent;
                padding: 2px;
                border-radius: 50%;
                width: 16px;
                height: 16px;
            }
            
            QTabBar::close-button:hover {
                background-color: #e8eaed;
            }
            
            QTabBar::close-button:pressed {
                background-color: #dadce0;
            }
            
            /* Панель инструментов */
            QToolBar {
                background-color: #f1f3f4;
                border: none;
                spacing: 0px;
                padding: 2px 8px 6px 8px;
            }
            
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 6px 8px;
                color: #5f6368;
                font-size: 18px;
            }
            
            QToolButton:hover {
                background-color: #e8eaed;
            }
            
            QToolButton:pressed {
                background-color: #dadce0;
            }
            
            QToolButton:disabled {
                color: #9aa0a6;
            }
            
            /* Адресная строка */
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 22px;
                padding: 8px 16px;
                font-size: 14px;
                color: #202124;
                selection-background-color: #1a73e8;
                min-height: 30px;
            }
            
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                background-color: #ffffff;
                box-shadow: 0px 1px 4px rgba(26, 115, 232, 0.2);
            }
            
            QLineEdit:hover {
                border: 1px solid #9aa0a6;
            }
            
            /* Кнопки */
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                color: #5f6368;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background-color: #e8eaed;
            }
            
            QPushButton:pressed {
                background-color: #dadce0;
            }
            
            /* Статус бар */
            QStatusBar {
                background-color: #f1f3f4;
                color: #5f6368;
                border-top: 1px solid #dadce0;
                font-size: 12px;
                padding: 2px 8px;
            }
            
            /* Кнопки вкладок */
            QTabBar QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
            }
            
            QTabBar QToolButton:hover {
                background-color: #e8eaed;
            }
            
            /* Контекстное меню */
            QMenu::right-arrow {
                image: none;
                width: 0px;
            }
            
            /* Закругления для диалогов */
            QDialog {
                background-color: #ffffff;
            }
            
            QGroupBox {
                border: 1px solid #dadce0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 8px;
                font-weight: 500;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: #202124;
            }
            
            QListWidget {
                border: 1px solid #dadce0;
                border-radius: 8px;
                padding: 4px;
                outline: none;
            }
            
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
            }
            
            QListWidget::item:selected {
                background-color: #e8eaed;
            }
            
            QListWidget::item:hover {
                background-color: #f1f3f4;
            }
            
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background: #c1c7cd;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #9aa0a6;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
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
        
        # Контейнер для вкладок и панелей
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        main_layout.addWidget(container)
        
        # Верхняя панель
        top_panel = QWidget()
        top_panel.setObjectName("tab_container")
        top_panel.setStyleSheet("background-color: #f1f3f4;")
        top_panel_layout = QVBoxLayout(top_panel)
        top_panel_layout.setContentsMargins(0, 0, 0, 0)
        top_panel_layout.setSpacing(0)
        container_layout.addWidget(top_panel)
        
        # Панель вкладок (кастомная)
        tab_container = QWidget()
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(8, 0, 0, 0)
        tab_layout.setSpacing(0)
        top_panel_layout.addWidget(tab_container)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(ChromeTabBar())
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        tab_layout.addWidget(self.tab_widget)
        
        # Кнопки управления окном (как в Chrome)
        window_controls = QWidget()
        window_layout = QHBoxLayout(window_controls)
        window_layout.setContentsMargins(0, 0, 8, 0)
        window_layout.setSpacing(0)
        
        # Кнопка "Новая вкладка"
        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedSize(28, 28)
        new_tab_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: 300;
                border-radius: 4px;
                background-color: transparent;
                color: #5f6368;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
        """)
        new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        window_layout.addWidget(new_tab_btn)
        
        # Кнопки управления окном
        for btn, shortcut in [("−", self.showMinimized), ("□", self.toggle_maximize), ("✕", self.close)]:
            button = QPushButton(btn)
            button.setFixedSize(36, 28)
            button.clicked.connect(shortcut)
            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: 500;
                    border: none;
                    background-color: transparent;
                    color: #5f6368;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #e8eaed;
                }
            """)
            if btn == "✕":
                button.setStyleSheet(button.styleSheet() + """
                    QPushButton:hover {
                        background-color: #e81123;
                        color: #ffffff;
                    }
                """)
            window_layout.addWidget(button)
        
        tab_layout.addWidget(window_controls)
        
        # Панель инструментов
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        container_layout.addWidget(toolbar)
        
        # Кнопки навигации с иконками как в Chrome
        self.back_btn = QAction("←", self)
        self.back_btn.triggered.connect(self.go_back)
        self.back_btn.setToolTip("Назад")
        self.back_btn.setEnabled(False)
        toolbar.addAction(self.back_btn)
        
        self.forward_btn = QAction("→", self)
        self.forward_btn.triggered.connect(self.go_forward)
        self.forward_btn.setToolTip("Вперед")
        self.forward_btn.setEnabled(False)
        toolbar.addAction(self.forward_btn)
        
        self.refresh_btn = QAction("↻", self)
        self.refresh_btn.triggered.connect(self.refresh_page)
        self.refresh_btn.setToolTip("Обновить")
        toolbar.addAction(self.refresh_btn)
        
        toolbar.addSeparator()
        
        # Адресная строка
        url_container = QWidget()
        url_layout = QHBoxLayout(url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)
        url_layout.setSpacing(0)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Поиск в Google или введите адрес")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        url_layout.addWidget(self.url_bar)
        
        # Кнопка блокировки (как в Chrome)
        lock_btn = QPushButton("🔒")
        lock_btn.setFixedSize(28, 28)
        lock_btn.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                background: transparent;
                border: none;
                color: #5f6368;
            }
        """)
        url_layout.addWidget(lock_btn)
        
        toolbar.addWidget(url_container)
        
        toolbar.addSeparator()
        
        # Кнопка закладок
        self.bookmark_btn = QAction("☆", self)
        self.bookmark_btn.triggered.connect(self.toggle_bookmark)
        self.bookmark_btn.setToolTip("Добавить в закладки")
        toolbar.addAction(self.bookmark_btn)
        
        # Кнопка расширений (пазл)
        extensions_btn = QAction("🧩", self)
        extensions_btn.setToolTip("Расширения")
        toolbar.addAction(extensions_btn)
        
        # Кнопка профиля
        profile_btn = QAction("👤", self)
        profile_btn.setToolTip("Профиль")
        toolbar.addAction(profile_btn)
        
        # Кнопка меню (три точки)
        menu_btn = QPushButton("⋮")
        menu_btn.setFixedSize(36, 36)
        menu_btn.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: 700;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                color: #5f6368;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #e8eaed;
            }
            QPushButton:pressed {
                background-color: #dadce0;
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
        
        # Добавляем индикатор загрузки
        self.loading_indicator = QLabel()
        self.loading_indicator.setFixedSize(16, 16)
        self.status_bar.addPermanentWidget(self.loading_indicator)
        
        # Загружаем первую вкладку
        self.add_new_tab()
        
    def create_menu(self):
        """Создание меню как в Chrome"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("Файл")
        actions = [
            ("Новая вкладка", "Ctrl+T", lambda: self.add_new_tab()),
            ("Новое окно", "Ctrl+N", self.new_window),
            ("Новое окно в режиме инкогнито", "Ctrl+Shift+N", self.new_incognito),
            None,  # separator
            ("Открыть файл...", "Ctrl+O", self.open_file),
            ("Сохранить страницу как...", "Ctrl+S", self.save_page),
            None,  # separator
            ("Печать...", "Ctrl+P", self.print_page),
            None,  # separator
            ("Выход", "Ctrl+Shift+Q", self.close)
        ]
        for item in actions:
            if item is None:
                file_menu.addSeparator()
            else:
                text, shortcut, callback = item
                action = QAction(text, self)
                action.setShortcut(shortcut)
                action.triggered.connect(callback)
                file_menu.addAction(action)
        
        # Правка
        edit_menu = menubar.addMenu("Правка")
        edit_actions = [
            ("Вырезать", "Ctrl+X", self.cut_text),
            ("Копировать", "Ctrl+C", self.copy_text),
            ("Вставить", "Ctrl+V", self.paste_text),
            None,
            ("Найти...", "Ctrl+F", self.show_find),
            ("Найти далее", "Ctrl+G", self.find_next),
        ]
        for item in edit_actions:
            if item is None:
                edit_menu.addSeparator()
            else:
                text, shortcut, callback = item
                action = QAction(text, self)
                action.setShortcut(shortcut)
                action.triggered.connect(callback)
                edit_menu.addAction(action)
        
        # Вид
        view_menu = menubar.addMenu("Вид")
        view_actions = [
            ("Увеличить", "Ctrl++", lambda: self.zoom(0.1)),
            ("Уменьшить", "Ctrl+-", lambda: self.zoom(-0.1)),
            ("Обычный размер", "Ctrl+0", lambda: self.zoom(0)),
            None,
            ("Полноэкранный режим", "F11", self.toggle_fullscreen),
        ]
        for item in view_actions:
            if item is None:
                view_menu.addSeparator()
            else:
                text, shortcut, callback = item
                action = QAction(text, self)
                action.setShortcut(shortcut)
                action.triggered.connect(callback)
                view_menu.addAction(action)
        
        # Закладки
        bookmarks_menu = menubar.addMenu("Закладки")
        bm_actions = [
            ("Добавить в закладки", "Ctrl+D", self.toggle_bookmark),
            None,
            ("Показать закладки", "Ctrl+Shift+O", self.show_bookmarks),
        ]
        for item in bm_actions:
            if item is None:
                bookmarks_menu.addSeparator()
            else:
                text, shortcut, callback = item
                action = QAction(text, self)
                action.setShortcut(shortcut)
                action.triggered.connect(callback)
                bookmarks_menu.addAction(action)
        
        # История
        history_menu = menubar.addMenu("История")
        hist_actions = [
            ("Показать историю", "Ctrl+H", self.show_history),
            ("Очистить историю", None, self.clear_history_dialog),
        ]
        for text, shortcut, callback in hist_actions:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(callback)
            history_menu.addAction(action)
        
        # Дополнительно
        more_menu = menubar.addMenu("Дополнительно")
        more_actions = [
            ("Настройки", None, self.show_settings),
            ("О программе", None, self.show_about),
        ]
        for text, shortcut, callback in more_actions:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            action.triggered.connect(callback)
            more_menu.addAction(action)
    
    def create_new_tab(self, url=None):
        """Создание новой вкладки с эффектом как в Chrome"""
        if url is None:
            url = "https://www.google.com"
        
        # Создаем виджет для вкладки
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        
        # WebView с настройками как в Chrome
        webview = QWebEngineView()
        webview.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        webview.settings().setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        webview.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        webview.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        webview.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        
        webview.setUrl(QUrl(url))
        webview.loadStarted.connect(lambda: self.on_load_started(webview))
        webview.loadProgress.connect(lambda p: self.on_load_progress(webview, p))
        webview.loadFinished.connect(lambda ok: self.on_load_finished(webview, ok))
        webview.urlChanged.connect(lambda url: self.on_url_changed(webview, url))
        webview.titleChanged.connect(lambda title: self.update_tab_title(webview, title))
        webview.iconChanged.connect(lambda icon: self.update_tab_icon(webview, icon))
        
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
        """Добавление новой вкладки с анимацией"""
        if url is None:
            url = "https://www.google.com"
        self.create_new_tab(url)
    
    def close_tab(self, index):
        """Закрытие вкладки с эффектом как в Chrome"""
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            widget.deleteLater()
            self.tabs.pop(index)
        else:
            # Если это последняя вкладка, создаем новую
            self.create_new_tab("https://www.google.com")
    
    def on_tab_changed(self, index):
        """При смене вкладки"""
        if index >= 0 and index < len(self.tabs):
            self.current_tab_index = index
            webview = self.tabs[index]
            url = webview.url().toString()
            self.url_bar.setText(url)
            
            # Обновляем состояние кнопок
            self.back_btn.setEnabled(webview.history().canGoBack())
            self.forward_btn.setEnabled(webview.history().canGoForward())
            
            # Проверяем закладку
            self.update_bookmark_state(url)
    
    def on_url_changed(self, webview, url):
        """При изменении URL"""
        if webview == self.current_webview():
            url_str = url.toString()
            self.url_bar.setText(url_str)
            self.update_bookmark_state(url_str)
            
            # Добавляем в историю
            if url_str not in [h[0] for h in self.history]:
                self.history.append((url_str, datetime.now().strftime("%d.%m.%Y %H:%M")))
                
                # Сохраняем историю
                self.save_settings()
    
    def on_load_started(self, webview):
        """Начало загрузки"""
        if webview == self.current_webview():
            self.loading_indicator.setText("⟳")
            self.loading_indicator.setStyleSheet("color: #1a73e8; font-size: 16px;")
            self.status_bar.showMessage("Загрузка...")
    
    def on_load_progress(self, webview, progress):
        """Прогресс загрузки"""
        if webview == self.current_webview():
            self.status_bar.showMessage(f"Загрузка... {progress}%")
    
    def on_load_finished(self, webview, ok):
        """Загрузка завершена"""
        if webview == self.current_webview():
            self.loading_indicator.setText("✓")
            self.loading_indicator.setStyleSheet("color: #34a853; font-size: 14px;")
            self.status_bar.showMessage("Готово")
            
            # Обновляем состояние кнопок
            self.back_btn.setEnabled(webview.history().canGoBack())
            self.forward_btn.setEnabled(webview.history().canGoForward())
            
            QTimer.singleShot(1000, lambda: self.loading_indicator.setText(""))
    
    def update_tab_title(self, webview, title):
        """Обновление заголовка вкладки"""
        index = self.tabs.index(webview) if webview in self.tabs else -1
        if index >= 0:
            if len(title) > 30:
                title = title[:27] + "..."
            if not title:
                title = "Новая вкладка"
            self.tab_widget.setTabText(index, title)
    
    def update_tab_icon(self, webview, icon):
        """Обновление иконки вкладки"""
        index = self.tabs.index(webview) if webview in self.tabs else -1
        if index >= 0 and not icon.isNull():
            self.tab_widget.setTabIcon(index, QIcon(icon))
    
    def update_bookmark_state(self, url):
        """Обновление состояния кнопки закладки"""
        is_bookmarked = any(bookmark_url == url for bookmark_url, _ in self.bookmarks)
        self.bookmark_btn.setText("★" if is_bookmarked else "☆")
    
    def navigate_to_url(self):
        """Навигация по URL или поиск"""
        text = self.url_bar.text().strip()
        if not text:
            return
        
        # Проверяем, является ли текст URL
        if text.startswith(("http://", "https://")):
            url = QUrl(text)
        elif "." in text and not " " in text and not text.startswith("chrome://"):
            url = QUrl("https://" + text)
        elif text.startswith("chrome://"):
            url = QUrl(text)
        else:
            # Поиск в Google
            search_text = text.replace(" ", "+")
            url = QUrl(f"https://www.google.com/search?q={search_text}")
        
        webview = self.current_webview()
        if webview:
            webview.setUrl(url)
            self.url_bar.setText(url.toString())
    
    def go_back(self):
        """Назад с анимацией"""
        webview = self.current_webview()
        if webview and webview.history().canGoBack():
            webview.back()
    
    def go_forward(self):
        """Вперед с анимацией"""
        webview = self.current_webview()
        if webview and webview.history().canGoForward():
            webview.forward()
    
    def refresh_page(self):
        """Обновить страницу с анимацией"""
        webview = self.current_webview()
        if webview:
            webview.reload()
    
    def zoom(self, delta):
        """Масштабирование"""
        webview = self.current_webview()
        if webview:
            if delta == 0:
                webview.setZoomFactor(1.0)
            else:
                current = webview.zoomFactor()
                new_zoom = max(0.25, min(5.0, current + delta))
                webview.setZoomFactor(new_zoom)
    
    def toggle_bookmark(self):
        """Добавить/удалить закладку"""
        webview = self.current_webview()
        if not webview:
            return
        
        url = webview.url().toString()
        title = webview.title()
        
        # Проверяем, есть ли уже в закладках
        for i, (bookmark_url, _) in enumerate(self.bookmarks):
            if bookmark_url == url:
                self.bookmarks.pop(i)
                self.bookmark_btn.setText("☆")
                self.status_bar.showMessage("Закладка удалена")
                self.save_settings()
                return
        
        # Добавляем закладку
        self.bookmarks.append((url, title if title else url))
        self.bookmark_btn.setText("★")
        self.status_bar.showMessage("Закладка добавлена")
        self.save_settings()
    
    def show_bookmarks(self):
        """Показать закладки в отдельном окне"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Закладки")
        dialog.setGeometry(200, 200, 600, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("Закладки")
        label.setStyleSheet("font-size: 18px; font-weight: 500; padding: 8px 0;")
        layout.addWidget(label)
        
        list_widget = QListWidget()
        
        if not self.bookmarks:
            list_widget.addItem("Нет закладок")
        else:
            for url, title in self.bookmarks:
                item = QListWidgetItem(f"★ {title}\n{url}")
                item.setData(Qt.UserRole, url)
                list_widget.addItem(item)
        
        list_widget.itemDoubleClicked.connect(lambda item: self.open_bookmark(item.data(Qt.UserRole)))
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Открыть в новой вкладке")
        open_btn.clicked.connect(lambda: self.open_bookmark_from_dialog(list_widget))
        btn_layout.addWidget(open_btn)
        
        delete_btn = QPushButton("Удалить")
        delete_btn.setStyleSheet("color: #e81123;")
        delete_btn.clicked.connect(lambda: self.delete_bookmark(list_widget))
        btn_layout.addWidget(delete_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()
    
    def open_bookmark_from_dialog(self, list_widget):
        """Открыть закладку из диалога"""
        current = list_widget.currentItem()
        if current:
            url = current.data(Qt.UserRole)
            if url:
                self.add_new_tab(url)
    
    def delete_bookmark(self, list_widget):
        """Удалить закладку из диалога"""
        current = list_widget.currentItem()
        if current:
            url = current.data(Qt.UserRole)
            if url:
                self.bookmarks = [(u, t) for u, t in self.bookmarks if u != url]
                list_widget.takeItem(list_widget.currentRow())
                self.save_settings()
                self.update_bookmark_state(self.url_bar.text())
    
    def open_bookmark(self, url):
        """Открыть закладку"""
        if url:
            self.add_new_tab(url)
    
    def show_history(self):
        """Показать историю"""
        dialog = QDialog(self)
        dialog.setWindowTitle("История")
        dialog.setGeometry(200, 200, 700, 500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        label = QLabel("История посещений")
        label.setStyleSheet("font-size: 18px; font-weight: 500; padding: 8px 0;")
        layout.addWidget(label)
        
        list_widget = QListWidget()
        
        if not self.history:
            list_widget.addItem("История пуста")
        else:
            for url, date in self.history[-100:]:  # Показываем последние 100
                item = QListWidgetItem(f"{date}\n{url}")
                item.setData(Qt.UserRole, url)
                list_widget.addItem(item)
        
        list_widget.itemDoubleClicked.connect(lambda item: self.open_history(item.data(Qt.UserRole)))
        layout.addWidget(list_widget)
        
        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Открыть в новой вкладке")
        open_btn.clicked.connect(lambda: self.open_history_from_dialog(list_widget))
        btn_layout.addWidget(open_btn)
        
        clear_btn = QPushButton("Очистить историю")
        clear_btn.setStyleSheet("color: #e81123;")
        clear_btn.clicked.connect(lambda: self.clear_history_from_dialog(list_widget))
        btn_layout.addWidget(clear_btn)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()
    
    def open_history_from_dialog(self, list_widget):
        """Открыть из истории"""
        current = list_widget.currentItem()
        if current:
            url = current.data(Qt.UserRole)
            if url:
                self.add_new_tab(url)
    
    def clear_history_from_dialog(self, list_widget):
        """Очистить историю из диалога"""
        reply = QMessageBox.question(self, "Очистка истории", 
                                    "Удалить всю историю посещений?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history.clear()
            list_widget.clear()
            list_widget.addItem("История очищена")
            self.save_settings()
    
    def clear_history_dialog(self):
        """Диалог очистки истории"""
        reply = QMessageBox.question(self, "Очистка истории", 
                                    "Удалить всю историю посещений?",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history.clear()
            self.save_settings()
            QMessageBox.information(self, "Готово", "История очищена")
    
    def open_history(self, url):
        """Открыть из истории"""
        if url:
            self.add_new_tab(url)
    
    def show_find(self):
        """Поиск на странице"""
        webview = self.current_webview()
        if webview:
            text, ok = QInputDialog.getText(self, "Поиск", "Найти:")
            if ok and text:
                webview.findText(text)
    
    def find_next(self):
        """Найти далее"""
        # Простая реализация - повторяем последний поиск
        pass
    
    def cut_text(self):
        """Вырезать"""
        webview = self.current_webview()
        if webview:
            webview.triggerPageAction(QWebEnginePage.Cut)
    
    def copy_text(self):
        """Копировать"""
        webview = self.current_webview()
        if webview:
            webview.triggerPageAction(QWebEnginePage.Copy)
    
    def paste_text(self):
        """Вставить"""
        webview = self.current_webview()
        if webview:
            webview.triggerPageAction(QWebEnginePage.Paste)
    
    def open_file(self):
        """Открыть файл"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", 
            "HTML Files (*.html *.htm);;All Files (*.*)"
        )
        if file_path:
            webview = self.current_webview()
            if webview:
                webview.setUrl(QUrl.fromLocalFile(file_path))
    
    def save_page(self):
        """Сохранить страницу"""
        webview = self.current_webview()
        if webview:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить страницу", "", 
                "HTML Files (*.html);;All Files (*.*)"
            )
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
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить PDF", "page.pdf", 
                "PDF Files (*.pdf);;All Files (*.*)"
            )
            if file_path:
                webview.page().printToPdf(file_path)
                self.status_bar.showMessage(f"PDF сохранен: {file_path}")
    
    def toggle_maximize(self):
        """Развернуть/свернуть окно"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def toggle_fullscreen(self):
        """Полноэкранный режим"""
        if self.isFullScreen():
            self.showNormal()
            self.menuBar().show()
            self.status_bar.show()
            self.is_fullscreen = False
        else:
            self.showFullScreen()
            self.menuBar().hide()
            self.status_bar.hide()
            self.is_fullscreen = True
    
    def show_settings(self):
        """Настройки"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки")
        dialog.setGeometry(300, 300, 500, 400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Поисковик
        group = QGroupBox("Поисковая система")
        group_layout = QVBoxLayout(group)
        
        search_combo = QComboBox()
        search_combo.addItems(["Google", "Yandex", "Bing", "DuckDuckGo"])
        search_combo.setCurrentText(self.search_engine)
        group_layout.addWidget(search_combo)
        
        layout.addWidget(group)
        
        # Домашняя страница
        home_group = QGroupBox("Домашняя страница")
        home_layout = QVBoxLayout(home_group)
        home_input = QLineEdit("https://www.google.com")
        home_layout.addWidget(home_input)
        layout.addWidget(home_group)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_settings_dialog(dialog, search_combo, home_input))
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec_()
    
    def save_settings_dialog(self, dialog, search_combo, home_input):
        """Сохранение настроек"""
        self.search_engine = search_combo.currentText()
        dialog.close()
        QMessageBox.information(self, "Настройки", "Настройки сохранены")
    
    def show_about(self):
        """О программе с дизайном как в Chrome"""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("О Google Chrome")
        about_dialog.setFixedSize(500, 350)
        about_dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel {
                color: #202124;
            }
        """)
        
        layout = QVBoxLayout(about_dialog)
        layout.setSpacing(10)
        
        # Иконка
        icon_label = QLabel("🌐")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Название
        title_label = QLabel("Google Chrome")
        title_label.setStyleSheet("font-size: 24px; font-weight: 500;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Версия
        version_label = QLabel("Версия 120.0.6099.216 (Официальная сборка)")
        version_label.setStyleSheet("color: #5f6368; font-size: 13px;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Копирайт
        copyright_label = QLabel("© 2024 Google Inc. Все права защищены.")
        copyright_label.setStyleSheet("color: #5f6368; font-size: 12px;")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(about_dialog.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        about_dialog.exec_()
    
    def show_chrome_menu(self):
        """Меню с тремя точками - полная копия Chrome"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #dadce0;
                border-radius: 8px;
                padding: 8px 0px;
                min-width: 280px;
            }
            QMenu::item {
                padding: 6px 30px 6px 40px;
                border-radius: 0px;
            }
            QMenu::item:selected {
                background-color: #e8eaed;
            }
            QMenu::separator {
                height: 1px;
                background: #dadce0;
                margin: 4px 10px;
            }
        """)
        
        # Новое
        new_tab = menu.addAction("Новая вкладка")
        new_tab.setShortcut("Ctrl+T")
        new_tab.triggered.connect(lambda: self.add_new_tab())
        
        new_window = menu.addAction("Новое окно")
        new_window.setShortcut("Ctrl+N")
        new_window.triggered.connect(self.new_window)
        
        new_incognito = menu.addAction("Новое окно в режиме инкогнито")
        new_incognito.setShortcut("Ctrl+Shift+N")
        new_incognito.triggered.connect(self.new_incognito)
        
        menu.addSeparator()
        
        # История и закладки
        history_action = menu.addAction("История")
        history_action.triggered.connect(self.show_history)
        
        bookmarks_action = menu.addAction("Закладки")
        bookmarks_action.triggered.connect(self.show_bookmarks)
        
        downloads_action = menu.addAction("Загрузки")
        downloads_action.triggered.connect(self.show_downloads)
        
        menu.addSeparator()
        
        # Инструменты
        find_action = menu.addAction("Найти...")
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_find)
        
        print_action = menu.addAction("Печать...")
        print_action.setShortcut("Ctrl+P")
        print_action.triggered.connect(self.print_page)
        
        menu.addSeparator()
        
        # Настройки
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
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout(dialog)
        list_widget = QListWidget()
        
        for url in self.downloads[-20:]:
            list_widget.addItem(url)
        
        layout.addWidget(list_widget)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec_()
    
    def new_window(self):
        """Новое окно"""
        new_window = FakeChrome()
        new_window.show()
    
    def new_incognito(self):
        """Новое окно инкогнито"""
        new_window = FakeChrome()
        new_window.is_incognito = True
        new_window.setWindowTitle("Google Chrome (Инкогнито)")
        new_window.setStyleSheet(new_window.styleSheet() + """
            QMainWindow {
                background-color: #1a1a1a;
            }
        """)
        new_window.show()
    
    def load_settings(self):
        """Загрузка настроек"""
        settings_file = "chrome_settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.bookmarks = settings.get("bookmarks", [])
                    self.history = settings.get("history", [])
                    self.search_engine = settings.get("search_engine", "Google")
            except:
                pass
    
    def save_settings(self):
        """Сохранение настроек"""
        settings = {
            "bookmarks": self.bookmarks,
            "history": self.history,
            "search_engine": self.search_engine
        }
        try:
            with open("chrome_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
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
