from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QListWidget,
    QPushButton, QLineEdit, QFormLayout, QMessageBox, QFileDialog, QDialog
)
from PySide6.QtCore import Qt

import traceback
import datetime

# import the report generator
from app.models.report_template import ReportGenerator

# Importing the generate report dialog class
from app.ui.dialogs.generate_report_dialog import GenerateReportDialog
# Database for analysis
from app.database.database import Database

class ReportsTab(QWidget):
    """
    Reports Tab UI
    Includes:
    - General report chart
    - Outstanding issues list + add issue
    - Generate report button
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # MAIN LAYOUT
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # ============================================================
        # LEFT PANEL — REPORT CHART
        # ============================================================
        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)

        # --- General Report Chart ---
        groupChart = QGroupBox("General Report Chart")
        chart_layout = QVBoxLayout()
       
        # Use the GeneralReportChart widget (composed of 4 subplots)
        from app.ui.graphics.charts import GeneralReportChart
        self.generalReportChartWidget = GeneralReportChart(self)
        chart_layout.addWidget(self.generalReportChartWidget)

        # Refresh button to re-generate the report visuals
        refresh_row = QHBoxLayout()
        refresh_row.addStretch()
        self.btnRefreshReports = QPushButton("Refresh Charts")
        self.btnRefreshReports.clicked.connect(lambda: self.generalReportChartWidget.plot())
        # refresh both charts and issues list
        self.btnRefreshReports.clicked.connect(self.refresh_reports)
        refresh_row.addWidget(self.btnRefreshReports)
        chart_layout.addLayout(refresh_row)
 
        groupChart.setLayout(chart_layout)

        left_panel.addWidget(groupChart)

        # ============================================================
        # RIGHT PANEL — OUTSTANDING ISSUES + GENERATE REPORT
        # ============================================================
        right_panel = QVBoxLayout()
        right_panel.setSpacing(12)

        # --- Outstanding Issues ---
        groupIssues = QGroupBox("Outstanding Issues")
        issues_layout = QVBoxLayout()

        self.listOutstandingIssues = QListWidget()

        # Add Issue Row
        add_issue_row = QHBoxLayout()
        self.addIssueLabel = QLabel("Add Issue:")
        self.addIssueEdit = QLineEdit()
        add_issue_row.addWidget(self.addIssueLabel)
        add_issue_row.addWidget(self.addIssueEdit)

        issues_layout.addWidget(self.listOutstandingIssues)
        issues_layout.addLayout(add_issue_row)
        groupIssues.setLayout(issues_layout)

        # --- Generate Report Button ---
        self.btnGenerateReport = QPushButton("Generate Report")
        self.btnGenerateReport.setMinimumHeight(40)
        self.btnGenerateReport.clicked.connect(self.open_generate_report_dialog)

        # Add widgets to right panel
        right_panel.addWidget(groupIssues, stretch=1)
        right_panel.addWidget(self.btnGenerateReport)

        # ============================================================
        # ADD PANELS TO MAIN LAYOUT
        # ============================================================
        main_layout.addLayout(left_panel, stretch=1)
        main_layout.addLayout(right_panel, stretch=0)


    def open_generate_report_dialog(self):
        dialog = GenerateReportDialog(self)
        # show dialog; if accepted or if user triggers generation from dialog, call dialog.generate_report
        if dialog.exec() == QDialog.Accepted:
            # dialog accepted when generation succeeded (dialog.generate_report calls accept())
            try:
                self.refresh_reports()
            except Exception:
                pass
            return

        # if dialog closed without accepting, still allow the dialog to initiate generation via its button handler
        # (the dialog.generate_report method handles save dialogs and messages)



    def refresh_reports(self):
        """Refresh visual charts and recompute issues/insights."""
        try:
            self.generalReportChartWidget.plot()
        except Exception:
            pass
        try:
            self.analyze_attendance_issues()
        except Exception:
            pass

    def analyze_attendance_issues(self):
        """
        Populate listOutstandingIssues with insights:
         - low attendance dates
         - decreasing attendance trend
         - members with high absence rates
         - members with long consecutive absence streaks
        """
        self.listOutstandingIssues.clear()
        db = None
        try:
            db = Database()
        except Exception:
            pass

        if not db:
            self.listOutstandingIssues.addItem("Unable to access database for analysis.")
            return
        
        dates = sorted(db.getAllAttendanceDates() or [])
        members = db.getAllMembers() or []
        total_members = len(members)

        if not dates:
            self.listOutstandingIssues.addItem("No attendance records available.")
            return

        # 1) Low attendance per date
        low_threshold = 0.5  # 50%
        for d in dates:
            att = db.getAttendance(d)
            present = sum(1 for v in getattr(att, "records", {}).values() if v)
            pct = (present / total_members) if total_members else 0
            if pct < low_threshold:
                self.listOutstandingIssues.addItem(f"Low attendance on {d}: {present}/{total_members} ({pct*100:.0f}%)")

        # 2) Decreasing trend (compare first vs last third)
        if len(dates) >= 3 and total_members:
            n = len(dates)
            k = max(1, n // 3)
            first_chunk = dates[:k]
            last_chunk = dates[-k:]
            def avg_present(date_list):
                vals = []
                for dt in date_list:
                    a = db.getAttendance(dt)
                    vals.append(sum(1 for v in getattr(a, "records", {}).values() if v) / total_members)
                return sum(vals) / len(vals) if vals else 0

            first_avg = avg_present(first_chunk)
            last_avg = avg_present(last_chunk)
            if first_avg - last_avg > 0.15:  # dropped more than 15%
                self.listOutstandingIssues.addItem(
                    f"Decreasing attendance trend: first avg {first_avg*100:.0f}%, last avg {last_avg*100:.0f}%"
                )

        # 3) Member-level issues: high absence rate & long consecutive absences
        absence_rate_threshold = 0.5
        consecutive_threshold = 3
        for m in members:
            mid = getattr(m, "member_id", getattr(m, "id", None))
            if mid is None:
                continue
            att_map = db.get_attendance_for_member(mid) or {}
            total = len(dates)
            absences = sum(1 for v in att_map.values() if not v)
            rate = absences / (total or 1)
            if rate > absence_rate_threshold:
                self.listOutstandingIssues.addItem(
                    f"Frequent absences: {getattr(m,'name','<unknown>')} ({mid}) absent {absences}/{total} ({rate*100:.0f}%)"
                )
            
            # compute max consecutive absences
            consec = 0
            max_consec = 0
            for d in dates:
                present = bool(att_map.get(d, False))
                if not present:
                    consec += 1
                    if consec > max_consec:
                        max_consec = consec
                else:
                    consec = 0
            if max_consec >= consecutive_threshold:
                self.listOutstandingIssues.addItem(
                    f"Long absence streak: {getattr(m,'name','<unknown>')} ({mid}) absent for {max_consec} consecutive sessions"
                )

        # If nothing flagged, show a reassuring message
        if self.listOutstandingIssues.count() == 0:
            self.listOutstandingIssues.addItem("No significant issues detected.")