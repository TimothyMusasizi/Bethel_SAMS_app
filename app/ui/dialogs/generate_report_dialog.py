from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QComboBox, QCheckBox, QPushButton, QSizePolicy, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt

import datetime
import traceback

from app.models.report_template import ReportGenerator


class GenerateReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Generate Report")
        self.setMinimumWidth(420)

        # --------------------------
        # Main Layout
        # --------------------------
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # ====================================================
        # 1. Contents GroupBox
        # ====================================================
        self.contents_groupBox = QGroupBox("Include in Report")
        contents_layout = QVBoxLayout()

        self.include_analysis_checkBox = QCheckBox("Include Analysis")
        self.include_members_list_checkBox = QCheckBox("Include Members List")
        self.include_classification_details_checkBox = QCheckBox("Include Classification Details")
        self.include_color_indexing_checkBox = QCheckBox("Include Color Indexing")

        contents_layout.addWidget(self.include_analysis_checkBox)
        contents_layout.addWidget(self.include_members_list_checkBox)
        contents_layout.addWidget(self.include_classification_details_checkBox)
        contents_layout.addWidget(self.include_color_indexing_checkBox)

        self.contents_groupBox.setLayout(contents_layout)
        main_layout.addWidget(self.contents_groupBox)

        # ====================================================
        # 2. Settings GroupBox
        # ====================================================
        self.settings_groupBox = QGroupBox("Report Settings")
        settings_layout = QFormLayout()

        self.report_language_label = QLabel("Language:")
        self.report_language_combo = QComboBox()
        self.report_language_combo.addItems(["English", "Luganda"])

        settings_layout.addRow(self.report_language_label, self.report_language_combo)

        self.settings_groupBox.setLayout(settings_layout)
        main_layout.addWidget(self.settings_groupBox)

        # ====================================================
        # 3. Generate Report Button
        # ====================================================
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.generate_report_pushButton = QPushButton("Generate Report")
        self.generate_report_pushButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.generate_report_pushButton.clicked.connect(lambda: self.generate_report(self)) 

        button_layout.addWidget(self.generate_report_pushButton)

        main_layout.addLayout(button_layout)

        # --------------------------
        # Final Tweaks
        # --------------------------
        main_layout.addStretch(1)
        self.setWindowModality(Qt.ApplicationModal)

    def generate_report(self, parent=None):
        """
        Perform report generation:
         - read selected year/month and options
         - ask user for save location
         - call ReportGenerator.generate_monthly_report(...)
        Returns path on success, None on cancel/failure.
        """
        try:
            year = int(self.year_spin.value())
            month = int(self.month_combo.currentText())
        except Exception:
            year = datetime.date.today().year
            month = datetime.date.today().month

        color_index = bool(self.include_color_indexing_checkBox.isChecked())

        default_name = f"Bethel_Report_{year}_{month:02d}.pdf"
        save_path, _ = QFileDialog.getSaveFileName(parent or self, "Save Report As", default_name, "PDF Files (*.pdf)")
        if not save_path:
            return None
        try:
            rg = ReportGenerator()
            out = rg.generate_monthly_report(year, month, save_path, color_index=color_index)
            QMessageBox.information(parent or self, "Report Generated", f"Report saved to:\n{out}")
            # Optionally close dialog on success
            self.accept()
            return out
        except Exception:
            tb = traceback.format_exc()
            print(tb)
            QMessageBox.critical(parent or self, "Report Error", f"Failed to generate report:\n\n{tb}")
            return None