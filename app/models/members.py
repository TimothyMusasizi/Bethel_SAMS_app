

class Member:
    def __init__(self):
        self.id = None
        self.member_id = None
        self.name = None
        self.contact = None
        self.email = None
        self.dob = None  # Date of Birth
        self.occupation = None
        self.marital_status = None
        self.duty = None
        self.member_class = None
        self.activity_status = None # Active/Inactive
        self.photo_path = None  # Path to member's photo

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "contact": self.contact,
            "email": self.email,
            "dob": self.dob,
            "occupation": self.occupation,
            "marital_status": self.marital_status,
            "duty": self.duty,
            "member_class": self.member_class,
            "activity_status": self.activity_status,
            "photo_path": self.photo_path,
        }