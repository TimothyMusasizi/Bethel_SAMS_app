from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDoubleSpinBox,
    QDateEdit, QComboBox, QDialogButtonBox, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt, QDate

from app.models.financial import Financial
from app.database.database import Database


class FinancialRecordDialog(QDialog):
    """Dialog for adding or editing a financial record."""
    
    def __init__(self, financial: Financial = None, parent=None):
        super().__init__(parent)
        self.financial = financial or Financial()
        self.is_edit_mode = financial is not None
        self.setWindowTitle("Edit Offering" if self.is_edit_mode else "Add Offering")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Member selection (dropdown from database)
        self.member_combo = QComboBox()
        db = Database.get_instance()
        members = db.getAllMembers()
        self.member_list = members
        
        for member in members:
            display_name = f"{member.name} ({member.member_id})"
            self.member_combo.addItem(display_name, member)
        
        # Pre-select existing member if editing
        if self.is_edit_mode and self.financial.member_id:
            for i, member in enumerate(members):
                if str(member.member_id) == str(self.financial.member_id):
                    self.member_combo.setCurrentIndex(i)
                    break
        
        form.addRow("Member:", self.member_combo)
        
        # Value input
        self.value_input = QDoubleSpinBox()
        self.value_input.setRange(0, 999999.99)
        self.value_input.setDecimals(2)
        self.value_input.setValue(self.financial.value)
        form.addRow("Amount:", self.value_input)
        
        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        
        if self.financial.date:
            # Parse date string (YYYY-MM-DD)
            date_obj = QDate.fromString(self.financial.date, "yyyy-MM-dd")
            self.date_input.setDate(date_obj)
        else:
            self.date_input.setDate(QDate.currentDate())
        
        form.addRow("Date:", self.date_input)
        
        # Notes input
        self.notes_input = QTextEdit()
        self.notes_input.setPlainText(self.financial.notes or "")
        self.notes_input.setMaximumHeight(100)
        form.addRow("Notes:", self.notes_input)
        
        layout.addLayout(form)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_financial_record(self) -> Financial:
        """Get the updated financial record from the dialog."""
        member = self.member_combo.currentData()
        
        self.financial.member_id = member.member_id
        self.financial.member_name = member.name
        self.financial.value = self.value_input.value()
        self.financial.date = self.date_input.date().toString("yyyy-MM-dd")
        self.financial.notes = self.notes_input.toPlainText()
        
        return self.financial
