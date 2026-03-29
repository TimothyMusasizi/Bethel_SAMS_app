from PySide6.QtWidgets import (
    QToolBar,
    QLineEdit,
    QWidgetAction,
    QLabel,
    QToolButton,
    QMenu,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QAction


class AppToolBar(QToolBar):
    """Application toolbar for the main window.

    - Emits signals for common actions so the UI remains modular.
    - Contains: Add, Edit, Export, Refresh actions and a search field.

    Usage:
        toolbar = AppToolBar(parent=self)
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        toolbar.add_member.connect(self.on_add_member)
        toolbar.search_text_changed.connect(self.on_search)
    """

    add_member = Signal()
    edit_member = Signal()
    export_member = Signal()
    refresh = Signal()
    search_text_changed = Signal(str)
    # Advanced management signals
    edit_class_list = Signal()
    edit_duty_list = Signal()
    edit_activity_options = Signal()

    # Statistics signals
    refresh_stats = Signal()
    export_stats = Signal()
    # Theme signals
    toggle_theme = Signal()
    # Network signals
    host_server = Signal()
    join_server = Signal()

    def __init__(self, parent=None):
        super().__init__("Main Toolbar", parent)
        self.setMovable(False)
        self.setObjectName("AppToolBar")
        self._create_actions()

    def _create_actions(self):
        # Add
        self.action_add = QAction(QIcon.fromTheme("list-add"), "Add Member", self)
        self.action_add.triggered.connect(self.add_member.emit)
        self.addAction(self.action_add)

        # Edit
        self.action_edit = QAction(QIcon.fromTheme("document-edit"), "Edit Member", self)
        self.action_edit.triggered.connect(self.edit_member.emit)
        self.addAction(self.action_edit)

        # Export
        self.action_export = QAction(QIcon.fromTheme("document-save-as"), "Export Info", self)
        self.action_export.triggered.connect(self.export_member.emit)
        self.addAction(self.action_export)

        # Refresh
        self.action_refresh = QAction(QIcon.fromTheme("view-refresh"), "Refresh", self)
        self.action_refresh.triggered.connect(self.refresh.emit)
        self.addAction(self.action_refresh)

        # Theme toggle
        self.action_toggle_theme = QAction(QIcon.fromTheme("weather-clear-night"), "Toggle Theme", self)
        self.action_toggle_theme.setToolTip("Toggle between dark and light themes")
        self.action_toggle_theme.triggered.connect(self.toggle_theme.emit)
        self.addAction(self.action_toggle_theme)

        # spacer and search
        self.addSeparator()
        self.search_edit = QLineEdit(self)
        self.search_edit.setPlaceholderText("Search members...")
        self.search_edit.setMaximumWidth(240)
        self.search_edit.textChanged.connect(self.search_text_changed.emit)
        search_action = QWidgetAction(self)
        search_action.setDefaultWidget(self.search_edit)
        self.addAction(search_action)
        # add advanced divisions and actions
        self.addSeparator()
        self._create_advanced_divisions()

    def set_actions_enabled(self, *, add=True, edit=True, export=True, refresh=True):
        """Enable or disable toolbar actions in bulk."""
        self.action_add.setEnabled(add)
        self.action_edit.setEnabled(edit)
        self.action_export.setEnabled(export)
        self.action_refresh.setEnabled(refresh)

    def _division_label_action(self, title: str) -> QWidgetAction:
        lbl = QLabel(title)
        # Let theme stylesheet handle colors; only set layout properties
        lbl.setStyleSheet("font-weight: bold; margin: 4px 8px 2px 8px; padding: 0px;")
        act = QWidgetAction(self)
        act.setDefaultWidget(lbl)
        return act

    def _create_advanced_divisions(self):
        # Classes division
        self.addAction(self._division_label_action("Classes"))
        self.action_edit_classes = QAction(QIcon.fromTheme("view-list"), "Edit Class List", self)
        self.action_edit_classes.setToolTip("Edit available classes / groups")
        self.action_edit_classes.triggered.connect(self.edit_class_list.emit)
        self.addAction(self.action_edit_classes)

        # Duties division
        self.addAction(self._division_label_action("Duties"))
        self.action_edit_duties = QAction(QIcon.fromTheme("user-tie"), "Edit Duty List", self)
        self.action_edit_duties.setToolTip("Edit duty / role list used by members")
        self.action_edit_duties.triggered.connect(self.edit_duty_list.emit)
        self.addAction(self.action_edit_duties)

        # Activity division
        self.addAction(self._division_label_action("Activity"))
        self.action_edit_activity = QAction(QIcon.fromTheme("system-run"), "Edit Activity Options", self)
        self.action_edit_activity.setToolTip("Manage activity status options (Active, Inactive, Visitor, etc.)")
        self.action_edit_activity.triggered.connect(self.edit_activity_options.emit)
        self.addAction(self.action_edit_activity)

        # Statistics division
        self.addAction(self._division_label_action("Statistics"))
        self.action_refresh_stats = QAction(QIcon.fromTheme("view-refresh"), "Refresh Stats", self)
        self.action_refresh_stats.triggered.connect(self.refresh_stats.emit)
        self.addAction(self.action_refresh_stats)

        self.action_export_stats = QAction(QIcon.fromTheme("document-save-as"), "Export Stats", self)
        self.action_export_stats.triggered.connect(self.export_stats.emit)
        self.addAction(self.action_export_stats)

        # Network division
        self.addAction(self._division_label_action("Network"))
        self.action_host_server = QAction(QIcon.fromTheme("network-server"), "Host Server", self)
        self.action_host_server.setToolTip("Start hosting a sync server")
        self.action_host_server.triggered.connect(self.host_server.emit)
        self.addAction(self.action_host_server)

        self.action_join_server = QAction(QIcon.fromTheme("network-wired"), "Join Server", self)
        self.action_join_server.setToolTip("Request to join a host server")
        self.action_join_server.triggered.connect(self.join_server.emit)
        self.addAction(self.action_join_server)

    def clear_search(self):
        self.search_edit.clear()

    def set_search_text(self, text: str):
        self.search_edit.setText(text)
