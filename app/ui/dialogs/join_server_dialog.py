from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt
from app.utils.network import request_connect, sync_get_members, sync_post_members


class JoinServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Join Server')
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.host_url = QLineEdit()
        self.host_url.setPlaceholderText('http://hostname:5000')

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Your name')

        self.access_combo = QComboBox()
        self.access_combo.addItems(['read', 'read-write'])

        form.addRow('Server URL', self.host_url)
        form.addRow('Your Name', self.name_edit)
        form.addRow('Requested Access', self.access_combo)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_request)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_request(self):
        url = self.host_url.text().strip()
        name = self.name_edit.text().strip() or 'guest'
        access = self.access_combo.currentText()
        try:
            resp = request_connect(url, name=name, access=access)
            QMessageBox.information(self, 'Requested', f"Request submitted: {resp.get('request_id')}")
            # Optionally, attempt to pull members once approved later
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to send request: {e}')
