from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QPushButton, QHBoxLayout, QSizePolicy, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ImageViewerDialog(QDialog):
    """Simple dialog that shows an image in a scrollable area for a clearer view."""
    def __init__(self, pixmap: QPixmap = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Viewer")
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        # Allow the label to be larger than the scroll area so the user can scroll for full-size image
        self.label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.scroll.setWidget(self.label)
        layout.addWidget(self.scroll)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        if pixmap:
            self.setPixmap(pixmap)

    def setPixmap(self, pixmap: QPixmap):
        """Set the image to display. Do not forcibly scale so clarity is preserved."""
        if pixmap is None or pixmap.isNull():
            QMessageBox.warning(self, "Image Error", "Unable to load image.")
            return
        # Show the full pixmap; the QScrollArea will provide scrolling if it's larger than the dialog.
        self.label.setPixmap(pixmap)
        # Ensure the label expands to the pixmap size so scrollbars appear when needed
        self.label.resize(pixmap.size())

    @staticmethod
    def show_from_path(path: str, parent=None):
        pix = QPixmap(path)
        if pix.isNull():
            QMessageBox.warning(parent, "Image Error", "Unable to load image.")
            return None
        dlg = ImageViewerDialog(pix, parent)
        dlg.exec()
        return dlg