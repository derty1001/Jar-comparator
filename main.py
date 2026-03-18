# main.py
import sys
import json
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFileDialog, QTextEdit,
    QLineEdit, QCheckBox, QComboBox, QProgressBar, QMessageBox,
    QMenuBar, QMenu, QDialog, QDialogButtonBox, QRadioButton,
    QGroupBox, QSplitter, QFrame, QStatusBar, QToolBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QDragEnterEvent, QDropEvent, QAction, QIcon

CONFIG_DIR = Path(os.environ.get('APPDATA', Path.home() / '.config')) / 'JarComparator'
CONFIG_FILE = CONFIG_DIR / 'config.json'

DEFAULT_CONFIG = {
    "theme": "dark",
    "hash_display_mode": "inline",
    "recent_files": []
}


class Config:
    def __init__(self):
        self.data = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except:
                pass

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def add_recent(self, file1, file2):
        pair = [str(file1), str(file2)]
        recent = self.data.get('recent_files', [])
        recent = [r for r in recent if r != pair]
        recent.insert(0, pair)
        recent = recent[:10]
        self.data['recent_files'] = recent
        self.save()


config = Config()


class ThemeManager:
    DARK = {
        'bg_primary': '#1a1a2e',
        'bg_secondary': '#16213e',
        'bg_tertiary': '#0f3460',
        'accent': '#9d4edd',
        'accent_light': '#c77dff',
        'text': '#e0e0e0',
        'text_secondary': '#a0a0a0',
        'success': '#4ade80',
        'error': '#f87171',
        'warning': '#fbbf24',
        'border': '#533483'
    }

    LIGHT = {
        'bg_primary': '#ffffff',
        'bg_secondary': '#fff7ed',
        'bg_tertiary': '#ffedd5',
        'accent': '#f97316',
        'accent_light': '#fb923c',
        'text': '#1f2937',
        'text_secondary': '#6b7280',
        'success': '#22c55e',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'border': '#fdba74'
    }

    @classmethod
    def apply(cls, app, theme_name):
        colors = cls.DARK if theme_name == 'dark' else cls.LIGHT

        app.setStyle('Fusion')
        palette = QPalette()

        palette.setColor(QPalette.ColorRole.Window, QColor(colors['bg_primary']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['bg_secondary']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['bg_tertiary']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['text']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['accent']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['text']))

        app.setPalette(palette)

        app.setStyleSheet(f"""
            QMainWindow, QDialog {{
                background-color: {colors['bg_primary']};
            }}
            QPushButton {{
                background-color: {colors['accent']};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {colors['accent_light']};
            }}
            QPushButton:disabled {{
                background-color: {colors['bg_tertiary']};
                color: {colors['text_secondary']};
            }}
            QPushButton#secondary {{
                background-color: {colors['bg_tertiary']};
                border: 2px solid {colors['accent']};
            }}
            QPushButton#secondary:hover {{
                background-color: {colors['accent']};
            }}
            QPushButton#back {{
                background-color: transparent;
                border: 2px solid {colors['accent']};
                color: {colors['accent']};
                min-width: 40px;
                max-width: 40px;
                padding: 5px;
                font-size: 16px;
            }}
            QPushButton#back:hover {{
                background-color: {colors['accent']};
                color: white;
            }}
            QLineEdit, QTextEdit {{
                background-color: {colors['bg_secondary']};
                color: {colors['text']};
                border: 2px solid {colors['border']};
                border-radius: 6px;
                padding: 8px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {colors['accent']};
            }}
            QGroupBox {{
                color: {colors['accent']};
                font-weight: bold;
                border: 2px solid {colors['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QCheckBox {{
                color: {colors['text']};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QComboBox {{
                background-color: {colors['bg_secondary']};
                color: {colors['text']};
                border: 2px solid {colors['border']};
                border-radius: 6px;
                padding: 6px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['accent']};
            }}
            QProgressBar {{
                border: 2px solid {colors['border']};
                border-radius: 6px;
                text-align: center;
                color: {colors['text']};
            }}
            QProgressBar::chunk {{
                background-color: {colors['accent']};
                border-radius: 4px;
            }}
            QMenuBar {{
                background-color: {colors['bg_secondary']};
                color: {colors['text']};
            }}
            QMenuBar::item:selected {{
                background-color: {colors['accent']};
            }}
            QMenu {{
                background-color: {colors['bg_secondary']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
            }}
            QMenu::item:selected {{
                background-color: {colors['accent']};
            }}
            QLabel#title {{
                color: {colors['accent']};
                font-size: 24px;
                font-weight: bold;
            }}
            QLabel#subtitle {{
                color: {colors['text_secondary']};
                font-size: 14px;
            }}
            QScrollBar:vertical {{
                background-color: {colors['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors['accent']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        return colors


class DropLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.jar'):
                self.setText(file_path)


class HashCompareWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str, str, bool)
    error = pyqtSignal(str)

    def __init__(self, file1, file2, algorithm):
        super().__init__()
        self.file1 = file1
        self.file2 = file2
        self.algorithm = algorithm

    def run(self):
        try:
            import hashlib

            self.progress.emit(25)

            def get_hash(filepath, algo):
                hasher = hashlib.new(algo)
                with open(filepath, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
                return hasher.hexdigest()

            hash1 = get_hash(self.file1, self.algorithm)
            self.progress.emit(60)

            hash2 = get_hash(self.file2, self.algorithm)
            self.progress.emit(100)

            match = hash1 == hash2
            self.finished.emit(hash1, hash2, match)

        except Exception as e:
            self.error.emit(str(e))


class ContentCompareWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, file1, file2, show_all):
        super().__init__()
        self.file1 = file1
        self.file2 = file2
        self.show_all = show_all

    def run(self):
        try:
            import zipfile
            import hashlib

            def get_jar_contents(jar_path, prefix=""):
                files = {}
                try:
                    with zipfile.ZipFile(jar_path, 'r') as zf:
                        for info in zf.infolist():
                            if info.is_dir():
                                continue

                            full_path = f"{prefix}{info.filename}" if prefix else info.filename

                            data = zf.read(info.filename)
                            file_hash = hashlib.sha256(data).hexdigest()
                            files[full_path] = file_hash

                            if info.filename.startswith('META-INF/jars/') and info.filename.endswith('.jar'):
                                try:
                                    nested_files = get_jar_contents_from_data(data, f"{full_path}/")
                                    files.update(nested_files)
                                except:
                                    pass
                except Exception as e:
                    raise Exception(f"Ошибка чтения {jar_path}: {e}")
                return files

            def get_jar_contents_from_data(data, prefix):
                files = {}
                import io
                with zipfile.ZipFile(io.BytesIO(data), 'r') as zf:
                    for info in zf.infolist():
                        if info.is_dir():
                            continue
                        full_path = f"{prefix}{info.filename}"
                        file_data = zf.read(info.filename)
                        file_hash = hashlib.sha256(file_data).hexdigest()
                        files[full_path] = file_hash

                        if info.filename.startswith('META-INF/jars/') and info.filename.endswith('.jar'):
                            try:
                                nested = get_jar_contents_from_data(file_data, f"{full_path}/")
                                files.update(nested)
                            except:
                                pass
                return files

            self.progress.emit(10, "Чтение первого JAR...")
            files1 = get_jar_contents(self.file1)
            self.progress.emit(40, "Чтение второго JAR...")

            files2 = get_jar_contents(self.file2)
            self.progress.emit(70, "Сравнение файлов...")

            all_files = set(files1.keys()) | set(files2.keys())
            total = len(all_files)

            result = {
                'same': [],
                'different': [],
                'only_in_1': [],
                'only_in_2': [],
                'files1_count': len(files1),
                'files2_count': len(files2),
                'show_all': self.show_all
            }

            for i, filename in enumerate(sorted(all_files)):
                progress = 70 + int((i / total) * 30)
                self.progress.emit(progress, f"Обработка {i + 1}/{total}...")

                in1 = filename in files1
                in2 = filename in files2

                if in1 and in2:
                    if files1[filename] == files2[filename]:
                        result['same'].append((filename, files1[filename]))
                    else:
                        result['different'].append((filename, files1[filename], files2[filename]))
                elif in1:
                    result['only_in_1'].append((filename, files1[filename]))
                else:
                    result['only_in_2'].append((filename, files2[filename]))

            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class ModeSelectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JAR Comparator")
        self.setMinimumSize(600, 400)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("🔧 JAR Comparator")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Выберите режим сравнения")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(30)

        btn_layout = QHBoxLayout()

        self.btn_hash = QPushButton("📦 Сравнить хеши\nJAR файлов")
        self.btn_hash.setMinimumSize(200, 150)
        self.btn_hash.setFont(QFont("Arial", 12))
        self.btn_hash.clicked.connect(self.open_hash_compare)
        btn_layout.addWidget(self.btn_hash)

        self.btn_content = QPushButton("📋 Сравнить содержимое\nJAR файлов")
        self.btn_content.setMinimumSize(200, 150)
        self.btn_content.setFont(QFont("Arial", 12))
        self.btn_content.clicked.connect(self.open_content_compare)
        btn_layout.addWidget(self.btn_content)

        layout.addLayout(btn_layout)

        layout.addStretch()

        settings_layout = QHBoxLayout()

        theme_btn = QPushButton("🎨 Сменить тему")
        theme_btn.setObjectName("secondary")
        theme_btn.clicked.connect(self.toggle_theme)
        settings_layout.addWidget(theme_btn)

        settings_layout.addStretch()

        layout.addLayout(settings_layout)

        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def apply_theme(self):
        theme = config.get('theme', 'dark')
        self.colors = ThemeManager.apply(QApplication.instance(), theme)

    def toggle_theme(self):
        current = config.get('theme', 'dark')
        new_theme = 'light' if current == 'dark' else 'dark'
        config.set('theme', new_theme)
        self.apply_theme()
        # Перезапуск НЕ нужен, тема применяется сразу

    def open_hash_compare(self):
        self.window = HashCompareWindow()
        self.window.show()
        self.hide()

    def open_content_compare(self):
        self.window = ContentCompareWindow()
        self.window.show()
        self.hide()


class BaseCompareWindow(QMainWindow):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.worker = None

    def setup_navigation(self):
        # Кнопка назад слева сверху
        self.back_btn = QPushButton("←")
        self.back_btn.setObjectName("back")
        self.back_btn.setToolTip("Назад к выбору режима")
        self.back_btn.clicked.connect(self.go_back)

        # Добавляем в layout центрального виджета
        # Должно быть вызвано после setCentralWidget

    def setup_menus(self):
        menubar = self.menuBar()

        # Меню История
        history_menu = menubar.addMenu("История")
        self.update_history_menu(history_menu)

        # Меню Файл только с выходом
        file_menu = menubar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def update_history_menu(self, menu):
        menu.clear()
        recent = config.get('recent_files', [])
        if not recent:
            empty = QAction("(нет истории)", self)
            empty.setEnabled(False)
            menu.addAction(empty)
        else:
            for i, (f1, f2) in enumerate(recent[:5], 1):
                action = QAction(f"{i}. {os.path.basename(f1)} ↔ {os.path.basename(f2)}", self)
                action.triggered.connect(lambda checked, a=f1, b=f2: self.load_recent(a, b))
                menu.addAction(action)

            menu.addSeparator()
            clear_action = QAction("Очистить историю", self)
            clear_action.triggered.connect(self.clear_history)
            menu.addAction(clear_action)

    def load_recent(self, f1, f2):
        raise NotImplementedError

    def clear_history(self):
        config.set('recent_files', [])
        self.update_history_menu(self.history_menu)

    def go_back(self):
        self.window = ModeSelectWindow()
        self.window.show()
        self.close()

    def apply_theme(self):
        theme = config.get('theme', 'dark')
        self.colors = ThemeManager.apply(QApplication.instance(), theme)


class HashCompareWindow(BaseCompareWindow):
    def __init__(self):
        super().__init__("Сравнение хешей JAR файлов")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Навигация
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.back_btn.setObjectName("back")
        self.back_btn.setToolTip("Назад к выбору режима")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        self.setup_menus()

        input_group = QGroupBox("Выбор файлов")
        input_layout = QVBoxLayout(input_group)

        row1 = QHBoxLayout()
        self.file1_input = DropLineEdit()
        self.file1_input.setPlaceholderText("Перетащите первый JAR файл или нажмите Обзор...")
        row1.addWidget(QLabel("Файл 1:"))
        row1.addWidget(self.file1_input)
        btn1 = QPushButton("Обзор...")
        btn1.clicked.connect(lambda: self.browse_file(self.file1_input))
        row1.addWidget(btn1)
        input_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.file2_input = DropLineEdit()
        self.file2_input.setPlaceholderText("Перетащите второй JAR файл или нажмите Обзор...")
        row2.addWidget(QLabel("Файл 2:"))
        row2.addWidget(self.file2_input)
        btn2 = QPushButton("Обзор...")
        btn2.clicked.connect(lambda: self.browse_file(self.file2_input))
        row2.addWidget(btn2)
        input_layout.addLayout(row2)

        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Алгоритм:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["SHA256", "MD5"])
        self.algo_combo.setCurrentIndex(0)
        algo_layout.addWidget(self.algo_combo)
        algo_layout.addStretch()
        input_layout.addLayout(algo_layout)

        layout.addWidget(input_group)

        self.compare_btn = QPushButton("🔍 Сравнить хеши")
        self.compare_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.compare_btn.clicked.connect(self.compare)
        layout.addWidget(self.compare_btn)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.result_label.setVisible(False)
        layout.addWidget(self.result_label)

        self.hashes_box = QTextEdit()
        self.hashes_box.setPlaceholderText("Хеши файлов появятся здесь...")
        self.hashes_box.setMaximumHeight(150)
        layout.addWidget(self.hashes_box)

        self.copy_btn = QPushButton("📋 Копировать результаты")
        self.copy_btn.clicked.connect(self.copy_results)
        self.copy_btn.setVisible(False)
        layout.addWidget(self.copy_btn)

    def setup_menus(self):
        menubar = self.menuBar()

        history_menu = menubar.addMenu("История")
        self.history_menu = history_menu
        self.update_history_menu(history_menu)

        file_menu = menubar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def update_history_menu(self, menu=None):
        if menu is None:
            menu = self.history_menu
        menu.clear()
        recent = config.get('recent_files', [])
        if not recent:
            empty = QAction("(нет истории)", self)
            empty.setEnabled(False)
            menu.addAction(empty)
        else:
            for i, (f1, f2) in enumerate(recent[:5], 1):
                action = QAction(f"{i}. {os.path.basename(f1)} ↔ {os.path.basename(f2)}", self)
                action.triggered.connect(lambda checked, a=f1, b=f2: self.load_recent(a, b))
                menu.addAction(action)

            menu.addSeparator()
            clear_action = QAction("Очистить историю", self)
            clear_action.triggered.connect(self.clear_history)
            menu.addAction(clear_action)

    def load_recent(self, f1, f2):
        self.file1_input.setText(f1)
        self.file2_input.setText(f2)

    def browse_file(self, line_edit):
        file, _ = QFileDialog.getOpenFileName(
            self, "Выберите JAR файл", "", "JAR files (*.jar);;All files (*.*)"
        )
        if file:
            line_edit.setText(file)

    def compare(self):
        f1 = self.file1_input.text()
        f2 = self.file2_input.text()

        if not f1 or not f2:
            QMessageBox.warning(self, "Ошибка", "Выберите оба файла!")
            return

        if not os.path.exists(f1) or not os.path.exists(f2):
            QMessageBox.warning(self, "Ошибка", "Один из файлов не найден!")
            return

        self.compare_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.result_label.setVisible(False)
        self.copy_btn.setVisible(False)
        self.hashes_box.clear()

        algo = self.algo_combo.currentText().lower()

        self.worker = HashCompareWorker(f1, f2, algo)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_finished(self, hash1, hash2, match):
        self.progress.setVisible(False)
        self.compare_btn.setEnabled(True)

        algo = self.algo_combo.currentText()
        self.hashes_box.setText(
            f"📄 Хеш первого файла ({algo}):\n{hash1}\n\n"
            f"📄 Хеш второго файла ({algo}):\n{hash2}"
        )

        if match:
            self.result_label.setText("✅ ФАЙЛЫ ИДЕНТИЧНЫ")
            self.result_label.setStyleSheet(f"color: {self.colors['success']};")
        else:
            self.result_label.setText("❌ ФАЙЛЫ РАЗЛИЧНЫ")
            self.result_label.setStyleSheet(f"color: {self.colors['error']};")

        self.result_label.setVisible(True)
        self.copy_btn.setVisible(True)

        config.add_recent(self.file1_input.text(), self.file2_input.text())
        self.update_history_menu()

    def on_error(self, error_msg):
        self.progress.setVisible(False)
        self.compare_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", error_msg)

    def copy_results(self):
        text = self.hashes_box.toPlainText()
        if self.result_label.text():
            text = f"{self.result_label.text()}\n\n{text}"
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Скопировано", "Результаты скопированы в буфер обмена!")


class ContentCompareWindow(BaseCompareWindow):
    def __init__(self):
        super().__init__("Сравнение содержимого JAR файлов")
        self.setMinimumSize(900, 700)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Навигация
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("←")
        self.back_btn.setObjectName("back")
        self.back_btn.setToolTip("Назад к выбору режима")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        self.setup_menus()

        input_group = QGroupBox("Выбор файлов")
        input_layout = QVBoxLayout(input_group)

        row1 = QHBoxLayout()
        self.file1_input = DropLineEdit()
        self.file1_input.setPlaceholderText("Перетащите первый JAR файл...")
        row1.addWidget(QLabel("Файл 1:"))
        row1.addWidget(self.file1_input)
        btn1 = QPushButton("Обзор...")
        btn1.clicked.connect(lambda: self.browse_file(self.file1_input))
        row1.addWidget(btn1)
        input_layout.addLayout(row1)

        row2 = QHBoxLayout()
        self.file2_input = DropLineEdit()
        self.file2_input.setPlaceholderText("Перетащите второй JAR файл...")
        row2.addWidget(QLabel("Файл 2:"))
        row2.addWidget(self.file2_input)
        btn2 = QPushButton("Обзор...")
        btn2.clicked.connect(lambda: self.browse_file(self.file2_input))
        row2.addWidget(btn2)
        input_layout.addLayout(row2)

        settings_layout = QHBoxLayout()
        self.show_all_check = QCheckBox("📋 Показывать все файлы (включая идентичные)")
        settings_layout.addWidget(self.show_all_check)
        settings_layout.addStretch()
        input_layout.addLayout(settings_layout)

        layout.addWidget(input_group)

        self.compare_btn = QPushButton("🔍 Сравнить содержимое")
        self.compare_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.compare_btn.clicked.connect(self.compare)
        layout.addWidget(self.compare_btn)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        self.results_box = QTextEdit()
        self.results_box.setPlaceholderText("Результаты сравнения появятся здесь...")
        self.results_box.setFont(QFont("Consolas", 10))
        layout.addWidget(self.results_box)

        self.copy_btn = QPushButton("📋 Копировать результаты")
        self.copy_btn.clicked.connect(self.copy_results)
        self.copy_btn.setVisible(False)
        layout.addWidget(self.copy_btn)

    def setup_menus(self):
        menubar = self.menuBar()

        history_menu = menubar.addMenu("История")
        self.history_menu = history_menu
        self.update_history_menu(history_menu)

        file_menu = menubar.addMenu("Файл")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def update_history_menu(self, menu=None):
        if menu is None:
            menu = self.history_menu
        menu.clear()
        recent = config.get('recent_files', [])
        if not recent:
            empty = QAction("(нет истории)", self)
            empty.setEnabled(False)
            menu.addAction(empty)
        else:
            for i, (f1, f2) in enumerate(recent[:5], 1):
                action = QAction(f"{i}. {os.path.basename(f1)} ↔ {os.path.basename(f2)}", self)
                action.triggered.connect(lambda checked, a=f1, b=f2: self.load_recent(a, b))
                menu.addAction(action)

            menu.addSeparator()
            clear_action = QAction("Очистить историю", self)
            clear_action.triggered.connect(self.clear_history)
            menu.addAction(clear_action)

    def load_recent(self, f1, f2):
        self.file1_input.setText(f1)
        self.file2_input.setText(f2)

    def browse_file(self, line_edit):
        file, _ = QFileDialog.getOpenFileName(
            self, "Выберите JAR файл", "", "JAR files (*.jar);;All files (*.*)"
        )
        if file:
            line_edit.setText(file)

    def compare(self):
        f1 = self.file1_input.text()
        f2 = self.file2_input.text()

        if not f1 or not f2:
            QMessageBox.warning(self, "Ошибка", "Выберите оба файла!")
            return

        if not os.path.exists(f1) or not os.path.exists(f2):
            QMessageBox.warning(self, "Ошибка", "Один из файлов не найден!")
            return

        self.compare_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_label.setText("Начинаем сравнение...")
        self.results_box.clear()
        self.copy_btn.setVisible(False)

        show_all = self.show_all_check.isChecked()

        self.worker = ContentCompareWorker(f1, f2, show_all)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, value, message):
        self.progress.setValue(value)
        self.status_label.setText(message)

    def on_finished(self, result):
        self.progress.setVisible(False)
        self.compare_btn.setEnabled(True)
        self.status_label.setText("")

        colors = self.colors

        lines = []
        lines.append("📊 СТАТИСТИКА СРАВНЕНИЯ")
        lines.append("")
        lines.append(f"   📁 Всего файлов в первом JAR:  {result['files1_count']}")
        lines.append(f"   📁 Всего файлов во втором JAR: {result['files2_count']}")
        lines.append(f"   ✅ Идентичных файлов:         {len(result['same'])}")
        lines.append(f"   ❌ Файлов с различиями:       {len(result['different'])}")
        lines.append(f"   📂 Только в первом JAR:       {len(result['only_in_1'])}")
        lines.append(f"   📂 Только во втором JAR:      {len(result['only_in_2'])}")
        lines.append("")

        if len(result['different']) == 0 and len(result['only_in_1']) == 0 and len(result['only_in_2']) == 0:
            lines.append("🎉 ФАЙЛЫ ПОЛНОСТЬЮ ИДЕНТИЧНЫ!")
            lines.append("")
        else:
            lines.append("⚠️  НАЙДЕНЫ РАЗЛИЧИЯ")
            lines.append("")

        if result['different'] or result['only_in_1'] or result['only_in_2'] or result['show_all']:
            lines.append("📋 ДЕТАЛЬНЫЙ ОТЧЁТ")
            lines.append("")

            if result['different']:
                lines.append("❌ Файлы с разными хешами:")
                for filename, hash1, hash2 in result['different']:
                    lines.append(f"   {filename}")
                    lines.append(f"      JAR1: {hash1}")
                    lines.append(f"      JAR2: {hash2}")
                    lines.append("")

            if result['only_in_1']:
                lines.append("📂 Только в первом JAR:")
                for filename, hash_val in result['only_in_1']:
                    lines.append(f"   {filename}")
                lines.append("")

            if result['only_in_2']:
                lines.append("📂 Только во втором JAR:")
                for filename, hash_val in result['only_in_2']:
                    lines.append(f"   {filename}")
                lines.append("")

            if result['show_all'] and result['same']:
                lines.append("✅ Идентичные файлы:")
                for filename, hash_val in result['same']:
                    lines.append(f"   {filename}")
                lines.append("")

        self.results_box.setText("\n".join(lines))
        self.copy_btn.setVisible(True)

        config.add_recent(self.file1_input.text(), self.file2_input.text())
        self.update_history_menu()

    def on_error(self, error_msg):
        self.progress.setVisible(False)
        self.compare_btn.setEnabled(True)
        self.status_label.setText("")
        QMessageBox.critical(self, "Ошибка", error_msg)

    def copy_results(self):
        text = self.results_box.toPlainText()
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Скопировано", "Результаты скопированы в буфер обмена!")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    theme = config.get('theme', 'dark')
    ThemeManager.apply(app, theme)

    window = ModeSelectWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()