class User:
    def __init__(self, user_id, username, password_hash, email_address):
        self.user_id       = user_id
        self.username      = username
        self.password_hash = password_hash
        self.email_address = email_address

    def __repr__(self):
        return f"<User {self.user_id}: {self.username}>"