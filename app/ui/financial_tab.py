from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QComboBox, QLabel, QDateEdit, QSpinBox, QGroupBox,
    QFormLayout, QDialog, QScrollArea
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from datetime import datetime, timedelta
import statistics

from app.database.financial_database import FinancialDatabase
from app.database.database import Database
from app.models.financial import Financial
from app.ui.dialogs.financial_record_dialog import FinancialRecordDialog
from app.utils.financial_charts import try_plot_financial_over_time, try_plot_member_distribution


class FinancialTab(QWidget):
    """
    Financial/Thanksgiving Offerings Tab UI
    Provides:
    - View all financial records in a table
    - Add new offering records
    - Edit existing records
    - Delete records
    - Filter by member
    - Plot view of offerings over time (chart)
    - Summary statistics
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fin_db = FinancialDatabase.get_instance()
        self.db = Database.get_instance()
        self.current_selected_row = None
        self.setup_ui()
        self.load_records()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ============================================================
        # CONTROL PANEL (TOP)
        # ============================================================
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)

        # Member filter
        filter_group = QGroupBox("Filter")
        filter_form = QFormLayout()
        
        self.member_filter_combo = QComboBox()
        self.member_filter_combo.addItem("All Members", None)
        
        members = self.db.getAllMembers()
        for member in members:
            self.member_filter_combo.addItem(f"{member.name} ({member.member_id})", member.member_id)
        
        self.member_filter_combo.currentIndexChanged.connect(self.load_records)
        filter_form.addRow("Member:", self.member_filter_combo)
        filter_group.setLayout(filter_form)
        
        # Date range filter
        date_group = QGroupBox("Date Range")
        date_form = QFormLayout()
        
        # Calculate one year ago
        today = QDate.currentDate()
        one_year_ago = today.addYears(-1)
        
        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(one_year_ago)
        self.start_date_input.dateChanged.connect(self.load_records)
        
        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(today)
        self.end_date_input.dateChanged.connect(self.load_records)
        
        date_form.addRow("From:", self.start_date_input)
        date_form.addRow("To:", self.end_date_input)
        date_group.setLayout(date_form)

        control_layout.addWidget(filter_group)
        control_layout.addWidget(date_group)
        control_layout.addStretch()

        main_layout.addLayout(control_layout)

        # ============================================================
        # MAIN CONTENT (LEFT: TABLE, RIGHT: STATISTICS)
        # ============================================================
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)

        # --- LEFT PANEL: TABLE AND BUTTONS ---
        left_panel = QVBoxLayout()

        # Table widget
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels(["ID", "Member", "Amount", "Date", "Notes", ""])
        self.records_table.setColumnHidden(0, True)  # Hide ID column
        self.records_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.records_table.setSelectionMode(QTableWidget.SingleSelection)
        self.records_table.itemSelectionChanged.connect(self.on_row_selected)
        self.records_table.horizontalHeader().setStretchLastSection(False)

        left_panel.addWidget(self.records_table, stretch=1)

        # Button panel
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.btn_add = QPushButton("Add Offering")
        self.btn_add.clicked.connect(self.open_add_dialog)
        button_layout.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Edit")
        self.btn_edit.clicked.connect(self.open_edit_dialog)
        self.btn_edit.setEnabled(False)
        button_layout.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_delete.setEnabled(False)
        button_layout.addWidget(self.btn_delete)

        button_layout.addStretch()

        # Summary total
        self.label_total = QLabel("Total: 0.00")
        self.label_total.setStyleSheet("font-weight: bold; min-width: 150px;")
        button_layout.addWidget(self.label_total)

        # Chart buttons
        self.btn_chart_timeline = QPushButton("Chart (Timeline)")
        self.btn_chart_timeline.clicked.connect(self.show_timeline_chart)
        button_layout.addWidget(self.btn_chart_timeline)
        
        self.btn_chart_members = QPushButton("Chart (By Member)")
        self.btn_chart_members.clicked.connect(self.show_member_chart)
        button_layout.addWidget(self.btn_chart_members)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self.load_records)
        button_layout.addWidget(self.btn_refresh)

        left_panel.addLayout(button_layout)

        # --- RIGHT PANEL: STATISTICS ---
        right_panel = QVBoxLayout()

        # Statistics group box
        stats_group = QGroupBox("Period Summary Statistics")
        stats_layout = QFormLayout()
        stats_layout.setSpacing(8)

        # Create stat labels
        self.stat_total = self._create_stat_label("0.00")
        self.stat_count = self._create_stat_label("0")
        self.stat_average = self._create_stat_label("0.00")
        self.stat_median = self._create_stat_label("0.00")
        self.stat_max = self._create_stat_label("0.00")
        self.stat_min = self._create_stat_label("0.00")

        # Period comparison stats
        self.stat_comparison_total = self._create_stat_label("0.00")
        self.stat_comparison_avg = self._create_stat_label("0.00")

        # Add to form
        stats_layout.addRow("Total Amount:", self.stat_total)
        stats_layout.addRow("Transaction Count:", self.stat_count)
        stats_layout.addRow("Average per Transaction:", self.stat_average)
        stats_layout.addRow("Median:", self.stat_median)
        stats_layout.addRow("Highest Single:", self.stat_max)
        stats_layout.addRow("Lowest Single:", self.stat_min)
        
        stats_layout.addRow("", QLabel(""))  # Spacer
        
        stats_layout.addRow("Vs. Previous Period:", QLabel(""))
        stats_layout.addRow("  Total Change:", self.stat_comparison_total)
        stats_layout.addRow("  Avg Change:", self.stat_comparison_avg)

        stats_group.setLayout(stats_layout)
        stats_group.setMinimumWidth(280)

        right_panel.addWidget(stats_group, stretch=1)

        # Add panels to content layout
        content_layout.addLayout(left_panel, stretch=1)
        content_layout.addLayout(right_panel, stretch=0)

        main_layout.addLayout(content_layout, stretch=1)

    def load_records(self):
        """Load and display financial records based on current filters."""
        try:
            # Get filter values
            selected_member_id = self.member_filter_combo.currentData()
            start_date = self.start_date_input.date().toString("yyyy-MM-dd")
            end_date = self.end_date_input.date().toString("yyyy-MM-dd")

            # Fetch records
            if selected_member_id:
                # Get records for specific member within date range
                all_records = self.fin_db.get_financial_records_for_member(str(selected_member_id))
                records = [r for r in all_records if start_date <= r.date <= end_date]
            else:
                # Get all records within date range
                records = self.fin_db.get_financial_records_by_date_range(start_date, end_date)

            # Clear table
            self.records_table.setRowCount(0)

            # Populate table
            for record in records:
                row = self.records_table.rowCount()
                self.records_table.insertRow(row)

                # ID (hidden)
                id_item = QTableWidgetItem(str(record.id))
                self.records_table.setItem(row, 0, id_item)

                # Member name
                member_item = QTableWidgetItem(record.member_name or "Unknown")
                member_item.setFlags(member_item.flags() & ~Qt.ItemIsEditable)
                self.records_table.setItem(row, 1, member_item)

                # Amount
                amount_item = QTableWidgetItem(f"{record.value:.2f}")
                amount_item.setFlags(amount_item.flags() & ~Qt.ItemIsEditable)
                self.records_table.setItem(row, 2, amount_item)

                # Date
                date_item = QTableWidgetItem(record.date or "")
                date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
                self.records_table.setItem(row, 3, date_item)

                # Notes
                notes_item = QTableWidgetItem(record.notes or "")
                notes_item.setFlags(notes_item.flags() & ~Qt.ItemIsEditable)
                self.records_table.setItem(row, 4, notes_item)

                # Empty column for buttons
                btn_item = QTableWidgetItem("")
                self.records_table.setItem(row, 5, btn_item)

            # Resize columns
            self.records_table.resizeColumnsToContents()
            self.records_table.setColumnWidth(1, 150)
            self.records_table.setColumnWidth(4, 200)

            # Update total and statistics
            self.update_total_label()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load records: {e}")

    def on_row_selected(self):
        """Handle row selection."""
        selected = self.records_table.selectedItems()
        if selected:
            self.current_selected_row = self.records_table.row(selected[0])
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
        else:
            self.current_selected_row = None
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)

    def open_add_dialog(self):
        """Open dialog to add a new financial record."""
        financial = Financial()
        dlg = FinancialRecordDialog(financial, self)
        if dlg.exec() == QDialog.Accepted:
            try:
                record = dlg.get_financial_record()
                self.fin_db.add_financial_record(record)
                self.load_records()
                QMessageBox.information(self, "Success", "Offering record added successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add record: {e}")

    def open_edit_dialog(self):
        """Open dialog to edit selected financial record."""
        if self.current_selected_row is None:
            QMessageBox.warning(self, "No Selection", "Please select a record to edit.")
            return

        # Get record ID from hidden column
        record_id = int(self.records_table.item(self.current_selected_row, 0).text())
        financial = self.fin_db.get_financial_record(record_id)

        if not financial:
            QMessageBox.critical(self, "Error", "Failed to load record.")
            return

        dlg = FinancialRecordDialog(financial, self)
        if dlg.exec() == QDialog.Accepted:
            try:
                record = dlg.get_financial_record()
                self.fin_db.update_financial_record(record)
                self.load_records()
                QMessageBox.information(self, "Success", "Record updated successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update record: {e}")

    def delete_record(self):
        """Delete the selected financial record."""
        if self.current_selected_row is None:
            QMessageBox.warning(self, "No Selection", "Please select a record to delete.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                record_id = int(self.records_table.item(self.current_selected_row, 0).text())
                self.fin_db.delete_financial_record(record_id)
                self.load_records()
                QMessageBox.information(self, "Success", "Record deleted successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {e}")

    def update_total_label(self):
        """Update the total sum label based on current filtered records."""
        try:
            selected_member_id = self.member_filter_combo.currentData()
            start_date = self.start_date_input.date().toString("yyyy-MM-dd")
            end_date = self.end_date_input.date().toString("yyyy-MM-dd")

            if selected_member_id:
                # Sum for specific member
                total = self.fin_db.get_total_by_member(str(selected_member_id))
                # Filter by date range
                records = self.fin_db.get_financial_records_for_member(str(selected_member_id))
                records = [r for r in records if start_date <= r.date <= end_date]
            else:
                # Sum all within date range
                records = self.fin_db.get_financial_records_by_date_range(start_date, end_date)
                total = sum(r.value for r in records)

            self.label_total.setText(f"Total: {total:.2f}")

            # Update statistics panel
            self._update_statistics_panel(records, start_date, end_date, selected_member_id)

        except Exception as e:
            self.label_total.setText("Total: Error")

    def _create_stat_label(self, text="0.00"):
        """Create a styled label for statistics display."""
        label = QLabel(text)
        label.setStyleSheet(
            "font-weight: bold; padding: 4px 8px; "
            "background: rgba(100, 150, 200, 0.08); border-radius: 4px; "
            "min-width: 100px; min-height: 20px;"
        )
        label.setWordWrap(False)
        return label

    def _get_change_color(self, change_value, is_positive_better=True):
        """Return color and arrow based on change value."""
        if change_value == 0:
            return "#f39c12", "→"  # Orange for no change
        elif (change_value > 0 and is_positive_better) or (change_value < 0 and not is_positive_better):
            return "#2ecc71", "↑"  # Green for positive/good
        else:
            return "#e74c3c", "↓"  # Red for negative/bad

    def _compute_period_statistics(self, records):
        """Compute various statistics for the given records."""
        stats = {
            'total': 0,
            'count': 0,
            'average': 0,
            'median': 0,
            'max': 0,
            'min': 0
        }

        if not records:
            return stats

        values = [r.value for r in records]
        stats['total'] = sum(values)
        stats['count'] = len(values)
        stats['average'] = stats['total'] / stats['count'] if stats['count'] > 0 else 0
        stats['median'] = statistics.median(values) if len(values) > 0 else 0
        stats['max'] = max(values) if values else 0
        stats['min'] = min(values) if values else 0

        return stats

    def _update_statistics_panel(self, current_records, start_date, end_date, selected_member_id):
        """Update the statistics panel with current and previous period comparisons."""
        try:
            # Compute current period statistics
            current_stats = self._compute_period_statistics(current_records)

            # Compute previous period statistics
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            period_length = (end_date_obj - start_date_obj).days

            prev_end = start_date_obj - timedelta(days=1)
            prev_start = prev_end - timedelta(days=period_length)

            prev_start_str = prev_start.strftime("%Y-%m-%d")
            prev_end_str = prev_end.strftime("%Y-%m-%d")

            if selected_member_id:
                all_prev_records = self.fin_db.get_financial_records_for_member(str(selected_member_id))
                prev_records = [r for r in all_prev_records if prev_start_str <= r.date <= prev_end_str]
            else:
                prev_records = self.fin_db.get_financial_records_by_date_range(prev_start_str, prev_end_str)

            prev_stats = self._compute_period_statistics(prev_records)

            # Update labels
            self.stat_total.setText(f"{current_stats['total']:.2f}")
            self.stat_count.setText(str(current_stats['count']))
            self.stat_average.setText(f"{current_stats['average']:.2f}")
            self.stat_median.setText(f"{current_stats['median']:.2f}")
            self.stat_max.setText(f"{current_stats['max']:.2f}")
            self.stat_min.setText(f"{current_stats['min']:.2f}")

            # Update comparison labels with colors and change indicators
            total_change = current_stats['total'] - prev_stats['total']
            avg_change = current_stats['average'] - prev_stats['average']

            # Format comparison text with arrows and colors
            total_color, total_arrow = self._get_change_color(total_change, is_positive_better=True)
            avg_color, avg_arrow = self._get_change_color(avg_change, is_positive_better=True)

            total_comp_text = f"{total_arrow} {total_change:+.2f}" if prev_stats['total'] > 0 else "No previous data"
            avg_comp_text = f"{avg_arrow} {avg_change:+.2f}" if prev_stats['average'] > 0 else "No previous data"

            self.stat_comparison_total.setText(total_comp_text)
            self.stat_comparison_total.setStyleSheet(
                f"color: {total_color}; font-weight: bold; padding: 4px 8px; "
                f"background: rgba({self._hex_to_rgb(total_color)}, 0.1); border-radius: 4px; "
                f"min-width: 100px; min-height: 20px;"
            )

            self.stat_comparison_avg.setText(avg_comp_text)
            self.stat_comparison_avg.setStyleSheet(
                f"color: {avg_color}; font-weight: bold; padding: 4px 8px; "
                f"background: rgba({self._hex_to_rgb(avg_color)}, 0.1); border-radius: 4px; "
                f"min-width: 100px; min-height: 20px;"
            )

        except Exception as e:
            print(f"Error updating statistics: {e}")

    def _hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple for QSS rgba."""
        hex_color = hex_color.lstrip('#')
        return f"{int(hex_color[0:2], 16)}, {int(hex_color[2:4], 16)}, {int(hex_color[4:6], 16)}"


    def show_timeline_chart(self):
        """Display offerings over time as a line chart."""
        try:
            records = self.fin_db.get_financial_records_last_year()
            if not records:
                QMessageBox.information(self, "No Data", "No financial records found in the last year.")
                return
            
            try_plot_financial_over_time(records, "Thanksgiving Offerings Over Time (Last Year)")
        except Exception as e:
            QMessageBox.critical(self, "Chart Error", f"Failed to display chart: {e}")

    def show_member_chart(self):
        """Display offerings by member as a bar chart."""
        try:
            records = self.fin_db.get_financial_records_last_year()
            if not records:
                QMessageBox.information(self, "No Data", "No financial records found in the last year.")
                return
            
            try_plot_member_distribution(records, "Member Contributions (Last Year)")
        except Exception as e:
            QMessageBox.critical(self, "Chart Error", f"Failed to display chart: {e}")
