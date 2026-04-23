from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
    QListWidgetItem, QLabel, QPushButton, QGroupBox, QWidget
)
from PyQt6.QtCore import Qt
from plugin import PluginManager, PluginStatus


class PluginSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("插件管理")
        self.setMinimumSize(600, 400)
        self._init_ui()
        self._load_plugins()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        list_group = QGroupBox("已安装插件")
        list_layout = QVBoxLayout(list_group)

        self.plugin_list = QListWidget()
        self.plugin_list.itemClicked.connect(self._on_item_clicked)
        list_layout.addWidget(self.plugin_list)

        layout.addWidget(list_group)

        info_group = QGroupBox("插件信息")
        info_layout = QVBoxLayout(info_group)
        
        self.name_label = QLabel("名称: -")
        info_layout.addWidget(self.name_label)
        
        self.version_label = QLabel("版本: -")
        info_layout.addWidget(self.version_label)
        
        self.author_label = QLabel("作者: -")
        info_layout.addWidget(self.author_label)
        
        self.desc_label = QLabel("描述: -")
        self.desc_label.setWordWrap(True)
        info_layout.addWidget(self.desc_label)

        btn_layout = QHBoxLayout()
        self.toggle_btn = QPushButton("启用")
        self.toggle_btn.clicked.connect(self._toggle_plugin)
        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        info_layout.addLayout(btn_layout)
        layout.addWidget(info_group)

    def _load_plugins(self):
        self.plugin_list.clear()
        for plugin_id, plugin_class in PluginManager.get_all_plugins().items():
            info = plugin_class.get_info()
            item = QListWidgetItem(f"{info.icon} {info.name}")
            item.setData(Qt.ItemDataRole.UserRole, plugin_id)
            
            if PluginManager.is_enabled(plugin_id):
                item.setForeground(Qt.GlobalColor.darkGreen)
                item.setText(f"{info.icon} {info.name} ✓")
            else:
                item.setForeground(Qt.GlobalColor.gray)
                item.setText(f"{info.icon} {info.name} (已禁用)")
            
            self.plugin_list.addItem(item)

    def _on_item_clicked(self, item: QListWidgetItem):
        plugin_id = item.data(Qt.ItemDataRole.UserRole)
        plugin_class = PluginManager.get_plugin(plugin_id)
        
        if plugin_class:
            info = plugin_class.get_info()
            self.name_label.setText(f"名称: {info.name}")
            self.version_label.setText(f"版本: {info.version}")
            self.author_label.setText(f"作者: {info.author}")
            self.desc_label.setText(f"描述: {info.description}")
            
            if PluginManager.is_enabled(plugin_id):
                self.toggle_btn.setText("禁用")
            else:
                self.toggle_btn.setText("启用")
            
            self._selected_plugin_id = plugin_id

    def _toggle_plugin(self):
        if hasattr(self, '_selected_plugin_id'):
            plugin_id = self._selected_plugin_id
            if PluginManager.is_enabled(plugin_id):
                PluginManager.disable_plugin(plugin_id)
            else:
                PluginManager.enable_plugin(plugin_id)
            self._load_plugins()
