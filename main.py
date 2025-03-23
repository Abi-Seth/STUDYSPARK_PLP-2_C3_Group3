class User:
    """This is the users class"""
    def __init__(self):
        self.users = {}
        self.logged_in_user = None

    def Register(self, username, password):
        if username in self.users:
            print("Username already exists. Please choose a different one.")
        else:
            self.users[username] = password
            print(f"User '{username}' registered successfully!")

    def log in(self, username, password):
        if username not in self.users:
            print("User not found. Please register first.")
        elif self.users[username] != password:
            print("Incorrect password. Please try again.")
        else:
            self.logged_in_user = username
            print(f"User '{username}' logged in successfully!")

    def log out(self):
        if self.logged_in_user:
            print(f"User '{self.logged_in_user}' logged out successfully!")
            self.logged_in_user = None
        else:
            print("No user is currently logged in.")

    def is_logged_in(self):
        return self.logged_in_user is not None

class StudySession:
    """This is the study session class"""

class StudyGroups:
    """This is the study groups class"""

def main():
    """Main entry point for StudySpark"""
    print("============================================")
    print("WELCOME TO STUDYSPARK - YOUR STUDY MOTIVATOR")
    print("============================================ \n")

    # CHECK IF THEY HAVE AN ACTIVE SESSION
    # IF NO
    while True:
        print("1. Log in")
        print("2. Register")
        print("3. Logout")
        print("4. Exit")

        choice = input("\nChoose an option: ")
        if choice == '1':
            # call the login function
            print("login person")
            break
        elif choice == '2':
            # call the register function
            print("Register person")
            break
        elif choice == '3':
            # delete the current session
            print("Goodbye for now!")
            break
        elif choice == '4':
            print("Goodbye for now!")
            exit()
            break
        else:
            print("You choose the wrong thing!")
    # IF YES
        # THE MAIN APP MENU

if __name__ == "__main__":
    main()
