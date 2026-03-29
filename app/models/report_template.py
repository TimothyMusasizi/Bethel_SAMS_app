"""
Report generator for General Assembly Report (monthly).
Uses reportlab for PDF generation and matplotlib for optional charts.

Usage example:
    from app.models.report_template import ReportGenerator
    rg = ReportGenerator()
    rg.generate_monthly_report(2025, 11, r"c:\temp\bethel_report_nov_2025.pdf", color_index=True)

Dependencies:
    pip install reportlab matplotlib
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.units import mm
import tempfile
import os
import math
import datetime
import matplotlib.pyplot as plt

from app.database.database import Database


def _safe_attr(obj, *names, default=""):
    for n in names:
        val = getattr(obj, n, None)
        if val not in (None, ""):
            return val
    return default


class ReportGenerator:
    def __init__(self, db: Database = None):
        self.db = db if db is not None else Database()
        self.styles = getSampleStyleSheet()
        self.h1 = ParagraphStyle("h1", parent=self.styles["Heading1"], alignment=1)
        self.h2 = ParagraphStyle("h2", parent=self.styles["Heading2"], spaceBefore=6)
        self.normal = self.styles["Normal"]

    def generate_monthly_report(self, year: int, month: int, output_path: str, *,
                                title="General Assembly Report",
                                church_name="Bethel Discipleship Church",
                                color_index=False):
        # compute date range for month
        start = datetime.date(year, month, 1)
        if month == 12:
            end = datetime.date(year + 1, 1, 1)
        else:
            end = datetime.date(year, month + 1, 1)

        # fetch data
        members = self.db.getAllMembers() or []
        all_dates = sorted(self.db.getAllAttendanceDates() or [])
        month_dates = [
            d for d in all_dates
            if start <= datetime.datetime.strptime(d, "%Y-%m-%d").date() < end
        ]

        # build member maps
        member_map = {}
        for m in members:
            mid = _safe_attr(m, "member_id", "id", default=None)
            if mid is None:
                continue
            member_map[str(mid)] = m

        # attendance matrix for the month
        attendance_by_date = {}
        for d in month_dates:
            att = self.db.getAttendance(d)
            recs = getattr(att, "records", {}) if att else {}
            # normalize keys to string
            attendance_by_date[d] = {str(k): bool(v) for k, v in recs.items()}

        # per-member stats
        stats = {}
        sessions = len(month_dates)
        for mid, m in member_map.items():
            presents = 0
            for d in month_dates:
                rec = attendance_by_date.get(d, {})
                if rec.get(str(mid), False):
                    presents += 1
            absence = sessions - presents
            rate_absent = (absence / sessions) if sessions else 0.0
            stats[mid] = {
                "member": m,
                "presents": presents,
                "absent": absence,
                "absence_rate": rate_absent
            }

        # generate basic attendance aggregates
        total_present_per_date = [
            (d, sum(1 for v in attendance_by_date.get(d, {}).values() if v))
            for d in month_dates
        ]
        avg_present = (sum(x for _, x in total_present_per_date) / sessions) if sessions else 0

        # identify top absentees
        top_absentees = sorted(stats.items(), key=lambda kv: kv[1]["absent"], reverse=True)[:10]

        # identify visitors, new joiners (best-effort), inactive, removed
        visitors = [m for m in members if _safe_attr(m, "member_class", default="").lower() == "visitor"]
        removed_statuses = {"removed", "left", "resigned", "terminated", "deleted"}
        no_longer = [m for m in members if _safe_attr(m, "activity_status", default="").lower() in removed_statuses]
        inactive = [m for m in members if _safe_attr(m, "activity_status", default="").lower() not in {"active"} and m not in no_longer]

        # attempt to detect join date field names
        joined_this_month = []
        for m in members:
            for attr in ("joined", "join_date", "created_at", "date_joined"):
                val = getattr(m, attr, None)
                if not val:
                    continue
                try:
                    if isinstance(val, str):
                        dt = datetime.datetime.fromisoformat(val.split(" ")[0]).date()
                    elif isinstance(val, datetime.date):
                        dt = val
                    else:
                        continue
                    if start <= dt < end:
                        joined_this_month.append(m)
                    break
                except Exception:
                    continue

        # prepare doc
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
        flow = []

        # Header
        flow.append(Paragraph(title, self.h1))
        flow.append(Paragraph(church_name, self.h2))
        flow.append(Spacer(1, 6))

        # Summary / Abstract
        abstract_lines = [
            f"Report period: {start.isoformat()} to {(end - datetime.timedelta(days=1)).isoformat()}",
            f"Total registered members: {len(members)}",
            f"Sessions this month: {sessions}",
            f"Average present per session: {avg_present:.1f}"
        ]
        flow.append(Paragraph("Summary", self.h2))
        for L in abstract_lines:
            flow.append(Paragraph(L, self.normal))
        flow.append(Spacer(1, 6))

        # Tables: all members (id, name, contact, activity)
        flow.append(Paragraph("All Registered Members", self.h2))
        tbl_data = [["ID", "Name", "Contact", "Activity"]]
        for m in members:
            mid = _safe_attr(m, "member_id", "id", default="")
            name = _safe_attr(m, "name", default="")
            contact = _safe_attr(m, "contact", "phone", default="")
            activity = _safe_attr(m, "activity_status", default="")
            row = [str(mid), name, contact, activity]
            tbl_data.append(row)

        t = Table(tbl_data, repeatRows=1, hAlign="LEFT", colWidths=[50*mm, 60*mm, 50*mm, 30*mm])
        style = TableStyle([
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.lightblue),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ])
        if color_index:
            # color visitors rows pale yellow, declining (high absence) pale red
            for i, m in enumerate(members, start=1):
                mid = str(_safe_attr(m, "member_id", "id", default=""))
                cls = _safe_attr(m, "member_class", default="").lower()
                if cls == "visitor":
                    style.add("BACKGROUND", (0,i), (-1,i), colors.HexColor("#fff7d6"))
                elif mid in stats and stats[mid]["absence_rate"] > 0.5:
                    style.add("BACKGROUND", (0,i), (-1,i), colors.HexColor("#ffe6e6"))
        t.setStyle(style)
        flow.append(t)
        flow.append(Spacer(1, 8))

        # Joined this month
        flow.append(Paragraph("Members Joined This Month", self.h2))
        jt = [["ID", "Name", "Contact"]]
        for m in joined_this_month:
            jt.append([str(_safe_attr(m, "member_id", "id", default="")), _safe_attr(m, "name", default=""), _safe_attr(m, "contact", default="")])
        if len(jt) == 1:
            flow.append(Paragraph("No new joiners detected this month.", self.normal))
        else:
            flow.append(Table(jt, hAlign="LEFT", colWidths=[40*mm, 90*mm, 60*mm], style=TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)])))
        flow.append(Spacer(1,6))

        # Visitors
        flow.append(Paragraph("Visitors", self.h2))
        vv = [["ID", "Name", "Contact"]]
        for m in visitors:
            vv.append([str(_safe_attr(m, "member_id", "id", default="")), _safe_attr(m, "name", default=""), _safe_attr(m, "contact", default="")])
        if len(vv) == 1:
            flow.append(Paragraph("No visitors found.", self.normal))
        else:
            flow.append(Table(vv, hAlign="LEFT", colWidths=[40*mm, 90*mm, 60*mm], style=TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)])))
        flow.append(Spacer(1,6))

        # Inactive but still members
        flow.append(Paragraph("Inactive Members (still registered)", self.h2))
        ii = [["ID","Name","Last Known Activity"]]
        for m in inactive:
            ii.append([str(_safe_attr(m, "member_id","id", default="")), _safe_attr(m, "name", default=""), _safe_attr(m, "activity_status", default="")])
        if len(ii) == 1:
            flow.append(Paragraph("No inactive members found.", self.normal))
        else:
            flow.append(Table(ii, hAlign="LEFT", colWidths=[40*mm, 90*mm, 50*mm], style=TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)])))
        flow.append(Spacer(1,6))

        # No longer part of church
        flow.append(Paragraph("Members No Longer Part of the Church", self.h2))
        nl = [["ID","Name","Status"]]
        for m in no_longer:
            nl.append([str(_safe_attr(m, "member_id","id", default="")), _safe_attr(m, "name", default=""), _safe_attr(m, "activity_status", default="")])
        if len(nl) == 1:
            flow.append(Paragraph("No records found.", self.normal))
        else:
            flow.append(Table(nl, hAlign="LEFT", colWidths=[40*mm, 90*mm, 50*mm], style=TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)])))
        flow.append(Spacer(1,6))

        # Classes and members
        flow.append(Paragraph("Members by Class", self.h2))
        classes = {}
        for m in members:
            cls = _safe_attr(m, "member_class", default="Unspecified")
            classes.setdefault(cls, []).append(m)
        for cls, ml in classes.items():
            flow.append(Paragraph(f"{cls} ({len(ml)})", self.styles["Heading4"]))
            tbl = [["ID","Name","Contact"]]
            for m in ml:
                tbl.append([str(_safe_attr(m, "member_id","id", default="")), _safe_attr(m, "name", default=""), _safe_attr(m, "contact", default="")])
            flow.append(Table(tbl, hAlign="LEFT", colWidths=[35*mm, 80*mm, 55*mm], style=TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)])))
            flow.append(Spacer(1,4))

        flow.append(PageBreak())

        # Attendance statistics & trends
        flow.append(Paragraph("Attendance Analysis", self.h2))
        flow.append(Spacer(1,4))
        flow.append(Paragraph(f"Sessions in period: {sessions}", self.normal))
        flow.append(Paragraph(f"Average present per session: {avg_present:.1f}", self.normal))
        flow.append(Spacer(1,6))

        # Top absentees
        flow.append(Paragraph("Top Absentees (month)", self.h2))
        ta = [["Rank","ID","Name","Absences","Presence Count","Absence Rate"]]
        for idx, (mid, info) in enumerate(top_absentees, start=1):
            m = info["member"]
            ta.append([str(idx), str(_safe_attr(m, "member_id","id", default="")), _safe_attr(m, "name", default=""), str(info["absent"]), str(info["presents"]), f"{info['absence_rate']*100:.0f}%"])
        if len(ta) == 1:
            flow.append(Paragraph("No absence data for month.", self.normal))
        else:
            flow.append(Table(ta, hAlign="LEFT", colWidths=[15*mm, 30*mm, 70*mm, 25*mm, 30*mm, 30*mm], style=TableStyle([("GRID",(0,0),(-1,-1),0.25,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightblue)])))
        flow.append(Spacer(1,6))

        # small attendance trend chart (matplotlib -> image)
        if sessions:
            fig, ax = plt.subplots(figsize=(6,2.5))
            xs = list(range(len(total_present_per_date)))
            ys = [v for _, v in total_present_per_date]
            labels = [d for d,_ in total_present_per_date]
            ax.bar(xs, ys, color='tab:blue')
            ax.set_xticks(xs)
            ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
            ax.set_ylabel("Present")
            ax.set_title("Attendance per session")
            fig.tight_layout()
            tmpf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            fig.savefig(tmpf.name, dpi=150)
            plt.close(fig)
            flow.append(Image(tmpf.name, width=170*mm, height=50*mm))
            flow.append(Spacer(1,6))

        # Insights & Action Points
        flow.append(Paragraph("Insights & Action Points", self.h2))
        insights = []
        # insight: low attendance dates
        low_thresh = 0.5
        for d, total in total_present_per_date:
            pct = (total / len(members)) if members else 0
            if pct < low_thresh:
                insights.append(f"Low attendance on {d}: {total}/{len(members)} ({pct*100:.0f}%)")
        # insight: declining trend
        if len(total_present_per_date) >= 3:
            first = sum(v for _, v in total_present_per_date[:max(1, len(total_present_per_date)//3)]) / max(1, len(total_present_per_date)//3)
            last = sum(v for _, v in total_present_per_date[-max(1, len(total_present_per_date)//3):]) / max(1, len(total_present_per_date)//3)
            if first - last > 0.15 * len(members):
                insights.append("Significant decline in attendance over the month.")
        # member-level actions
        for mid, info in top_absentees[:5]:
            m = info["member"]
            if info["absence_rate"] > 0.5:
                insights.append(f"Frequent absences: {_safe_attr(m,'name','')}, contact for follow-up.")
        if not insights:
            insights.append("No critical issues detected for the period.")

        for it in insights:
            flow.append(Paragraph(f"- {it}", self.normal))

        flow.append(Spacer(1,8))
        flow.append(Paragraph("Suggested Actions:", self.h2))
        flow.append(Paragraph("1. Reach out to frequent absentees for pastoral care.", self.normal))
        flow.append(Paragraph("2. Consider targeted activities to improve engagement.", self.normal))
        flow.append(Paragraph("3. Review visitor follow-up process to convert visitors to members.", self.normal))

        # finalize
        doc.build(flow)

        # cleanup tmp image
        try:
            if 'tmpf' in locals():
                os.unlink(tmpf.name)
        except Exception:
            pass

        return output_path