from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, password, full_name):
        self.id = id
        self.email = email
        self.password = password
        self.full_name = full_name

    @classmethod
    def from_dict(cls, user_dict):
        """
        Converts a dictionary from MySQL row to a User object.
        """
        return cls(
            id=user_dict['id'],
            email=user_dict['email'],
            password=user_dict['password'],
            full_name=user_dict['full_name']
        )

    def get_id(self):
        return str(self.id)