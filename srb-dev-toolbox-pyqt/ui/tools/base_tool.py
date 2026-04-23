from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication
from PyQt6.QtGui import QClipboard
from typing import Optional


class BaseTool(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: Optional[object] = None
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        raise NotImplementedError("子类必须实现 _init_ui 方法")

    def _connect_signals(self):
        raise NotImplementedError("子类必须实现 _connect_signals 方法")

    def show_error(self, message: str):
        QMessageBox.critical(self, "错误", message)

    def show_info(self, message: str):
        QMessageBox.information(self, "提示", message)

    def show_warning(self, message: str):
        QMessageBox.warning(self, "警告", message)

    def show_question(self, message: str) -> bool:
        reply = QMessageBox.question(
            self, "确认", message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def copy_to_clipboard(self, text: str):
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text, QClipboard.Mode.Clipboard)
            self.show_info("已复制到剪贴板")

    def clear_all(self):
        pass

    def set_processing(self, processing: bool):
        pass

    def cancel_worker(self):
        if self._worker and self._worker.isRunning():
            self._worker.terminate()
            self._worker.wait()
