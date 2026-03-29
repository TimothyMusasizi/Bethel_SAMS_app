from app.database.database import Database


def export_member_pdf(member_id: str, save_path: str) -> str:
    """Export a member's details and attendance summary to a PDF file.

    Returns the output path on success, raises Exception on error.
    """
    # import reportlab lazily so the package is optional until export is used
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
    except Exception as e:
        raise ModuleNotFoundError("reportlab is required for PDF export") from e

    db = Database.get_instance()
    member = db.getMember(member_id)
    if not member:
        raise ValueError(f"Member not found: {member_id}")

    attendance = db.get_attendance_for_member(member_id) or {}
    dates = sorted(attendance.keys())
    total = len(dates)
    presents = sum(1 for d in dates if attendance.get(d))
    absences = total - presents
    rate = (presents / total * 100) if total else 0.0

    c = canvas.Canvas(save_path, pagesize=letter)
    width, height = letter
    margin = 0.75 * inch
    y = height - margin

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, f"Member Report: {member.name}")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Member ID: {member.member_id}")
    y -= 14
    c.drawString(margin, y, f"Contact: {member.contact}")
    y -= 14
    c.drawString(margin, y, f"Email: {member.email}")
    y -= 14
    c.drawString(margin, y, f"Class: {member.member_class}    Activity: {member.activity_status}")
    y -= 24

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Attendance Summary")
    y -= 16
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Total sessions: {total}")
    y -= 14
    c.drawString(margin, y, f"Present: {presents}      Absent: {absences}      Attendance Rate: {rate:.1f}%")
    y -= 18

    # table header
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margin, y, "Date")
    c.drawString(margin + 200, y, "Present")
    y -= 12
    c.setFont("Helvetica", 9)

    for d in dates:
        if y < margin + 40:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, str(d))
        c.drawString(margin + 200, y, "Yes" if attendance.get(d) else "No")
        y -= 12

    c.showPage()
    c.save()
    return save_path
