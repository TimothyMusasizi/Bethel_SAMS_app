from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QDialogButtonBox, QFileDialog, QGroupBox, QDateEdit, QComboBox
)
from PySide6.QtCore import Qt, QDate

# Importing database module for member ID handling
from app.database.database import Database
from app.models.members import Member
from app.utils.notifier import options_notifier


class EditMemberDialog(QDialog):
    """
    Dialog for editing an existing member.
    Includes:
    - Text fields for member details
    - Date picker for DOB
    - Photo path selector
    - OK / Cancel button box
    """


    def __init__(self,member: Member, parent=None):
        super().__init__(parent)
        self.member = member
        self.setWindowTitle(f"Edit Member  - {member.name}")
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
        # self.new_name_edit.setPlaceholderText("Enter full name")
        self.new_name_edit.setText(member.name or "")

        # --- Contact ---
        self.new_contact_label = QLabel("Contact:")
        self.new_contact_edit = QLineEdit()
        self.new_contact_edit.setInputMask("(+256) 70 000 0000;_")
        self.new_contact_edit.setText(member.contact)

        # --- Email ---
        self.new_email_label = QLabel("Email:")
        self.new_email_edit = QLineEdit()
        self.new_email_edit.setText(member.email)

        # --- Date of Birth ---
        self.new_dob_label = QLabel("Date of Birth:")
        self.new_dob_edit = QDateEdit()
        self.new_dob_edit.setCalendarPopup(True)
        if getattr(member, "dob", None):
            dob_qdate = QDate.fromString(member.dob, "yyyy-MM-dd")
            if dob_qdate.isValid():
                self.new_dob_edit.setDate(dob_qdate)

        # --- Occupation ---
        self.new_occupation_label = QLabel("Occupation:")
        self.new_occupation_edit = QLineEdit()
        self.new_occupation_edit.setText(member.occupation)

        # --- Marital Status ---
        self.new_status_label = QLabel("Marital Status:")
        self.new_status_edit = QLineEdit()
        self.new_status_edit.setText(member.marital_status)

        # --- Duty ---
        self.new_duty_label = QLabel("Duty:")
        self.new_duty_combo = QComboBox()

        # --- Class ---
        self.new_class_label = QLabel("Class:")
        self.new_class_combo = QComboBox()

        # --- Activity Status ---
        self.new_activity_label = QLabel("Activity Status:")
        self.new_activity_combo = QComboBox()

        # populate combos with current options and select member values
        self._populate_option_combos(member)
        options_notifier.options_changed.connect(lambda t: self._populate_option_combos(self.member))

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
        self.new_photo_edit.setText(getattr(member, "photo_path", "") or "")

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

        # if self.member:
        #     self.load_member_data(self.member)

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

    # def load_member_data(self, member: Member):
    #     """Load existing member data into the dialog fields."""
    #     self.new_name_edit.setText(member.name or "")
    #     self.new_contact_edit.setText(member.contact or "")
    #     self.new_email_edit.setText(member.email or "")
    #     if member.dob:
    #         dob = QDate.fromString(member.dob, "yyyy-MM-dd")
    #         self.new_dob_edit.setDate(dob)
    #     self.new_occupation_edit.setText(member.occupation or "")
    #     self.new_status_edit.setText(member.marital_status or "")
    #     self.new_class_edit.setText(member.member_class or "")
    #     self.new_activity_edit.setText(member.activity_status or "")
    #     self.new_photo_edit.setText(member.photo_path or "")

    def accept(self):
        """
        Handle the acceptance of the dialog, updating the member and saving changes to the database.
        """
        member_data = {
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

        # Assuming self.member is the Member instance being edited
        # assign fields explicitly (member model expects duty, member_class, activity_status)
        self.member.name = member_data["name"]
        self.member.contact = member_data["contact"]
        self.member.email = member_data["email"]
        self.member.dob = member_data["dob"]
        self.member.occupation = member_data["occupation"]
        self.member.marital_status = member_data["marital_status"]
        self.member.duty = member_data["duty"]
        self.member.member_class = member_data["member_class"]
        self.member.activity_status = member_data["activity_status"]
        self.member.photo_path = member_data["photo_path"]

        db = Database()
        db.updateMember(self.member)  # Assuming this method exists
        try:
            options_notifier.members_changed.emit(self.member.member_id if getattr(self.member, 'member_id', None) else '')
        except Exception:
            pass
        super().accept()

    def _populate_option_combos(self, member: Member):
        db = Database()
        try:
            duties = db.get_options('duties') or []
        except Exception:
            duties = []
        self.new_duty_combo.clear()
        self.new_duty_combo.addItems(duties)
        if getattr(member, 'duty', None):
            idx = self.new_duty_combo.findText(member.duty)
            if idx >= 0:
                self.new_duty_combo.setCurrentIndex(idx)

        try:
            classes = db.get_options('classes') or []
        except Exception:
            classes = []
        self.new_class_combo.clear()
        self.new_class_combo.addItems(classes)
        if getattr(member, 'member_class', None):
            idx = self.new_class_combo.findText(member.member_class)
            if idx >= 0:
                self.new_class_combo.setCurrentIndex(idx)

        try:
            acts = db.get_options('activity_options') or []
        except Exception:
            acts = []
        self.new_activity_combo.clear()
        self.new_activity_combo.addItems(acts)
        if getattr(member, 'activity_status', None):
            idx = self.new_activity_combo.findText(member.activity_status)
            if idx >= 0:
                self.new_activity_combo.setCurrentIndex(idx)