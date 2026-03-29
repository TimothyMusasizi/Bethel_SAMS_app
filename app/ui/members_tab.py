from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox,
    QPushButton, QComboBox, QGroupBox, QFormLayout, QFrame, QSizePolicy
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize, Signal

# importing dialogs
from app.ui.dialogs.add_member_dialog import AddMemberDialog
from app.ui.dialogs.edit_member_dialog import EditMemberDialog
from app.ui.dialogs.image_viewer_dialog import ImageViewerDialog

# importing database module for member handling
from app.database.database import Database

# importing graphics module for charts
from app.ui.graphics.charts import MplotCanvas, AttendanceChart

class ClickableLabel(QLabel):
    clicked = Signal()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

class MembersTab(QWidget):
    """
    Modular Members Tab Widget
    Contains:
    - Filters, search, sorting
    - Members list and controls
    - Member information panels
    - Attendance chart placeholder
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Refresh when members change elsewhere
        from app.utils.notifier import options_notifier
        options_notifier.members_changed.connect(lambda _id=None: self.load_members())

        # ===== MAIN LAYOUT =====
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # ============================================================
        # LEFT PANEL
        # ============================================================
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)

        # --- Filter Row ---
        filter_row = QHBoxLayout()
        self.labelFilter = QLabel("Filter by:")
        self.comboFilter = QComboBox()
        self.comboFilter.addItems(["All Members", "Active Only", "Inactive Only", "Visitors"])
        self.comboFilter.currentTextChanged.connect(lambda: self.load_members())

        filter_row.addWidget(self.labelFilter)
        filter_row.addWidget(self.comboFilter)

        # --- Member Count ---
        self.labelMemberCount = QLabel("Members: 0")
        self.labelMemberCount.setStyleSheet("font-weight: bold;")

        # --- Search Bar ---
        self.editSearchMembers = QLineEdit()
        self.editSearchMembers.setPlaceholderText("Search members...")
        self.editSearchMembers.textChanged.connect(lambda: self.load_members())

        # --- Sorting ---
        sort_row = QHBoxLayout()
        sort_label = QLabel("Sort by:")
        self.comboSortMembers = QComboBox()
        self.comboSortMembers.addItems(["Name", "Age", "Class"])
        sort_row.addWidget(sort_label)
        sort_row.addWidget(self.comboSortMembers)
        
        #getting a sort value
        self.comboSortMembers.currentTextChanged.connect(lambda: self.load_members())

        # --- Buttons ---
        self.btnAddMember = QPushButton("Add Member")
        self.btnAddMember.clicked.connect(self.open_add_member_dialog)

        self.btnEditMember = QPushButton("Edit Member")
        self.btnEditMember.clicked.connect(self.open_edit_member_dialog)

        self.btnDeleteMember = QPushButton("Delete Member")
        self.btnDeleteMember.clicked.connect(self.delete_selected_member)

        self.btnExportMember = QPushButton("Export Info")
        self.btnExportMember.clicked.connect(self.export_selected_member_pdf)

        # --- Members List ---
        self.listMembers = QListWidget()
        self.listMembers.setMinimumWidth(230)
        self.listMembers.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.listMembers.itemSelectionChanged.connect(self.load_member_details)


        # Add widgets to left panel
        left_panel.addLayout(filter_row)
        left_panel.addWidget(self.labelMemberCount)
        left_panel.addWidget(self.editSearchMembers)
        left_panel.addLayout(sort_row)
        left_panel.addWidget(self.btnAddMember)
        left_panel.addWidget(self.btnEditMember)
        left_panel.addWidget(self.btnDeleteMember)
        left_panel.addWidget(self.btnExportMember)
        left_panel.addWidget(self.listMembers, stretch=1)

        # ============================================================
        # RIGHT PANEL
        # ============================================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        # ------------------------------------------------------------
        # GROUP 1 — BASIC INFO
        # ------------------------------------------------------------
        groupBasicInfo = QGroupBox("Basic Information")
        basic_layout = QHBoxLayout()

        # --- Photo ---
        self.labelPhoto = ClickableLabel()
        self.labelPhoto.setFixedSize(120, 120)
        self.labelPhoto.setFrameShape(QFrame.StyledPanel)
        self.labelPhoto.setAlignment(Qt.AlignCenter)
        self.labelPhoto.setStyleSheet(
            "background-color: rgba(100, 150, 200, 0.2);"
            "border: 2px solid rgba(100, 150, 200, 0.5);"
            "border-radius: 8px;"
        )
        # default placeholder
        self.labelPhoto.setPixmap(QPixmap().scaled(120, 120, Qt.KeepAspectRatio))
        # store current Image path for viewer
        self.current_photo_path = None
        # open larger viewer when clicked
        self.labelPhoto.clicked.connect(self.open_image_viewer)

        # --- Text Info ---
        basic_info_layout = QFormLayout()
        self.labelMemberName = QLabel("")
        self.labelMemberContact = QLabel("")
        self.labelMemberEmail = QLabel("")

        basic_info_layout.addRow("Name:", self.labelMemberName)
        basic_info_layout.addRow("Contact:", self.labelMemberContact)
        basic_info_layout.addRow("Email:", self.labelMemberEmail)

        basic_layout.addWidget(self.labelPhoto)
        basic_layout.addLayout(basic_info_layout)
        groupBasicInfo.setLayout(basic_layout)

        # ------------------------------------------------------------
        # GROUP 2 — PERSONAL DETAILS
        # ------------------------------------------------------------
        groupPersonal = QGroupBox("Personal Details")
        personal_layout = QFormLayout()

        self.labelMemberId = QLabel("")
        self.labelOccupation = QLabel("")
        self.labelDob = QLabel("")
        self.labelMaritalStatus = QLabel("")
        self.labelDuty = QLabel("")
        self.labelClass = QLabel("")
        self.labelActivityStatus = QLabel("")

        personal_layout.addRow("Member ID:", self.labelMemberId)
        personal_layout.addRow("Occupation:", self.labelOccupation)
        personal_layout.addRow("Date of Birth:", self.labelDob)
        personal_layout.addRow("Marital Status:", self.labelMaritalStatus)
        personal_layout.addRow("Duty:", self.labelDuty)
        personal_layout.addRow("Class:", self.labelClass)
        personal_layout.addRow("Activity:", self.labelActivityStatus)

        groupPersonal.setLayout(personal_layout)

        # ------------------------------------------------------------
        # GROUP 3 — ATTENDANCE CHART
        # ------------------------------------------------------------
        groupAttendance = QGroupBox("Attendance")
        attendance_layout = QVBoxLayout()

        self.attendanceChart = AttendanceChart()
        attendance_layout.addWidget(self.attendanceChart)
        groupAttendance.setLayout(attendance_layout)


        # Add right side group boxes
        right_panel.addWidget(groupBasicInfo)
        right_panel.addWidget(groupPersonal)
        right_panel.addWidget(groupAttendance)

        # ============================================================
        # ADD LEFT & RIGHT PANELS TO MAIN LAYOUT
        # ============================================================
        main_layout.addLayout(left_panel, stretch=0)
        main_layout.addLayout(right_panel, stretch=1)

        # Load members into the list
        self.load_members()


    # Opening the add_member_dialog
    def open_add_member_dialog(self):
        dialog = AddMemberDialog(self)
        if dialog.exec():
            print("add_member_dialog opened")
        else:
            print("add_member_dialog opening failed")

        self.listMembers.update()
        self.load_members()

    #Opening the edit_member_dialog
    def open_edit_member_dialog(self):
        selected_items = self.listMembers.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a member to edit.")
            return  # No item selected

        selected_text = selected_items[0].text()

        # safer parsing: split from the last '(' so names containing '(' are handled
        if "(" in selected_text and selected_text.endswith(")"):
            member_id = selected_text.rsplit("(", 1)[1].rstrip(")")
        else:
            member_id = selected_text.strip()

        db = Database.get_instance()
        try:
            member = db.getMember(member_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Database Error", f"Error fetching member: {e}")
            return

        if not member:
            QMessageBox.warning(self, "Not Found", f"No member found with id: {member_id}")
            return

        try:
            dialog = EditMemberDialog(member, self)
            if dialog.exec():
                print("edit_member_dialog opened")
            else:
                print("edit_member_dialog opening failed")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Dialog Error", f"Failed to open edit dialog: {e}")
            return

        self.listMembers.update()
        self.load_members()

    def delete_selected_member(self):
        selected_items = self.listMembers.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a member to delete.")
            return

        selected_text = selected_items[0].text()
        if "(" in selected_text and selected_text.endswith(")"):
            member_id = selected_text.rsplit("(", 1)[1].rstrip(")")
        else:
            member_id = selected_text.strip()

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete member '{selected_text}'?\n\n"
            "This will permanently remove the member and all their attendance records.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        db = Database.get_instance()
        try:
            db.deleteMember(member_id)
            QMessageBox.information(self, "Deleted", f"Member '{selected_text}' has been deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete member: {e}")
            return

        # Notify other components that members have changed
        from app.utils.notifier import options_notifier
        options_notifier.members_changed.emit(member_id)

        self.load_members()
        # Clear details if the deleted member was selected
        if self.listMembers.selectedItems():
            self.load_member_details()
        else:
            self.clear_member_details()

    def load_members(self):
        """Load members from the database into the members list (with search, filters, sorting)."""
        db = Database.get_instance()
        members = db.getAllMembers() or []

        # Apply search
        search_text = (self.editSearchMembers.text() or "").strip().lower()
        if search_text:
            def matches_search(m):
                name = (getattr(m, "name", "") or "").lower()
                mid = (getattr(m, "member_id", "") or "").lower()
                contact = (getattr(m, "contact", "") or "").lower()
                email = (getattr(m, "email", "") or "").lower()
                return (search_text in name or
                        search_text in mid or
                        search_text in contact or
                        search_text in email)
            members = [m for m in members if matches_search(m)]

        # Apply filter
        filter_text = self.comboFilter.currentText()
        if filter_text == "Active Only":
            members = [m for m in members if getattr(m, "activity_status", "") == "Active"]
        elif filter_text == "Inactive Only":
            members = [m for m in members if getattr(m, "activity_status", "") == "Inactive"]
        elif filter_text == "Visitors":
            members = [m for m in members if getattr(m, "member_class", "") == "Visitor"]

        # Apply sorting
        sort_key = self.comboSortMembers.currentText()
        if sort_key == "Name":
            members.sort(key=lambda m: (getattr(m, "name", "") or "").lower())
        elif sort_key == "Age":
            members.sort(key=lambda m: getattr(m, "dob", "") or "")
        elif sort_key == "Class":
            members.sort(key=lambda m: (getattr(m, "member_class", "") or "").lower())

        # Update UI
        self.listMembers.clear()
        for member in members:
            self.listMembers.addItem(f"{member.name} ({member.member_id})")

        self.labelMemberCount.setText(f"Members: {len(members)}")



    def load_member_details(self):
        """Load selected member details into the right panel."""
        selected_items = self.listMembers.selectedItems()
        if not selected_items:
            return  # No item selected

        selected_text = selected_items[0].text()
        if "(" in selected_text and selected_text.endswith(")"):
            member_id = selected_text.rsplit("(", 1)[1].rstrip(")")
        else:
            member_id = selected_text.strip()

        db = Database.get_instance()
        member = db.getMember(member_id)
        if not member:
            return  # Member not found

        # Update UI with member details
        self.labelMemberName.setText(member.name or "")
        self.labelMemberContact.setText(member.contact or "")
        self.labelMemberEmail.setText(member.email or "")
        self.labelMemberId.setText(member.member_id or "")
        self.labelOccupation.setText(member.occupation or "")
        self.labelDob.setText(member.dob or "")
        self.labelMaritalStatus.setText(member.marital_status or "")
        self.labelDuty.setText("N/A")  # Placeholder, implement duty retrieval
        self.labelDuty.setText(member.duty or "N/A")
        self.labelClass.setText(member.member_class or "")
        self.labelActivityStatus.setText(member.activity_status or "")

        # Load photo
        if member.photo_path:
            pixmap = QPixmap(member.photo_path)
            if not pixmap.isNull():
                self.labelPhoto.setPixmap(pixmap.scaled(120, 120, Qt.KeepAspectRatio))
                self.current_photo_path = member.photo_path
            else:
                self.labelPhoto.setPixmap(QPixmap().scaled(120, 120, Qt.KeepAspectRatio))
                self.current_photo_path = None
        else:
            self.labelPhoto.setPixmap(QPixmap().scaled(120, 120, Qt.KeepAspectRatio))
            self.current_photo_path = None
        
        # --------------------------
        # Attendance chart plotting
        # --------------------------
        try:
            db2 = Database.get_instance()
            member_attendance = db2.get_attendance_for_member(member.member_id) or {}
        except Exception:
            member_attendance = {}

        # Normalize to ordered lists (dates, numeric presence)
        dates = sorted(member_attendance.keys())
        presence_vals = [1 if member_attendance[d] else 0 for d in dates]

        # If there's no data, clear the chart and return
        try:
            canvas = self.attendanceChart.canvas
            axes = canvas.axes
        except Exception:
            canvas = None
            axes = None

        if not dates:
            if axes is not None:
                try:
                    axes.clear()
                    canvas.draw()
                except Exception:
                    pass
            return

        # Plot and ensure redraw; use tight_layout to avoid clipped xticks
        try:
            self.attendanceChart.plot_attendance(dates, presence_vals)
            if canvas is not None:
                try:
                    canvas.figure.tight_layout()
                except Exception:
                    pass
                try:
                    canvas.draw()
                except Exception:
                    pass
        except Exception as e:
            print(f"[debug] Failed to plot attendance for member {member.member_id}: {e}")
            if axes is not None:
                try:
                    axes.clear()
                    canvas.draw()
                except Exception:
                    pass

    def clear_member_details(self):
        """Clear all member detail fields."""
        self.labelMemberName.setText("")
        self.labelMemberContact.setText("")
        self.labelMemberEmail.setText("")
        self.labelMemberId.setText("")
        self.labelOccupation.setText("")
        self.labelDob.setText("")
        self.labelMaritalStatus.setText("")
        self.labelDuty.setText("")
        self.labelClass.setText("")
        self.labelActivityStatus.setText("")
        self.labelPhoto.setPixmap(QPixmap().scaled(120, 120, Qt.KeepAspectRatio))
        self.current_photo_path = None

        # Clear attendance chart
        try:
            canvas = self.attendanceChart.canvas
            axes = canvas.axes
            if axes is not None:
                axes.clear()
                canvas.draw()
        except Exception:
            pass

    def open_image_viewer(self):
        """Open the clicked member photo in a larger dialog."""
        # Prefer the stored path if available
        if self.current_photo_path:
            ImageViewerDialog.show_from_path(self.current_photo_path, parent=self)
            return
        # Otherwise try using the displayed pixmap (scaled) if present
        pix = self.labelPhoto.pixmap()
        if pix and not pix.isNull():
            # create an unscaled copy for clearer view (if original stored path not available)
            ImageViewerDialog(pix, parent=self).exec()
            return

        QMessageBox.information(self, "No Image", "No image available for this member.")

    def export_selected_member_pdf(self):
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        from app.utils.pdf_export import export_member_pdf

        selected_items = self.listMembers.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a member to export.")
            return
        selected_text = selected_items[0].text()
        if "(" in selected_text and selected_text.endswith(")"):
            member_id = selected_text.rsplit("(", 1)[1].rstrip(")")
        else:
            member_id = selected_text.strip()

        path, _ = QFileDialog.getSaveFileName(self, "Save Member Report", f"member_{member_id}.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        try:
            try:
                out = export_member_pdf(member_id, path)
                QMessageBox.information(self, "Exported", f"Member exported to:\n{out}")
            except ModuleNotFoundError:
                QMessageBox.critical(self, "Missing Dependency", "The 'reportlab' package is required to export PDFs. Install with: pip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export member: {e}")