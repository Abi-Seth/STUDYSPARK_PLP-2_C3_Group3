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
    """Handles study session tracking for users"""

    def __init__(self, filename="database/study_sessions.json"):
        self.filename = filename
        self.sessions = self.load_sessions()

    def load_sessions(self):
        """Load study sessions from file."""
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_sessions(self):
        """Save study sessions to file."""
        with open(self.filename, "w") as file:
            json.dump(self.sessions, file, indent=4)

    def start_session(self, user):
        """Starts a study session for a logged-in user."""
        if user.logged_in_user is None:
            print("Please log in before starting a session.")
            return

        username = user.logged_in_user
        session_name = input("Enter the study session name: ")
        duration = int(input("Enter the duration of the session in minutes: "))

        start_time = time.time()

        if username not in self.sessions:
            self.sessions[username] = []

        self.sessions[username].append({
            "session_name": session_name,
            "duration": duration,
            "start_time": start_time,
            "status": "In Progress"
        })

        self.save_sessions()
        print(f"\nSession '{session_name}' has started for {username}.")
        print(f"Duration: {duration} minutes. Stay focused!")

    def end_session(self, user):
        """Ends the last study session for a logged-in user."""
        if user.logged_in_user is None:
            print("Please log in before ending a session.")
            return

        username = user.logged_in_user

        if username not in self.sessions or not self.sessions[username]:
            print("No active study session found.")
            return

        last_session = self.sessions[username][-1]

        if last_session["status"] != "In Progress":
            print("No active study session to end.")
            return

        end_time = time.time()
        elapsed_time = (end_time - last_session["start_time"]) / 60  # Convert seconds to minutes

        last_session["status"] = "Completed"
        last_session["end_time"] = end_time
        last_session["actual_duration"] = round(elapsed_time, 2)

        self.save_sessions()
        print(f"\nSession '{last_session['session_name']}' completed!")
        print(f"Total time spent: {elapsed_time:.2f} minutes.")

   
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
