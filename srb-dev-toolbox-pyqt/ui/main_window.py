from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QStatusBar, QWidget, 
    QVBoxLayout, QMenuBar, QMenu, QMessageBox, QDialog
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt

from plugin import PluginManager, PluginStatus
from ui.plugin_settings_dialog import PluginSettingsDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("开发者工具箱")
        self.setMinimumSize(1000, 750)
        self.resize(1100, 800)
        
        self._plugin_widgets = {}
        self._init_menu_bar()
        self._init_ui()
        self._init_status_bar()
        self._load_plugins()

    def _init_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("文件(&F)")
        
        plugin_action = QAction("插件管理(&P)", self)
        plugin_action.setShortcut("Ctrl+Shift+P")
        plugin_action.triggered.connect(self._show_plugin_settings)
        file_menu.addAction(plugin_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("编辑(&E)")
        
        clear_all_action = QAction("清除当前(&C)", self)
        clear_all_action.setShortcut("Ctrl+Shift+C")
        clear_all_action.triggered.connect(self._clear_current_tab)
        edit_menu.addAction(clear_all_action)
        
        refresh_action = QAction("刷新插件(&R)", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_plugins)
        edit_menu.addAction(refresh_action)

        help_menu = menu_bar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(False)

        layout.addWidget(self.tab_widget)

    def _init_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 | 选择一个工具开始使用")

    def _load_plugins(self):
        self.tab_widget.clear()
        self._plugin_widgets.clear()
        
        enabled_count = 0
        for plugin_id, plugin_class in PluginManager.get_all_plugins().items():
            if not PluginManager.is_enabled(plugin_id):
                continue
                
            try:
                info = plugin_class.get_info()
                instance = PluginManager.get_instance(plugin_id)
                
                if instance:
                    widget = instance.create_widget(self)
                    self._plugin_widgets[plugin_id] = widget
                    self.tab_widget.addTab(widget, f"{info.icon} {info.name}")
                    enabled_count += 1
            except Exception as e:
                print(f"加载插件 {plugin_id} 失败: {e}")
        
        if enabled_count == 0:
            self.status_bar.showMessage("警告: 没有启用的插件，请在 文件 > 插件管理 中启用插件")
        else:
            self.status_bar.showMessage(f"已加载 {enabled_count} 个插件")

    def _refresh_plugins(self):
        self._load_plugins()

    def _clear_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            current_widget = self.tab_widget.currentWidget()
            if hasattr(current_widget, 'clear_all'):
                current_widget.clear_all()

    def _show_plugin_settings(self):
        dialog = PluginSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._refresh_plugins()

    def _show_about(self):
        enabled_plugins = [
            p.get_info().name for p in PluginManager.get_enabled_plugins()
        ]
        
        plugin_list = "\n".join([f"  • {name}" for name in enabled_plugins]) if enabled_plugins else "  (无)"
        
        QMessageBox.about(
            self,
            "关于开发者工具箱",
            f"""<h2>开发者工具箱</h2>
            <p>版本: 1.0.0</p>
            <p>一个功能强大的开发者工具集合</p>
            <h3>技术栈:</h3>
            <p>Python + PyQt6</p>
            <h3>插件系统:</h3>
            <p>当前已启用插件:</p>
            <pre>{plugin_list}</pre>
            <p style='color: gray; font-size: 11px;'>
            基于 Java 项目 srb-dev-toolbox-gui 重构
            </p>
            """
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出开发者工具箱吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
