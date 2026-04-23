import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from ui.tools import (
    JsonFormatterPlugin,
    Base64ToolPlugin,
    HashGeneratorPlugin,
    PasswordGeneratorPlugin,
    UrlEncoderPlugin,
)
from ui.main_window import MainWindow


def setup_app():
    app = QApplication(sys.argv)
    
    app.setApplicationName("开发者工具箱")
    app.setApplicationDisplayName("开发者工具箱")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DevTools")
    
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    app.setStyle("Fusion")
    
    return app


def main():
    app = setup_app()
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
