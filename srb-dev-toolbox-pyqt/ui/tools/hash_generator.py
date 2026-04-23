from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QCheckBox, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt
from .base_tool import BaseTool
from core.crypto_handler import HashHandler
from utils.worker_thread import WorkerThread
from plugin import IPlugin, plugin


@plugin(
    plugin_id="hash_generator",
    name="哈希生成器",
    version="1.0.0",
    description="支持多种哈希算法的生成工具",
    author="DevTools",
    icon="🔑"
)
class HashGeneratorPlugin(IPlugin):
    def create_widget(self, parent=None):
        return HashGenerator(parent)


class HashGenerator(BaseTool):
    def __init__(self, parent=None):
        self._worker = None
        super().__init__(parent)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        input_group = QGroupBox("输入")
        input_layout = QVBoxLayout(input_group)
        
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("文本:"))
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("输入要计算哈希的文本...")
        input_row.addWidget(self.input_text, stretch=1)
        input_layout.addLayout(input_row)

        options_group = QGroupBox("选项")
        options_layout = QHBoxLayout(options_group)

        options_layout.addWidget(QLabel("算法:"))
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(HashHandler.get_supported_algorithms())
        self.algorithm_combo.setCurrentText('SHA-256')
        options_layout.addWidget(self.algorithm_combo)

        self.uppercase_check = QCheckBox("大写输出")
        options_layout.addWidget(self.uppercase_check)

        options_layout.addWidget(QLabel("编码:"))
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(['utf-8', 'gbk', 'gb2312', 'latin-1'])
        options_layout.addWidget(self.encoding_combo)
        options_layout.addStretch()

        btn_group = QGroupBox("操作")
        btn_layout = QHBoxLayout(btn_group)

        self.generate_btn = QPushButton("🔐 生成哈希")
        self.generate_btn.setToolTip("生成哈希值")
        self.generate_btn.setDefault(True)
        btn_layout.addWidget(self.generate_btn)

        self.copy_btn = QPushButton("📋 复制结果")
        self.copy_btn.setToolTip("复制哈希值到剪贴板")
        btn_layout.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("🗑️ 清除")
        self.clear_btn.setToolTip("清除输入和输出")
        btn_layout.addWidget(self.clear_btn)

        output_group = QGroupBox("输出结果")
        output_layout = QVBoxLayout(output_group)
        
        result_row = QHBoxLayout()
        result_row.addWidget(QLabel("哈希值:"))
        self.result_label = QLabel("-")
        self.result_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.result_label.setStyleSheet("font-family: Consolas, Monaco, monospace; font-size: 11px;")
        result_row.addWidget(self.result_label, stretch=1)
        output_layout.addLayout(result_row)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("哈希值将显示在这里...")
        self.output_text.setMaximumHeight(100)
        self.output_text.setStyleSheet("font-family: Consolas, Monaco, monospace;")
        output_layout.addWidget(self.output_text)

        layout.addWidget(input_group)
        layout.addWidget(options_group)
        layout.addWidget(btn_group)
        layout.addWidget(output_group)
        layout.addStretch()

    def _connect_signals(self):
        self.generate_btn.clicked.connect(self._generate_hash)
        self.copy_btn.clicked.connect(self._copy_result)
        self.clear_btn.clicked.connect(self.clear_all)

    def _generate_hash(self):
        input_str = self.input_text.text()
        if not input_str:
            self.show_warning("请输入要计算哈希的文本")
            return

        algorithm = self.algorithm_combo.currentText()
        encoding = self.encoding_combo.currentText()
        uppercase = self.uppercase_check.isChecked()

        self.set_processing(True)
        
        self._worker = WorkerThread(
            HashHandler.generate_hash,
            input_str,
            algorithm=algorithm,
            encoding=encoding,
            uppercase=uppercase
        )
        self._worker.signals.finished.connect(self._on_finished)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def _on_finished(self, result):
        self.result_label.setText(result)
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
        self.result_label.setText("-")

    def set_processing(self, processing: bool):
        self.generate_btn.setEnabled(not processing)
        if processing:
            self.generate_btn.setText("⏳ 计算中...")
        else:
            self.generate_btn.setText("🔐 生成哈希")
