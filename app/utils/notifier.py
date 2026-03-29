from PySide6.QtCore import QObject, Signal


class _OptionsNotifier(QObject):
    options_changed = Signal(str)
    members_changed = Signal(str)


options_notifier = _OptionsNotifier()
