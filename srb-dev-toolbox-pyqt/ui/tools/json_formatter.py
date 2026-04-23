from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QSpinBox, QCheckBox, QGroupBox
)
from PyQt6.QtCore import Qt
from .base_tool import BaseTool
from core.json_handler import JsonHandler
from utils.worker_thread import WorkerThread
from widgets import BigTextEdit
from plugin import IPlugin, plugin


@plugin(
    plugin_id="json_formatter",
    name="JSON 格式化",
    version="1.0.0",
    description="JSON 格式化、压缩、验证工具",
    author="DevTools",
    icon="📄"
)
class JsonFormatterPlugin(IPlugin):
    def create_widget(self, parent=None):
        return JsonFormatter(parent)


class JsonFormatter(BaseTool):
    def __init__(self, parent=None):
        self._worker = None
        super().__init__(parent)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        input_group = QGroupBox("输入 JSON")
        input_layout = QVBoxLayout(input_group)
        self.input_text = BigTextEdit(placeholder="在此输入或粘贴 JSON 数据...")
        input_layout.addWidget(self.input_text)

        options_group = QGroupBox("格式化选项")
        options_layout = QHBoxLayout(options_group)
        
        options_layout.addWidget(QLabel("缩进:"))
        self.indent_spin = QSpinBox()
        self.indent_spin.setRange(1, 8)
        self.indent_spin.setValue(2)
        self.indent_spin.setSuffix(" 空格")
        options_layout.addWidget(self.indent_spin)

        self.sort_keys_check = QCheckBox("按键名排序")
        options_layout.addWidget(self.sort_keys_check)

        self.ensure_ascii_check = QCheckBox("ASCII 编码（中文转义）")
        options_layout.addWidget(self.ensure_ascii_check)
        options_layout.addStretch()

        btn_group = QGroupBox("操作")
        btn_layout = QHBoxLayout(btn_group)

        self.validate_btn = QPushButton("✓ 验证 JSON")
        self.validate_btn.setToolTip("验证 JSON 格式是否正确")
        btn_layout.addWidget(self.validate_btn)

        self.format_btn = QPushButton("🔄 格式化")
        self.format_btn.setToolTip("格式化 JSON 数据")
        self.format_btn.setDefault(True)
        btn_layout.addWidget(self.format_btn)

        self.minify_btn = QPushButton("📦 压缩")
        self.minify_btn.setToolTip("压缩 JSON，去除空白字符")
        btn_layout.addWidget(self.minify_btn)

        self.copy_btn = QPushButton("📋 复制结果")
        self.copy_btn.setToolTip("复制输出结果到剪贴板")
        btn_layout.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("🗑️ 清除")
        self.clear_btn.setToolTip("清除输入和输出")
        btn_layout.addWidget(self.clear_btn)

        output_group = QGroupBox("输出结果")
        output_layout = QVBoxLayout(output_group)
        self.output_text = BigTextEdit(placeholder="格式化结果将显示在这里...")
        self.output_text.setReadOnly(True)
        output_layout.addWidget(self.output_text)

        layout.addWidget(input_group)
        layout.addWidget(options_group)
        layout.addWidget(btn_group)
        layout.addWidget(output_group, stretch=1)

    def _connect_signals(self):
        self.validate_btn.clicked.connect(self._validate_json)
        self.format_btn.clicked.connect(self._format_json)
        self.minify_btn.clicked.connect(self._minify_json)
        self.copy_btn.clicked.connect(self._copy_result)
        self.clear_btn.clicked.connect(self.clear_all)

    def _validate_json(self):
        input_str = self.input_text.toPlainText()
        if not input_str.strip():
            self.show_warning("请输入 JSON 数据")
            return
        
        is_valid, message = JsonHandler.validate_json(input_str)
        if is_valid:
            self.show_info(message)
        else:
            self.show_error(message)

    def _format_json(self):
        input_str = self.input_text.toPlainText()
        if not input_str.strip():
            self.show_warning("请输入 JSON 数据")
            return

        indent = self.indent_spin.value()
        ensure_ascii = self.ensure_ascii_check.isChecked()
        sort_keys = self.sort_keys_check.isChecked()

        self.set_processing(True)
        
        self._worker = WorkerThread(
            JsonHandler.format_json,
            input_str,
            indent=indent,
            ensure_ascii=ensure_ascii,
            sort_keys=sort_keys
        )
        self._worker.signals.finished.connect(self._on_format_finished)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def _minify_json(self):
        input_str = self.input_text.toPlainText()
        if not input_str.strip():
            self.show_warning("请输入 JSON 数据")
            return

        self.set_processing(True)
        
        self._worker = WorkerThread(JsonHandler.minify_json, input_str)
        self._worker.signals.finished.connect(self._on_format_finished)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def _on_format_finished(self, result):
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

    def clear_all(self):
        self.input_text.clear()
        self.output_text.clear()

    def set_processing(self, processing: bool):
        self.format_btn.setEnabled(not processing)
        self.minify_btn.setEnabled(not processing)
        self.validate_btn.setEnabled(not processing)
        if processing:
            self.format_btn.setText("⏳ 处理中...")
        else:
            self.format_btn.setText("🔄 格式化")
