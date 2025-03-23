class User:
    def __init__(self):
        self.users = {}
        self.logged_in_user = None

    def register(self, username, password):
        if username in self.users:
            print("Username already exists. Please choose a different one.")
        else:
            self.users[username] = password
            print(f"User '{username}' registered successfully!")

    def login(self, username, password):
        if username not in self.users:
            print("User not found. Please register first.")
        elif self.users[username] != password:
            print("Incorrect password. Please try again.")
        else:
            self.logged_in_user = username
            print(f"User '{username}' logged in successfully!")

    def logout(self):
        if self.logged_in_user:
            print(f"User '{self.logged_in_user}' logged out successfully!")
            self.logged_in_user = None
        else:
            print("No user is currently logged in.")

    def is_logged_in(self):
        return self.logged_in_user is not None


# Example usage
auth_system = User()
auth_system.register("user1", "password123")
auth_system.login("user1", "password123")
auth_system.logout()

