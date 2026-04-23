from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QCheckBox, QGroupBox, QSpinBox,
    QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt
from .base_tool import BaseTool
from core.password_generator import PasswordGenerator as PwdGen
from plugin import IPlugin, plugin


@plugin(
    plugin_id="password_generator",
    name="密码生成器",
    version="1.0.0",
    description="安全的随机密码生成器",
    author="DevTools",
    icon="🔒"
)
class PasswordGeneratorPlugin(IPlugin):
    def create_widget(self, parent=None):
        return PasswordGenerator(parent)


class PasswordGenerator(BaseTool):
    def __init__(self, parent=None):
        super().__init__(parent)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        options_group = QGroupBox("密码选项")
        options_layout = QVBoxLayout(options_group)

        length_row = QHBoxLayout()
        length_row.addWidget(QLabel("密码长度:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, 128)
        self.length_spin.setValue(16)
        self.length_spin.setSuffix(" 位")
        length_row.addWidget(self.length_spin)
        length_row.addStretch()
        options_layout.addLayout(length_row)

        chars_row = QHBoxLayout()
        self.upper_check = QCheckBox("大写字母 (A-Z)")
        self.upper_check.setChecked(True)
        chars_row.addWidget(self.upper_check)

        self.lower_check = QCheckBox("小写字母 (a-z)")
        self.lower_check.setChecked(True)
        chars_row.addWidget(self.lower_check)
        options_layout.addLayout(chars_row)

        chars_row2 = QHBoxLayout()
        self.digits_check = QCheckBox("数字 (0-9)")
        self.digits_check.setChecked(True)
        chars_row2.addWidget(self.digits_check)

        self.special_check = QCheckBox("特殊字符 (!@#$%...)")
        self.special_check.setChecked(True)
        chars_row2.addWidget(self.special_check)
        options_layout.addLayout(chars_row2)

        chars_row3 = QHBoxLayout()
        self.exclude_confusing_check = QCheckBox("排除易混淆字符 (0O1lI)")
        chars_row3.addWidget(self.exclude_confusing_check)
        chars_row3.addStretch()
        options_layout.addLayout(chars_row3)

        btn_group = QGroupBox("操作")
        btn_layout = QHBoxLayout(btn_group)

        self.generate_btn = QPushButton("🎲 生成密码")
        self.generate_btn.setToolTip("生成随机密码")
        self.generate_btn.setDefault(True)
        btn_layout.addWidget(self.generate_btn)

        self.copy_btn = QPushButton("📋 复制密码")
        self.copy_btn.setToolTip("复制密码到剪贴板")
        btn_layout.addWidget(self.copy_btn)

        self.clear_btn = QPushButton("🗑️ 清除")
        self.clear_btn.setToolTip("清除密码")
        btn_layout.addWidget(self.clear_btn)

        result_group = QGroupBox("生成结果")
        result_layout = QVBoxLayout(result_group)

        pwd_row = QHBoxLayout()
        pwd_row.addWidget(QLabel("密码:"))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("生成的密码将显示在这里...")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
        self.password_edit.setReadOnly(True)
        self.password_edit.setStyleSheet("font-family: Consolas, Monaco, monospace; font-size: 14px;")
        pwd_row.addWidget(self.password_edit, stretch=1)

        self.show_hide_btn = QPushButton("👁️")
        self.show_hide_btn.setToolTip("显示/隐藏密码")
        self.show_hide_btn.setCheckable(True)
        self.show_hide_btn.setChecked(True)
        pwd_row.addWidget(self.show_hide_btn)
        result_layout.addLayout(pwd_row)

        strength_row = QHBoxLayout()
        strength_row.addWidget(QLabel("密码强度:"))
        self.strength_bar = QProgressBar()
        self.strength_bar.setRange(0, 8)
        self.strength_bar.setValue(0)
        self.strength_bar.setTextVisible(True)
        strength_row.addWidget(self.strength_bar, stretch=1)
        result_layout.addLayout(strength_row)

        self.strength_text = QTextEdit()
        self.strength_text.setReadOnly(True)
        self.strength_text.setMaximumHeight(80)
        self.strength_text.setPlaceholderText("密码强度评估...")
        result_layout.addWidget(self.strength_text)

        layout.addWidget(options_group)
        layout.addWidget(btn_group)
        layout.addWidget(result_group)
        layout.addStretch()

    def _connect_signals(self):
        self.generate_btn.clicked.connect(self._generate_password)
        self.copy_btn.clicked.connect(self._copy_result)
        self.clear_btn.clicked.connect(self.clear_all)
        self.show_hide_btn.clicked.connect(self._toggle_password_visibility)

    def _generate_password(self):
        length = self.length_spin.value()
        use_upper = self.upper_check.isChecked()
        use_lower = self.lower_check.isChecked()
        use_digits = self.digits_check.isChecked()
        use_special = self.special_check.isChecked()
        exclude_confusing = self.exclude_confusing_check.isChecked()

        if not any([use_upper, use_lower, use_digits, use_special]):
            self.show_warning("请至少选择一种字符类型")
            return

        try:
            password = PwdGen.generate(
                length=length,
                use_uppercase=use_upper,
                use_lowercase=use_lower,
                use_digits=use_digits,
                use_special=use_special,
                exclude_confusing=exclude_confusing
            )

            self.password_edit.setText(password)
            
            score, feedback = PwdGen.check_strength(password)
            self.strength_bar.setValue(score)
            
            if score <= 3:
                self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #ff4444; }")
            elif score <= 5:
                self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #ffbb33; }")
            else:
                self.strength_bar.setStyleSheet("QProgressBar::chunk { background-color: #00C851; }")
            
            self.strength_text.setText(feedback)

        except ValueError as e:
            self.show_error(str(e))

    def _toggle_password_visibility(self):
        if self.show_hide_btn.isChecked():
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_hide_btn.setText("👁️")
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_hide_btn.setText("🔒")

    def _copy_result(self):
        password = self.password_edit.text()
        if not password:
            self.show_warning("没有可复制的密码")
            return
        self.copy_to_clipboard(password)

    def clear_all(self):
        self.password_edit.clear()
        self.strength_bar.setValue(0)
        self.strength_text.clear()
