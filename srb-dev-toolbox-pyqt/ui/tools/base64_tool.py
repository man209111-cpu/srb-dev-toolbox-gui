from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QCheckBox, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt
from .base_tool import BaseTool
from core.encoding_handler import Base64Handler
from utils.worker_thread import WorkerThread
from widgets import BigTextEdit
from plugin import IPlugin, plugin


@plugin(
    plugin_id="base64_tool",
    name="Base64 编解码",
    version="1.0.0",
    description="Base64 编码和解码工具",
    author="DevTools",
    icon="🔐"
)
class Base64ToolPlugin(IPlugin):
    def create_widget(self, parent=None):
        return Base64Tool(parent)


class Base64Tool(BaseTool):
    def __init__(self, parent=None):
        self._worker = None
        super().__init__(parent)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        self.input_text = BigTextEdit(placeholder="在此输入或粘贴数据...")
        input_layout.addWidget(self.input_text)

        options_group = QGroupBox("选项")
        options_layout = QHBoxLayout(options_group)

        options_layout.addWidget(QLabel("编码:"))
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['utf-8', 'gbk', 'gb2312', 'latin-1'])
        options_layout.addWidget(self.encoding_combo)

        self.url_safe_check = QCheckBox("URL 安全模式")
        self.url_safe_check.setToolTip("使用 URL 安全的 Base64 编码（+ → -, / → _）")
        options_layout.addWidget(self.url_safe_check)
        options_layout.addStretch()

        btn_group = QGroupBox("操作")
        btn_layout = QHBoxLayout(btn_group)

        self.encode_btn = QPushButton("🔒 编码")
        self.encode_btn.setToolTip("将文本编码为 Base64")
        self.encode_btn.setDefault(True)
        btn_layout.addWidget(self.encode_btn)

        self.decode_btn = QPushButton("🔓 解码")
        self.decode_btn.setToolTip("将 Base64 解码为文本")
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
        url_safe = self.url_safe_check.isChecked()

        self.set_processing(True)
        
        self._worker = WorkerThread(
            Base64Handler.encode,
            input_str,
            encoding=encoding,
            url_safe=url_safe
        )
        self._worker.signals.finished.connect(self._on_finished)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def _decode(self):
        input_str = self.input_text.toPlainText()
        if not input_str.strip():
            self.show_warning("请输入要解码的 Base64 数据")
            return

        encoding = self.encoding_combo.currentText()
        url_safe = self.url_safe_check.isChecked()

        self.set_processing(True)
        
        self._worker = WorkerThread(
            Base64Handler.decode,
            input_str,
            encoding=encoding,
            url_safe=url_safe
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
