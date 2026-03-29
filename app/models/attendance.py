

class Attendance:
    def __init__(self, date):
        self.records = {}  # {member_id: present (bool), ...}
        self.date = date

    def mark_present(self, member_id):
        self.records[member_id] = True

    def mark_absent(self, member_id):
        self.records[member_id] = False

    def to_dict(self):
        return {
            "date": self.date,
            "attendance": self.records
        }
    
    

