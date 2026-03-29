from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtWidgets import QWidget, QVBoxLayout

# Importing database module for attendance data
from app.database.database import Database



class MplotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

class AttendanceChart(QWidget):
    """
    Attendance Chart Widget
    Displays attendance data in a bar chart format.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # MAIN LAYOUT
        main_layout = QVBoxLayout(self)

        # Matplotlib Canvas
        self.canvas = MplotCanvas(self, width=5, height=4, dpi=100)
        main_layout.addWidget(self.canvas)


    def plot_attendance(self, *args):
        """
        Flexible plotting API. Accepts:
          - plot_attendance(member_id)           -> fetches dict from DB via get_attendance_for_member
          - plot_attendance(attendance_dict)     -> uses provided dict {date: bool}
          - plot_attendance(dates_list, values) -> uses provided ordered lists

        Dates are expected as 'YYYY-MM-DD' strings (lexicographical sort works).
        """
        # Determine source of data
        attendance_data = None
        dates = []
        values = []

        # Case: (member_id) -> fetch from DB
        if len(args) == 1 and not isinstance(args[0], (dict, list, tuple)):
            member_id = args[0]
            try:
                db = Database()
                attendance_data = db.get_attendance_for_member(member_id) or {}
            except Exception:
                attendance_data = {}
        # Case: (attendance_dict)
        elif len(args) == 1 and isinstance(args[0], dict):
            attendance_data = args[0] or {}
        # Case: (dates_list, values_list)
        elif len(args) == 2:
            dates_arg, vals_arg = args
            try:
                dates = list(dates_arg)
                values = list(vals_arg)
            except Exception:
                dates = []
                values = []
        else:
            attendance_data = {}

        # If we have a dict, normalize into ordered lists
        if attendance_data is not None:
            # attendance_data: {date: bool}
            dates = sorted(attendance_data.keys())
            values = [1 if attendance_data[d] else 0 for d in dates]

        # Plot or clear if no data
        self.canvas.axes.clear()
        if not dates or not values:
            # nothing to plot -- keep axes empty and redraw
            self.canvas.draw()
            return
        
        # bar plot
        try:
            # Use numeric x positions to avoid matplotlib treating dates as categorical strangely
            x = range(len(dates))
            self.canvas.axes.bar(x, values, color='tab:blue', align='center')
            self.canvas.axes.set_xticks(x)
            # show short labels; rotate for readability
            self.canvas.axes.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)
            self.canvas.axes.set_title('Attendance')
            self.canvas.axes.set_xlabel('Date')
            self.canvas.axes.set_ylabel('Attendance (1=Present, 0=Absent)')
            self.canvas.axes.set_ylim(-0.1, 1.1)
            self.canvas.draw()
        except Exception as e:
            # safe fallback: clear and redraw
            print(f"[debug] AttendanceChart.plot_attendance failed: {e}")
            self.canvas.axes.clear()
            self.canvas.draw()


class GeneralReportChart(QWidget):
    """
    General report chart composed of 4 subplots:
      - Attendance trend over time (top-left)
      - Present vs Absent for latest date (top-right)
      - Member class distribution (bottom-left)
      - Active vs Inactive counts (bottom-right)
    """
    def __init__(self, parent=None, width=6, height=4, dpi=100):
        super().__init__(parent)
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # create 2x2 axes
        self.axes = self.fig.subplots(2, 2)
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

    def plot(self):
        # defensive data fetch
        try:
            db = Database()
        except Exception:
            db = None

        # Clear all axes
        for ax in self.axes.flatten():
            ax.clear()

        # 1) Attendance trend: dates -> total present
        dates = []
        totals = []
        try:
            if db:
                dates = db.getAllAttendanceDates() or []
                dates = sorted(dates)  # chronological by yyyy-mm-dd strings
                for d in dates:
                    att = db.getAttendance(d)
                    if att and hasattr(att, "records"):
                        totals.append(sum(1 for v in att.records.values() if v))
                    else:
                        totals.append(0)
        except Exception:
            dates = []
            totals = []

        ax_trend = self.axes[0, 0]
        if dates and totals:
            x = range(len(dates))
            ax_trend.plot(x, totals, marker='o', linestyle='-', color='tab:blue')
            ax_trend.set_xticks(x)
            ax_trend.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)
            ax_trend.set_title("Attendance Trend (total present)")
            ax_trend.set_ylabel("Present count")
        else:
            ax_trend.text(0.5, 0.5, "No attendance data", ha='center', va='center')
            ax_trend.set_title("Attendance Trend")

        # 2) Present vs Absent for latest date
        ax_pie = self.axes[0, 1]
        try:
            if dates:
                latest = dates[-1]
                att = db.getAttendance(latest) if db else None
                present = sum(1 for v in att.records.values() if v) if att and hasattr(att, "records") else 0
                total_members = max(sum(1 for _ in (att.records.keys())) if att and hasattr(att, "records") else 0,
                                    len(db.getAllMembers() or []) if db else 0)
                absent = max(total_members - present, 0)
                sizes = [present, absent]
                labels = ["Present", "Absent"]
                if sum(sizes) == 0:
                    ax_pie.text(0.5, 0.5, "No data for latest date", ha='center', va='center')
                else:
                    ax_pie.pie(sizes, labels=labels, autopct="%1.0f%%", colors=['tab:green', 'tab:red'])
                ax_pie.set_title(f"Present vs Absent ({latest})")
            else:
                ax_pie.text(0.5, 0.5, "No attendance dates", ha='center', va='center')
                ax_pie.set_title("Present vs Absent")
        except Exception:
            ax_pie.text(0.5, 0.5, "Error", ha='center', va='center')
            ax_pie.set_title("Present vs Absent")

        # 3) Member class distribution (bar)
        ax_class = self.axes[1, 0]
        try:
            members = db.getAllMembers() if db else []
            class_counts = {}
            for m in members:
                cls = (getattr(m, "member_class", None) or "Unknown")
                class_counts[cls] = class_counts.get(cls, 0) + 1
            if class_counts:
                labels = list(class_counts.keys())
                vals = [class_counts[k] for k in labels]
                x = range(len(labels))
                ax_class.bar(x, vals, color='tab:orange')
                ax_class.set_xticks(x)
                ax_class.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
                ax_class.set_title("Member Class Distribution")
            else:
                ax_class.text(0.5, 0.5, "No members", ha='center', va='center')
                ax_class.set_title("Member Class Distribution")
        except Exception:
            ax_class.text(0.5, 0.5, "Error", ha='center', va='center')
            ax_class.set_title("Member Class Distribution")

        # 4) Active vs Inactive (bar)
        ax_status = self.axes[1, 1]
        try:
            active = 0
            inactive = 0
            members = db.getAllMembers() if db else []
            for m in members:
                st = (getattr(m, "activity_status", None) or "").lower()
                if st == "active":
                    active += 1
                elif st:
                    inactive += 1
                else:
                    # treat unknown as inactive
                    inactive += 1
            totals = [active, inactive]
            labels = ["Active", "Inactive"]
            ax_status.bar(labels, totals, color=['tab:green', 'tab:red'])
            ax_status.set_title("Activity Status")
        except Exception:
            ax_status.text(0.5, 0.5, "Error", ha='center', va='center')
            ax_status.set_title("Activity Status")

        # Layout and redraw
        try:
            self.fig.tight_layout()
        except Exception:
            pass
        try:
            self.canvas.draw()
        except Exception:
            pass