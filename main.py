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

    def Login(self, username, password):
        if username not in self.users:
            print("User not found. Please register first.")
        elif self.users[username] != password:
            print("Incorrect password. Please try again.")
        else:
            self.logged_in_user = username
            print(f"User '{username}' logged in successfully!")

    def Logout(self):
        if self.logged_in_user:
            print(f"User '{self.logged_in_user}' logged out successfully!")
            self.logged_in_user = None
        else:
            print("No user is currently logged in.")

    def is_logged_in(self):
        return self.logged_in_user is not None

class StudySession:
    """Handle study sessions and AI encouragement messages."""

    def __init__(self, filename="database/study_sessions.json"):
        self.filename = filename
        self.sessions = self.load_sessions()
        self.active_sessions = {}  # Track ongoing sessions for users

    def load_sessions(self):
        """Load study session data from a file."""
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_sessions(self):
        """Save study session data to a file."""
        with open(self.filename, "w") as file:
            json.dump(self.sessions, file, indent=4)

    def start_session(self, user):
        """Start a study session for the logged-in user."""
        if user.is_logged_in():
            username = user.logged_in_user
            session_id = f"{username}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.active_sessions[username] = {"session_id": session_id, "start_time": start_time}
            print(f"==> Study session started for {username} at {start_time}.")
        else:
            print("==> Please log in to start a study session.")

    def end_session(self, user):
        """End the current study session for the logged-in user."""
        if user.is_logged_in():
            username = user.logged_in_user
            if username in self.active_sessions:
                session_data = self.active_sessions.pop(username)
                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                session_data["end_time"] = end_time
                session_data["duration"] = str(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") - datetime.strptime(session_data["start_time"], "%Y-%m-%d %H:%M:%S"))
                self.sessions[session_data["session_id"]] = session_data
                self.save_sessions()
                print(f"==> Study session ended for {username}. Duration: {session_data['duration']}.")
            else:
                print("==> No active study session found.")
        else:
            print("==> Please log in to end a study session.")

    def view_all_sessions(self, user):
        """View all past study sessions for the logged-in user."""
        if user.is_logged_in():
            username = user.logged_in_user
            user_sessions = [session for session in self.sessions.values() if session["session_id"].startswith(username)]
            if user_sessions:
                print(f"\nAll study sessions for {username}:")
                for session in user_sessions:
                    print(f"Session ID: {session['session_id']}, Start: {session['start_time']}, End: {session.get('end_time', 'In Progress')}, Duration: {session.get('duration', 'Ongoing')}")
            else:
                print("==> No study sessions found.")
        else:
            print("==> Please log in to view your study sessions.")

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
