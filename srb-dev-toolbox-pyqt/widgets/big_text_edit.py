from PyQt6.QtWidgets import QPlainTextEdit, QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QKeyEvent, QClipboard
from typing import Optional
import re


class TextLoadWorker(QObject):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, text: str):
        super().__init__()
        self._text = text
        self._cancelled = False
    
    def process(self) -> str:
        return self._text
    
    def cancel(self):
        self._cancelled = True


class BigTextEdit(QPlainTextEdit):
    LARGE_TEXT_THRESHOLD = 100 * 1024  # 100KB 以上视为大文本
    WARNING_THRESHOLD = 5 * 1024 * 1024  # 5MB 警告
    HARD_LIMIT = 50 * 1024 * 1024  # 50MB 硬限制
    
    text_loaded = pyqtSignal()
    loading_progress = pyqtSignal(int)
    
    def __init__(self, parent=None, placeholder: str = ""):
        super().__init__(parent)
        self._placeholder = placeholder
        self.setPlaceholderText(placeholder)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._loading = False
        self._pending_text: Optional[str] = None
        self._load_timer = QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.timeout.connect(self._process_pending_text)
        
        self.setStyleSheet("""
            QPlainTextEdit {
                font-family: Consolas, Monaco, 'Courier New', monospace;
                font-size: 12px;
                padding: 4px;
            }
        """)

    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeyEvent.StandardKey.Paste):
            self._handle_paste()
            event.accept()
            return
        super().keyPressEvent(event)

    def _handle_paste(self):
        clipboard = QApplication.clipboard()
        if clipboard:
            mime_data = clipboard.mimeData()
            if mime_data and mime_data.hasText():
                text = mime_data.text()
                self._insert_text_safely(text)

    def _insert_text_safely(self, text: str):
        text_size = len(text.encode('utf-8'))
        
        if text_size > self.HARD_LIMIT:
            QMessageBox.warning(
                self, "文本过大",
                f"文本大小 ({self._format_size(text_size)}) 超过限制 ({self._format_size(self.HARD_LIMIT)})"
            )
            return
        
        if text_size > self.WARNING_THRESHOLD:
            reply = QMessageBox.question(
                self, "大文本警告",
                f"您正在粘贴较大的文本 ({self._format_size(text_size)})。\n"
                "这可能需要一些时间处理。是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        if text_size > self.LARGE_TEXT_THRESHOLD:
            self._insert_large_text(text)
        else:
            self.insertPlainText(text)

    def _insert_large_text(self, text: str):
        cursor = self.textCursor()
        cursor.insertText(text)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()
        self.text_loaded.emit()

    def _process_pending_text(self):
        if self._pending_text is not None:
            text = self._pending_text
            self._pending_text = None
            self._insert_large_text(text)

    def setPlainText(self, text: str):
        text_size = len(text.encode('utf-8')) if text else 0
        
        if text_size > self.HARD_LIMIT:
            QMessageBox.warning(
                self, "文本过大",
                f"文本大小 ({self._format_size(text_size)}) 超过限制 ({self._format_size(self.HARD_LIMIT)})"
            )
            return
        
        if text_size > self.LARGE_TEXT_THRESHOLD:
            self._loading = True
            self.setPlaceholderText(f"正在加载文本 ({self._format_size(text_size)})...")
            super().setPlainText("")
            QApplication.processEvents()
            super().setPlainText(text)
            self.setPlaceholderText(self._placeholder)
            self._loading = False
            self.text_loaded.emit()
        else:
            super().setPlainText(text)

    def insertFromMimeData(self, source):
        if source and source.hasText():
            text = source.text()
            self._insert_text_safely(text)
        else:
            super().insertFromMimeData(source)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
