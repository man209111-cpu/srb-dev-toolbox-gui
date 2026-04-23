from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QGroupBox, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt
from .base_tool import BaseTool
from core.encoding_handler import UrlHandler
from utils.worker_thread import WorkerThread
from widgets import BigTextEdit
from plugin import IPlugin, plugin


@plugin(
    plugin_id="url_encoder",
    name="URL 编解码",
    version="1.0.0",
    description="URL 编码和解码工具",
    author="DevTools",
    icon="🌐"
)
class UrlEncoderPlugin(IPlugin):
    def create_widget(self, parent=None):
        return UrlEncoder(parent)


class UrlEncoder(BaseTool):
    def __init__(self, parent=None):
        self._worker = None
        super().__init__(parent)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        self.input_text = BigTextEdit(placeholder="在此输入或粘贴 URL 或文本...")
        input_layout.addWidget(self.input_text)

        options_group = QGroupBox("选项")
        options_layout = QHBoxLayout(options_group)

        options_layout.addWidget(QLabel("编码:"))
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['utf-8', 'gbk', 'gb2312', 'latin-1'])
        options_layout.addWidget(self.encoding_combo)

        options_layout.addWidget(QLabel("保留字符:"))
        self.safe_edit = QLineEdit()
        self.safe_edit.setPlaceholderText("可选，如: /:?&=")
        self.safe_edit.setToolTip("指定不需要编码的字符，常用于 URL 路径")
        options_layout.addWidget(self.safe_edit, stretch=1)
        options_layout.addStretch()

        btn_group = QGroupBox("操作")
        btn_layout = QHBoxLayout(btn_group)

        self.encode_btn = QPushButton("🔒 编码")
        self.encode_btn.setToolTip("将文本编码为 URL 格式")
        self.encode_btn.setDefault(True)
        btn_layout.addWidget(self.encode_btn)

        self.decode_btn = QPushButton("🔓 解码")
        self.decode_btn.setToolTip("将 URL 编码解码为普通文本")
        btn_layout.addWidget(self.decode_btn)

        self.copy_btn = QPushButton("📋 复制结果")
        self.copy_btn.setToolTip("复制输出结果到剪贴板")
        btn_layout.addWidget(self.copy_btn)

        self.swap_btn = QPushButton("↔️ 交换")
        self.swap_btn.setToolTip("将输出内容移到输入框")
        btn_layout.addWidget(self.swap_btn)

        self.clear_btn = QPushButton("🗑️ 清除")
        self.clear_btn.setToolTip("清除输入和输出")
        btn_layout.addWidget(self.clear_btn)

        output_group = QGroupBox("输出结果")
        output_layout = QVBoxLayout(output_group)
        self.output_text = BigTextEdit(placeholder="结果将显示在这里...")
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)

        layout.addWidget(input_group)
        layout.addWidget(options_group)
        layout.addWidget(btn_group)
        layout.addWidget(output_group, stretch=1)

    def _connect_signals(self):
        self.encode_btn.clicked.connect(self._encode)
        self.decode_btn.clicked.connect(self._decode)
        self.copy_btn.clicked.connect(self._copy_result)
        self.swap_btn.clicked.connect(self._swap)
        self.clear_btn.clicked.connect(self.clear_all)

    def _encode(self):
        input_str = self.input_text.toPlainText()
        if not input_str.strip():
            self.show_warning("请输入要编码的数据")
            return

        encoding = self.encoding_combo.currentText()
        safe = self.safe_edit.text() or ''

        self.set_processing(True)
        
        self._worker = WorkerThread(
            UrlHandler.encode,
            input_str,
            encoding=encoding,
            safe=safe
        )
        self._worker.signals.finished.connect(self._on_finished)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def _decode(self):
        input_str = self.input_text.toPlainText()
        if not input_str.strip():
            self.show_warning("请输入要解码的数据")
            return

        encoding = self.encoding_combo.currentText()

        self.set_processing(True)
        
        self._worker = WorkerThread(
            UrlHandler.decode,
            input_str,
            encoding=encoding
        )
        self._worker.signals.finished.connect(self._on_finished)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result):
        self.output_text.setPlainText(result)
        self.set_processing(False)

    def _on_error(self, error_msg):
        self.show_error(error_msg)
        self.set_processing(False)

    def _copy_result(self):
        result = self.output_text.toPlainText()
        if not result.strip():
            self.show_warning("没有可复制的结果")
            return
        self.copy_to_clipboard(result)

    def _swap(self):
        output = self.output_text.toPlainText()
        if not output.strip():
            self.show_warning("输出框为空")
            return
        self.input_text.setPlainText(output)
        self.output_text.clear()

    def clear_all(self):
        self.input_text.clear()
        self.output_text.clear()

    def set_processing(self, processing: bool):
        self.encode_btn.setEnabled(not processing)
        self.decode_btn.setEnabled(not processing)
        if processing:
            self.encode_btn.setText("⏳ 编码中...")
            self.decode_btn.setText("⏳ 解码中...")
        else:
            self.encode_btn.setText("🔒 编码")
            self.decode_btn.setText("🔓 解码")
