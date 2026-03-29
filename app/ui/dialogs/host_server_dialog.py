from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QSpinBox, QComboBox, QDialogButtonBox, QVBoxLayout
from PySide6.QtCore import Qt
from threading import Thread
from server.app import run_server


class HostServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Host Server")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1024, 65535)
        self.port_spin.setValue(5000)

        self.access_combo = QComboBox()
        self.access_combo.addItems(['read', 'read-write'])

        self.host_edit = QLineEdit()
        self.host_edit.setPlaceholderText('0.0.0.0')

        form.addRow('Host', self.host_edit)
        form.addRow('Port', self.port_spin)
        form.addRow('Default access', self.access_combo)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_start)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_start(self):
        host = self.host_edit.text().strip() or '0.0.0.0'
        port = int(self.port_spin.value())
        # start server in thread
        t = Thread(target=run_server, args=(host, port), daemon=True)
        t.start()
        self.accept()
