import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget, QMessageBox, QLabel, QWidgetAction
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# toolbar
from app.ui.toolbar import AppToolBar
from app.utils.notifier import options_notifier

# Import your tabs (ensure these files are in the same directory or adjust import paths)
from app.ui.members_tab import MembersTab
from app.ui.attendance_tab import AttendanceTab
from app.ui.reports_tab import ReportsTab
from app.ui.financial_tab import FinancialTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Church Management System")
        self.resize(1200, 700)  # default window size

        # ============================================================
        # MAIN TAB WIDGET
        # ============================================================
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)
        self.tabs.setTabsClosable(False)

        # ============================================================
        # ADD TABS
        # ============================================================
        self.members_tab = MembersTab()
        self.attendance_tab = AttendanceTab()
        self.reports_tab = ReportsTab()
        self.financial_tab = FinancialTab()

        self.tabs.addTab(self.members_tab, "Members")
        self.tabs.addTab(self.attendance_tab, "Attendance")
        self.tabs.addTab(self.reports_tab, "Reports")
        self.tabs.addTab(self.financial_tab, "Financial")

        # ============================================================
        # TOOLBAR (outside tabs, inside main window)
        # ============================================================
        self.toolbar = AppToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Basic actions -> members tab
        self.toolbar.add_member.connect(self.members_tab.open_add_member_dialog)
        self.toolbar.edit_member.connect(self.members_tab.open_edit_member_dialog)
        self.toolbar.export_member.connect(self._on_export_member)
        # search text updates the members search field (will trigger load_members)
        self.toolbar.search_text_changed.connect(lambda text: self.members_tab.editSearchMembers.setText(text))

        # Refresh should update all visible data
        self.toolbar.refresh.connect(self._on_toolbar_refresh)

        # Advanced actions (placeholders / routing)
        self.toolbar.edit_class_list.connect(self._on_edit_class_list)
        self.toolbar.edit_duty_list.connect(self._on_edit_duty_list)
        self.toolbar.edit_activity_options.connect(self._on_edit_activity_options)
        # Network actions
        self.toolbar.host_server.connect(self._on_host_server)
        self.toolbar.join_server.connect(self._on_join_server)
        self.toolbar.refresh_stats.connect(self.reports_tab.refresh_reports)
        # export stats opens the Generate Report dialog so user can create PDFs
        self.toolbar.export_stats.connect(self._on_export_stats)
        # ============================================================
        # SET AS CENTRAL WIDGET
        # ============================================================
        self.setCentralWidget(self.tabs)

        # Apply initial theme and connect toggle signal
        self.theme_mode = "dark"
        self._apply_theme()
        self.toolbar.toggle_theme.connect(self._toggle_theme)

        # Add a prominent logo label in the toolbar
        self.toolbar.addSeparator()
        self.logo_widget = QLabel("  Bethel SAMS")
        self.logo_widget.setStyleSheet("font-weight:bold; padding:2px 8px; border:1px solid rgba(100,150,200,0.3); border-radius:5px;")
        logo_action = QWidgetAction(self)
        logo_action.setDefaultWidget(self.logo_widget)
        self.toolbar.addAction(logo_action)

        # Listen for option changes to refresh UI globally
        try:
            options_notifier.options_changed.connect(lambda t: self._on_toolbar_refresh())
        except Exception:
            pass

    def _on_toolbar_refresh(self):
        try:
            self.members_tab.load_members()
        except Exception:
            pass
        try:
            self.attendance_tab.load_attendance()
        except Exception:
            pass
        try:
            self.reports_tab.refresh_reports()
        except Exception:
            pass
        try:
            self.financial_tab.load_records()
        except Exception:
            pass

    def _get_theme_stylesheet(self, mode="dark"):
        # Faint background gradients and watermark style
        common = """
            QWidget {
                color: #e8ecf2;
                font-family: "Segoe UI", "Ubuntu", "Arial", sans-serif;
                font-size: 10pt;
            }

            QTabWidget::pane {
                border: 1px solid #456578;
                border-radius: 10px;
                margin: 2px;
                background: rgba(17, 26, 38, 0.75);
            }

            QGroupBox {
                border: 1px solid #4a6893;
                border-radius: 10px;
                margin-top: 32px;
                padding-top: 10px;
                background: rgba(14, 31, 47, 0.82);
                color: #d9ecff;
            }

            QGroupBox:title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                top: -14px;
                padding: 6px 12px;
                background: transparent;
                color: #d9ecff;
                font-weight: 600;
                font-size: 10pt;
                min-height: 38px;
                min-width: 60px;
            }

            QPushButton, QToolButton {
                border: 1px solid #2f5c92;
                border-radius: 6px;
                padding: 6px 12px;
                min-height: 26px;
            }

            QPushButton:hover, QToolButton:hover {
                border: 1px solid #78a1d8;
            }

            QPushButton:pressed, QToolButton:pressed {
                border: 1px solid #5a8bcc;
            }

            QLineEdit, QComboBox, QDateEdit, QListWidget, QTableWidget {
                border: 1px solid #3e5e83;
                border-radius: 5px;
                padding: 2px 6px;
            }

            QListWidget::item:hover {
                background: rgba(52, 94, 137, 0.55);
            }

            QListWidget::item:selected, QTableWidget::item:selected {
                background: rgba(76, 126, 184, 0.8);
                color: #f6fbff;
            }

            QHeaderView::section {
                background: #264466;
                color: #d9e9f5;
                padding: 5px;
                border: 1px solid #366587;
                font-weight: 600;
            }

            QScrollBar:vertical {
                background: rgba(23, 35, 52, 0.6);
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #4a77a3;
                min-height: 20px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #648fbf;
            }

            QLabel {
                color: #dce8f6;
                background: transparent;
                padding: 2px 4px;
            }

            QMenu {
                background: #1e3957;
                color: #e8f2ff;
                border: 1px solid #3a5d82;
            }
        """

        if mode == "light":
            return common + """
                QMainWindow {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f7fafc, stop:1 #dbe6f7);
                }

                QWidget {
                    background: rgba(255, 255, 255, 0.92);
                    color: #1a293e;
                }

                QTabBar::tab {
                    background: #d6e1f3;
                    color: #1f3a57;
                    border: 1px solid #aac2e0;
                }

                QTabBar::tab:selected {
                    background: #ffffff;
                    color: #102342;
                }

                QPushButton, QToolButton {
                    background: #ecf3fb;
                    color: #1f3a57;
                }

                QPushButton:hover, QToolButton:hover {
                    background: #d3e4f7;
                }

                QLineEdit, QComboBox, QDateEdit, QListWidget, QTableWidget {
                    background: #f3f8ff;
                    color: #152139;
                }

                QGroupBox {
                    border: 1px solid #b8d0e8;
                    color: #1a293e;
                }

                QGroupBox:title {
                    color: #0f2340;
                    background: transparent;
                    font-weight: 600;
                    font-size: 10pt;
                    min-height: 38px;
                    min-width: 60px;
                }

                QLabel {
                    color: #1a293e;
                    background: transparent;
                }
            """

        # dark theme by default
        return common + """
            QMainWindow {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #111827, stop:1 #1e3a56);
            }

            QTabBar::tab {
                background: #1f3351;
                color: #c6d9ec;
                border: 1px solid #3b546f;
            }

            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4370a1, stop:1 #1f4a7d);
                color: #ffffff;
                font-weight:bold;
            }

            QPushButton, QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2b60a2, stop:1 #1568b1);
                color: #f8fbff;
            }

            QPushButton:hover, QToolButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a7dc9, stop:1 #2f82ca);
            }

            QLineEdit, QComboBox, QDateEdit, QListWidget, QTableWidget {
                background: rgba(24, 41, 62, 0.95);
                color: #e1ebf7;
            }

            QMainWindow {
                background-image:
                    radial-gradient(circle at 20% 20%, rgba(255,255,255,0.08), transparent 42%),
                    radial-gradient(circle at 80% 80%, rgba(127, 181, 241, 0.09), transparent 35%);
            }
        """

    def _apply_theme(self):
        app = QApplication.instance()
        if app:
            app.setStyleSheet(self._get_theme_stylesheet(self.theme_mode))

    def _toggle_theme(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self._apply_theme()
        # Update toggle icon and label text
        if self.theme_mode == "dark":
            icon = QIcon.fromTheme("weather-clear-night")
            self.toolbar.action_toggle_theme.setText("Dark Theme")
        else:
            icon = QIcon.fromTheme("weather-sunny")
            self.toolbar.action_toggle_theme.setText("Light Theme")
        self.toolbar.action_toggle_theme.setIcon(icon)

    def _on_edit_class_list(self):
        from app.ui.dialogs.manage_options_dialog import ManageOptionsDialog
        dlg = ManageOptionsDialog("classes", "Manage Classes", parent=self)
        dlg.exec()

    def _on_edit_duty_list(self):
        from app.ui.dialogs.manage_options_dialog import ManageOptionsDialog
        dlg = ManageOptionsDialog("duties", "Manage Duties", parent=self)
        dlg.exec()

    def _on_edit_activity_options(self):
        from app.ui.dialogs.manage_options_dialog import ManageOptionsDialog
        dlg = ManageOptionsDialog("activity_options", "Manage Activity Options", parent=self)
        dlg.exec()

    def _on_export_member(self):
        from PySide6.QtWidgets import QFileDialog
        from app.utils.pdf_export import export_member_pdf

        # determine currently selected member in members_tab
        sel = self.members_tab.listMembers.selectedItems()
        if not sel:
            QMessageBox.information(self, "No Selection", "Please select a member to export.")
            return
        text = sel[0].text()
        if "(" in text and text.endswith(")"):
            member_id = text.rsplit("(", 1)[1].rstrip(")")
        else:
            member_id = text.strip()

        path, _ = QFileDialog.getSaveFileName(self, "Save Member Report", f"member_{member_id}.pdf", "PDF Files (*.pdf)")
        if not path:
            return
        try:
            # try to export; handle missing dependency
            try:
                out = export_member_pdf(member_id, path)
                QMessageBox.information(self, "Exported", f"Member exported to:\n{out}")
            except ModuleNotFoundError:
                QMessageBox.critical(self, "Missing Dependency", "The 'reportlab' package is required to export PDFs. Install with: pip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export member: {e}")

    def _on_export_stats(self):
        try:
            from app.ui.dialogs.generate_report_dialog import GenerateReportDialog
        except Exception:
            QMessageBox.information(self, "Export Stats", "Report dialog not available.")
            return
        dlg = GenerateReportDialog(self)
        dlg.exec()

    def _on_host_server(self):
        from app.ui.dialogs.host_server_dialog import HostServerDialog
        dlg = HostServerDialog(self)
        dlg.exec()

    def _on_join_server(self):
        from app.ui.dialogs.join_server_dialog import JoinServerDialog
        dlg = JoinServerDialog(self)
        dlg.exec()


# ================================================================
# APPLICATION ENTRY POINT
# ================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
