from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLineEdit, QMessageBox, QLabel
)
from PySide6.QtCore import Qt
from app.database.database import Database
from app.utils.notifier import options_notifier


class ManageOptionsDialog(QDialog):
    """Generic dialog to manage simple option lists (classes, duties, activity options).

    Usage: ManageOptionsDialog(table_name="classes", title="Manage Classes")
    """

    def __init__(self, table_name: str, title: str, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.setWindowTitle(title)
        self.setMinimumWidth(360)

        self.db = Database.get_instance()

        layout = QVBoxLayout(self)

        self.listWidget = QListWidget()
        layout.addWidget(QLabel("Items:"))
        layout.addWidget(self.listWidget)

        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("New item name...")
        self.btnAdd = QPushButton("Add")
        self.btnRemove = QPushButton("Remove Selected")
        row.addWidget(self.input)
        row.addWidget(self.btnAdd)
        row.addWidget(self.btnRemove)

        layout.addLayout(row)

        self.btnClose = QPushButton("Close")
        layout.addWidget(self.btnClose)

        self.btnAdd.clicked.connect(self.add_item)
        self.btnRemove.clicked.connect(self.remove_selected)
        self.btnClose.clicked.connect(self.accept)

        self.load_items()

    def load_items(self):
        self.listWidget.clear()
        try:
            items = self.db.get_options(self.table_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load items: {e}")
            return
        for it in items:
            self.listWidget.addItem(it)

    def add_item(self):
        name = self.input.text().strip()
        if not name:
            return
        try:
            self.db.add_option(self.table_name, name)
            self.input.clear()
            self.load_items()
            try:
                options_notifier.options_changed.emit(self.table_name)
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add item: {e}")

    def remove_selected(self):
        items = self.listWidget.selectedItems()
        if not items:
            return
        name = items[0].text()
        if QMessageBox.question(self, "Confirm", f"Delete '{name}'?") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.db.remove_option(self.table_name, name)
            self.load_items()
            try:
                options_notifier.options_changed.emit(self.table_name)
            except Exception:
                pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove item: {e}")
