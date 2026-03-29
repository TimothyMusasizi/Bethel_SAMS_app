from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QDialogButtonBox, QFileDialog, QGroupBox, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate

# Importing database module for member ID handling
from app.database.database import Database
from app.models.members import Member
from app.utils.notifier import options_notifier


class AddMemberDialog(QDialog):
    """
    Dialog for adding a new member.
    Includes:
    - Text fields for new member details
    - Date picker for DOB
    - Photo path selector
    - OK / Cancel button box
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Member")
        self.setMinimumWidth(450)

        # MAIN LAYOUT
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)

        # ============================================================
        # GROUP: MEMBER INFORMATION
        # ============================================================
        info_group = QGroupBox("Member Information")
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # --- Name ---
        self.new_name_label = QLabel("Name:")
        self.new_name_edit = QLineEdit()
        self.new_name_edit.setPlaceholderText("Enter full name")

        # --- Contact ---
        self.new_contact_label = QLabel("Contact:")
        self.new_contact_edit = QLineEdit()
        self.new_contact_edit.setInputMask("(+256) 70 000 0000;_")

        # --- Email ---
        self.new_email_label = QLabel("Email:")
        self.new_email_edit = QLineEdit()

        # --- Date of Birth ---
        self.new_dob_label = QLabel("Date of Birth:")
        self.new_dob_edit = QDateEdit()
        self.new_dob_edit.setCalendarPopup(True)
        self.new_dob_edit.setDate(QDate.currentDate())

        # --- Occupation ---
        self.new_occupation_label = QLabel("Occupation:")
        self.new_occupation_edit = QLineEdit()

        # --- Marital Status ---
        self.new_status_label = QLabel("Marital Status:")
        self.new_status_edit = QLineEdit()

        # --- Duty ---
        self.new_duty_label = QLabel("Duty:")
        self.new_duty_combo = QComboBox()

        # --- Class ---
        self.new_class_label = QLabel("Class:")
        self.new_class_combo = QComboBox()

        # --- Activity Status ---
        self.new_activity_label = QLabel("Activity Status:")
        self.new_activity_combo = QComboBox()

        # populate combos
        self._populate_option_combos()
        options_notifier.options_changed.connect(lambda t: self._populate_option_combos())

        # Add all to the form layout
        form_layout.addRow(self.new_name_label, self.new_name_edit)
        form_layout.addRow(self.new_contact_label, self.new_contact_edit)
        form_layout.addRow(self.new_email_label, self.new_email_edit)
        form_layout.addRow(self.new_dob_label, self.new_dob_edit)
        form_layout.addRow(self.new_occupation_label, self.new_occupation_edit)
        form_layout.addRow(self.new_status_label, self.new_status_edit)
        form_layout.addRow(self.new_duty_label, self.new_duty_combo)
        form_layout.addRow(self.new_class_label, self.new_class_combo)
        form_layout.addRow(self.new_activity_label, self.new_activity_combo)

        info_group.setLayout(form_layout)

        # ============================================================
        # GROUP: PHOTO
        # ============================================================
        photo_group = QGroupBox("Photo")
        photo_layout = QHBoxLayout()

        self.new_photo_label = QLabel("Photo Path:")
        self.new_photo_edit = QLineEdit()
        self.new_photo_edit.setPlaceholderText("Select an image file...")

        self.new_photo_pushButton = QPushButton("Browse")
        self.new_photo_pushButton.clicked.connect(self.browse_photo)

        photo_layout.addWidget(self.new_photo_edit)
        photo_layout.addWidget(self.new_photo_pushButton)
        photo_group.setLayout(photo_layout)

        # ============================================================
        # BUTTON BOX: OK + CANCEL
        # ============================================================
        self.new_buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        self.new_buttonBox.accepted.connect(self.accept)
        self.new_buttonBox.rejected.connect(self.reject)

        # ============================================================
        # ADD TO MAIN LAYOUT
        # ============================================================
        main_layout.addWidget(info_group)
        main_layout.addWidget(photo_group)
        main_layout.addWidget(self.new_buttonBox)

    # ============================================================
    # PHOTO BROWSER
    # ============================================================
    def browse_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Photo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if path:
            self.new_photo_edit.setText(path)

    def get_member_data(self):
        """
        Retrieve the entered member data as a dictionary.
        """
        return {
            "name": self.new_name_edit.text(),
            "contact": self.new_contact_edit.text(),
            "email": self.new_email_edit.text(),
            "dob": self.new_dob_edit.date().toString("yyyy-MM-dd"),
            "occupation": self.new_occupation_edit.text(),
            "marital_status": self.new_status_edit.text(),
            "duty": self.new_duty_combo.currentText(),
            "member_class": self.new_class_combo.currentText(),
            "activity_status": self.new_activity_combo.currentText(),
            "photo_path": self.new_photo_edit.text(),
        }
    
    def generate_member_id(self):
        """
        Generate a unique member ID based on the database.
        """
        db = Database()
        # Logic to generate a unique member ID can be implemented here
        # For example, using the count of existing members or a UUID
        # This is a placeholder implementation
        existing_members = db.getAllMembers()  # Assuming this method exists
        new_id = f"M{len(existing_members) + 1:05d}"
        return new_id
    
    def accept(self):
        """
        Handle the acceptance of the dialog, creating a new member and adding it to the database.
        """
        member_data = self.get_member_data()
        new_member = Member()
        new_member.member_id = self.generate_member_id()
        new_member.name = member_data["name"]
        new_member.contact = member_data["contact"]
        new_member.email = member_data["email"]
        new_member.dob = member_data["dob"]
        new_member.occupation = member_data["occupation"]
        new_member.marital_status = member_data["marital_status"]
        new_member.duty = member_data.get("duty")
        new_member.member_class = member_data["member_class"]
        new_member.activity_status = member_data["activity_status"]
        new_member.photo_path = member_data["photo_path"]

        db = Database()
        db.addMember(new_member)
        try:
            options_notifier.members_changed.emit(new_member.member_id)
        except Exception:
            pass
        super().accept()

    def _populate_option_combos(self):
        db = Database()
        # duties
        try:
            duties = db.get_options('duties') or []
        except Exception:
            duties = []
        self.new_duty_combo.clear()
        self.new_duty_combo.addItems(duties)

        # classes
        try:
            classes = db.get_options('classes') or []
        except Exception:
            classes = []
        self.new_class_combo.clear()
        self.new_class_combo.addItems(classes)

        # activity
        try:
            acts = db.get_options('activity_options') or []
        except Exception:
            acts = []
        self.new_activity_combo.clear()
        self.new_activity_combo.addItems(acts)