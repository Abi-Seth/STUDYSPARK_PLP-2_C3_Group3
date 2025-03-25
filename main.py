import time
import json
import hashlib
import requests
from datetime import datetime, timedelta
import os

os.makedirs("database", exist_ok=True)

class User:
    """Handles user registration, login, and session management."""
    def __init__(self, filename="database/users.json"):
        self.filename = filename
        self.users = self.load_users()
        self.logged_in_user = None

    def load_users(self):
        try:
            with open(self.filename, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_users(self):
        with open(self.filename, "w") as file:
            json.dump(self.users, file, indent=4)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        if any(user["username"] == username for user in self.users):
            print("==> Username already exists. Please choose a different one.")
        else:
            hashed_password = self.hash_password(password)
            self.users.append({
                "username": username, 
                "password": hashed_password, 
                "streak": 0, 
                "points": 0, 
                "badges": [],
                "last_study_date": None,
                "study_reminders": []
            })
            self.save_users()
            print(f"==> User '{username}' registered successfully!")

    def login(self, username, password):
        hashed_password = self.hash_password(password)
        user = next((user for user in self.users if user["username"] == username and user["password"] == hashed_password), None)
        if not user:
            print("==> Invalid username or password. Please try again.")
        else:
            self.logged_in_user = username
            print(f"==> User '{username}' logged in successfully!")
            self.update_streak(username)

    def update_streak(self, username):
        user = next((u for u in self.users if u["username"] == username), None)
        if user:
            today = datetime.now().date()
            last_study = datetime.strptime(user["last_study_date"], "%Y-%m-%d").date() if user["last_study_date"] else None
            
            if last_study:
                if today == last_study + timedelta(days=1):
                    user["streak"] += 1
                elif today > last_study + timedelta(days=1):
                    user["streak"] = 1
            user["last_study_date"] = today.strftime("%Y-%m-%d")
            self.save_users()

    def logout(self):
        if self.logged_in_user:
            print(f"==> User '{self.logged_in_user}' logged out successfully!")
            self.logged_in_user = None
        else:
            print("==> No user is currently logged in.")

    def is_logged_in(self):
        return self.logged_in_user is not None

    def get_current_user(self):
        return next((user for user in self.users if user["username"] == self.logged_in_user), None)

class StudySession:
    """Handle study sessions and AI encouragement messages."""

class ProgressReport:
    """Handle user progress tracking and reporting."""

class Leaderboard:
    """Handle user rankings and leaderboard display."""

class StudyGroup:
    """Handle study groups and resources."""

class StudyReminder:
    """Handle study reminders and scheduling."""

def main():
    user = User()
    study_session = StudySession()
    progress_report = ProgressReport(user, study_session)
    leaderboard = Leaderboard(user)
    study_group = StudyGroup()
    study_reminder = StudyReminder(user)
    
    print("============================================")
    print("WELCOME TO STUDYSPARK - YOUR STUDY MOTIVATOR")
    print("============================================ \n")
    
    while True:
        if not user.is_logged_in():
            print("\nMAIN MENU (Not Logged In)")
            print("1. Log in")
            print("2. Register")
            print("3. Exit")
        else:
            print("\nMAIN MENU (Logged in as " + user.logged_in_user + ")")
            print("1. Start a Study Session")
            print("2. End a Study Session")
            print("3. View All Sessions")
            print("4. View Progress Report")
            print("5. View Leaderboard")
            print("6. Study Groups")
            print("7. Modify Study Reminders")
            print("8. Logout")
        
        choice = input("\nChoose an option: ")
        
        if not user.is_logged_in():
            if choice == '1':
                username = input("Enter username: ")
                password = input("Enter password: ")
                user.login(username, password)
            elif choice == '2':
                username = input("Choose a username: ")
                password = input("Choose a password: ")
                user.register(username, password)
            elif choice == '3':
                print("Goodbye for now!")
                break
            else:
                print("==> Invalid choice. Please try again.")
        else:
            if choice == '1':
                study_session.start_session(user)
            elif choice == '2':
                study_session.end_session(user)
            elif choice == '3':
                study_session.view_all_sessions(user)
            elif choice == '4':
                progress_report.view_report()
            elif choice == '5':
                leaderboard.view_leaderboard()
            elif choice == '6':
                print("\nSTUDY GROUPS MENU")
                print("1. Create Study Group")
                print("2. View Study Groups")
                print("3. Join Study Group")
                print("4. Add Resource to Group")
                print("5. View Group Resources")
                group_choice = input("Choose an option: ")

                if group_choice == '1':
                    study_group.create_group(user)
                elif group_choice == '2':
                    study_group.view_groups()
                elif group_choice == '3':
                    study_group.join_group(user)
                elif group_choice == '4':
                    study_group.add_resource(user)
                elif group_choice == '5':
                    study_group.view_resources()
                else:
                    print("==> Invalid choice.")
            elif choice == '7':
                study_reminder.modify_schedule()
            elif choice == '8':
                user.logout()
            else:
                print("==> Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
