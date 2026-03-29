from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QListWidget,
    QPushButton, QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QFormLayout, QMessageBox
)
from PySide6.QtCore import Qt, QDate

# Importing database module for attendance handling
from app.database.database import Database

# Importing attendance model
from app.models.attendance import Attendance
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QPushButton
from PySide6.QtCore import QTimer


class AttendanceTab(QWidget):
    """
    Attendance Tab UI
    Provides:
    - Date selection
    - Filtering controls
    - View previous attendance records
    - Load or create new attendance
    - Attendance table widget
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # MAIN LAYOUT
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # ============================================================
        # LEFT PANEL
        # ============================================================
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)

        # --- DATE SELECTION ---
        date_group = QGroupBox("Date")
        date_layout = QFormLayout()
        self.attendanceDateLabel = QLabel("Attendance Date:")
        self.attendanceDateEdit = QDateEdit()
        self.attendanceDateEdit.setCalendarPopup(True)
        self.attendanceDateEdit.setDate(QDate.currentDate())

        date_layout.addRow(self.attendanceDateLabel, self.attendanceDateEdit)
        date_group.setLayout(date_layout)

        # --- FILTER SELECTION ---
        filter_group = QGroupBox("Filter")
        filter_layout = QFormLayout()

        self.attendanceFilterLabel = QLabel("Filter by:")
        self.attendanceFilterCombo = QComboBox()
        self.attendanceFilterCombo.addItems([
            "Present Members", "Absent Members", "All Members"
        ])
        self.attendanceFilterCombo.setCurrentIndex(2)  # Default to "All Members"
        self.attendanceFilterCombo.currentTextChanged.connect(lambda: self.load_attendance())

        filter_layout.addRow(self.attendanceFilterLabel, self.attendanceFilterCombo)
        filter_group.setLayout(filter_layout)

        # --- ACTION BUTTONS ---
        self.btnLoadAttendance = QPushButton("Load Attendance")
        self.btnLoadAttendance.setToolTip("Load attendance record for the selected date")
        self.btnLoadAttendance.clicked.connect(self.load_attendance)

        self.btnNewAttendance = QPushButton("New Attendance")
        self.btnNewAttendance.setToolTip("Create a new attendance record for the selected date")
        self.btnNewAttendance.clicked.connect(self.create_new_attendance)

        self.btnSaveAttendance = QPushButton("Save Attendance")
        self.btnSaveAttendance.setToolTip("Save the current attendance records")
        self.btnSaveAttendance.clicked.connect(self.save_attendance)

        # --- RECORDS LIST ---
        records_group = QGroupBox("Attendance Records")
        records_layout = QVBoxLayout()

        # Buttons for records
        records_buttons = QHBoxLayout()
        self.btnDeleteAttendance = QPushButton("Delete Selected")
        self.btnDeleteAttendance.setToolTip("Delete the selected attendance record")
        self.btnDeleteAttendance.clicked.connect(self.delete_selected_attendance)
        records_buttons.addWidget(self.btnDeleteAttendance)
        records_buttons.addStretch()

        self.listAttendanceRecords = QListWidget()
        self.listAttendanceRecords.itemDoubleClicked.connect(self.on_record_selected)
        self.listAttendanceRecords.itemActivated.connect(self.on_record_selected)
        self.listAttendanceRecords.setSelectionMode(QListWidget.SingleSelection)
        self.list_attendance_records()

        records_layout.addLayout(records_buttons)
        records_layout.addWidget(self.listAttendanceRecords)
        records_group.setLayout(records_layout)

        # Add widgets to left panel
        left_panel.addWidget(date_group)
        left_panel.addWidget(filter_group)
        left_panel.addWidget(self.btnLoadAttendance)
        left_panel.addWidget(self.btnNewAttendance)
        left_panel.addWidget(self.btnSaveAttendance)
        left_panel.addWidget(records_group, stretch=1)

        # ============================================================
        # RIGHT PANEL - ATTENDANCE TABLE
        # ============================================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        table_group = QGroupBox("Attendance Table")
        table_layout = QVBoxLayout()
        # small attendance summary widgets

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(8)

        present_label = QLabel("Present:")
        present_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.presentCountLabel = QLabel("0")
        self.presentCountLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.totalCountLabel = QLabel("/ 0")
        self.totalCountLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setToolTip("Recount present members")
        refresh_btn.setFixedHeight(22)

        stats_layout.addWidget(present_label)
        stats_layout.addWidget(self.presentCountLabel)
        stats_layout.addWidget(self.totalCountLabel)
        stats_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        stats_layout.addWidget(refresh_btn)

        table_layout.addLayout(stats_layout)

        # updater function to count checked items in the Status column (1)
        def update_present_count():
            try:
                table = getattr(self, "attendanceTableWidget", None)
                if table is None:
                    return
                rows = table.rowCount()
                present = 0
                for r in range(rows):
                    item = table.item(r, 1)
                    if item is not None and item.checkState() == Qt.Checked:
                        present += 1
                self.presentCountLabel.setText(str(present))
                self.totalCountLabel.setText(f"/ {rows}")
            except Exception:
                pass

        # manual refresh button
        refresh_btn.clicked.connect(update_present_count)

        # periodic updater to keep count in sync with user changes (safe if widget not yet created)
        timer = QTimer(self)
        timer.setInterval(800)  # ms
        timer.timeout.connect(update_present_count)
        timer.start()

        self.attendanceTableWidget = QTableWidget(0, 3)
        self.attendanceTableWidget.setHorizontalHeaderLabels(
            ["Member Name", "Status", "Notes"]
        )
        self.attendanceTableWidget.horizontalHeader().setStretchLastSection(True)

        table_layout.addWidget(self.attendanceTableWidget)
        table_group.setLayout(table_layout)

        right_panel.addWidget(table_group)

        # ============================================================
        # ADD PANELS TO MAIN LAYOUT
        # ============================================================
        main_layout.addLayout(left_panel, stretch=0)
        main_layout.addLayout(right_panel, stretch=1)

    def create_new_attendance(self):
        """
        Create a new attendance record for the selected date.
        Clears the attendance table for new entries.
        """
        selected_date = self.attendanceDateEdit.date().toString("yyyy-MM-dd")
        # Clear existing table entries
        self.attendanceTableWidget.setRowCount(0)

        members = []
        try:
            db = Database()
            members = db.getAllMembers()
        except Exception as e:
            print("Error fetching members for new attendance:", e)
            members = []

        # Fallback: if no members were returned, leave table empty
        if not members:
            return

        self.attendanceTableWidget.setRowCount(len(members))

        for row, member in enumerate(members):
            # robustly resolve name and id for object or dict
            if hasattr(member, "name"):
                member_name = getattr(member, "name", "") or ""
                member_id = getattr(member, "member_id", "") or getattr(member, "id", "")
            else:
                member_name = member.get("name", "")
                member_id = member.get("member_id", "") or member.get("id", "")

            name_item = QTableWidgetItem(member_name)
            name_item.setData(Qt.UserRole, str(member_id))  # store str member id
            status_item = QTableWidgetItem()
            status_item.setFlags(status_item.flags() | Qt.ItemIsUserCheckable)
            status_item.setCheckState(Qt.Unchecked)

            notes_item = QTableWidgetItem("")
            self.attendanceTableWidget.setItem(row, 0, name_item)
            self.attendanceTableWidget.setItem(row, 1, status_item)
            self.attendanceTableWidget.setItem(row, 2, notes_item)

    def load_attendance(self):
        """
        Load attendance record for the selected date into the table,
        applying the current filter (Present / Absent / All).
        """
        selected_date = self.attendanceDateEdit.date().toString("yyyy-MM-dd")
        db = Database()

        try:
            attendance_record = db.getAttendance(selected_date)
        except Exception as e:
            print("Error loading attendance:", e)
            QMessageBox.critical(self, "Error", f"Failed to load attendance: {e}")
            return

        if not attendance_record:
            # No record found for the date
            self.attendanceTableWidget.setRowCount(0)
            return

        # attendance_record expected to have a .records dict mapping member_id -> bool
        records = getattr(attendance_record, "records", None)
        if records is None:
            try:
                records = attendance_record.get_records()
            except Exception:
                records = {}

        # Apply filter from the combo
        filter_text = self.attendanceFilterCombo.currentText()
        if filter_text == "Present Members":
            filtered_items = [(mid, present) for mid, present in records.items() if present]
        elif filter_text == "Absent Members":
            filtered_items = [(mid, present) for mid, present in records.items() if not present]
        else:  # "All Members" or unknown
            filtered_items = list(records.items())

        # Resolve member names and sort by name for stable display
        resolved = []
        for mid, present in filtered_items:
            try:
                member = db.getMember(str(mid))
                name = member.name if member else str(mid)
            except Exception:
                name = str(mid)
            resolved.append((name, mid, present))
        resolved.sort(key=lambda x: x[0].lower())

        self.attendanceTableWidget.setRowCount(len(resolved))

        for row, (member_name, member_id, present) in enumerate(resolved):
            name_item = QTableWidgetItem(member_name)
            name_item.setData(Qt.UserRole, str(member_id))

            status_item = QTableWidgetItem()
            status_item.setFlags(status_item.flags() | Qt.ItemIsUserCheckable)
            status_item.setCheckState(Qt.Checked if present else Qt.Unchecked)

            notes_item = QTableWidgetItem("")

            self.attendanceTableWidget.setItem(row, 0, name_item)
            self.attendanceTableWidget.setItem(row, 1, status_item)
            self.attendanceTableWidget.setItem(row, 2, notes_item)


    def save_attendance(self):
        """
        Save the current attendance records from the table to the database.
        This merges table values into an existing Attendance for the date (if any),
        otherwise creates a new Attendance and inserts it.
        """
        selected_date = self.attendanceDateEdit.date().toString("yyyy-MM-dd")
        db = Database()

        # Load existing attendance or create new
        try:
            existing = db.getAttendance(selected_date)
        except Exception:
            existing = None

        attendance = existing if existing else Attendance(selected_date)

        # Update attendance from what's currently shown in the table
        for row in range(self.attendanceTableWidget.rowCount()):
            member_item = self.attendanceTableWidget.item(row, 0)
            status_item = self.attendanceTableWidget.item(row, 1)
            if member_item is None or status_item is None:
                continue

            # Prefer stored user-role id, fall back to visible text
            member_id = member_item.data(Qt.UserRole) or member_item.text()
            member_id = str(member_id)

            if status_item.checkState() == Qt.Checked:
                attendance.mark_present(member_id)
            else:
                attendance.mark_absent(member_id)

        # Persist: call updateAttendance if record existed, otherwise addAttendance
        try:
            if existing:
                db.updateAttendance(attendance)
            else:
                db.addAttendance(attendance)
            QMessageBox.information(self, "Saved", "Attendance saved successfully.")
        except Exception as e:
            print("Error saving attendance:", e)
            QMessageBox.critical(self, "Error", f"Failed to save attendance: {e}")

        self.list_attendance_records()

    def on_record_selected(self, item):
        """
        Handle selection of an attendance record from the list.
        Loads the selected record into the table.
        """
        selected_date = item.text()
        self.attendanceDateEdit.setDate(QDate.fromString(selected_date, "yyyy-MM-dd"))
        self.load_attendance()

    def list_attendance_records(self):
        """
        Populate the attendance records list with available dates from the database.
        """
        db = Database()
        try:
            records = db.getAllAttendanceDates() or []
            self.listAttendanceRecords.clear()
            for date_str in records:
                self.listAttendanceRecords.addItem(date_str)
        except Exception as e:
            print("Error listing attendance records:", e)

    def delete_selected_attendance(self):
        """
        Delete the selected attendance record.
        """
        selected_items = self.listAttendanceRecords.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select an attendance record to delete.")
            return

        selected_date = selected_items[0].text()

        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the attendance record for {selected_date}?\n\n"
            "This will permanently remove all attendance data for this date.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        db = Database()
        try:
            db.deleteAttendance(selected_date)
            QMessageBox.information(self, "Deleted", f"Attendance record for {selected_date} has been deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete attendance record: {e}")
            return

        self.list_attendance_records()
        # If the deleted date was loaded, clear the table
        current_date = self.attendanceDateEdit.date().toString("yyyy-MM-dd")
        if current_date == selected_date:
            self.attendanceTableWidget.setRowCount(0)


