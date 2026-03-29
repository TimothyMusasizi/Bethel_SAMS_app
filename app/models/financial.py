class Financial:
    """Model for financial/thanksgiving offerings record.
    
    Attributes:
        id: Unique record ID
        member_id: Reference to member
        member_name: Name of the member who gave
        value: Amount/value of offering
        date: Date of offering (YYYY-MM-DD format)
        notes: Optional notes about the offering
    """
    
    def __init__(self):
        self.id = None
        self.member_id = None
        self.member_name = None
        self.value = 0.0
        self.date = None
        self.notes = ""
    
    def to_dict(self):
        return {
            "id": self.id,
            "member_id": self.member_id,
            "member_name": self.member_name,
            "value": self.value,
            "date": self.date,
            "notes": self.notes,
        }
