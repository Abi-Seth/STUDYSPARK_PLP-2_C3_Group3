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
    
    def view_all_sessions(self, user):
        if not user.is_logged_in():
            print("==> Please log in to view your sessions.")
            return
        
        if user.logged_in_user not in self.sessions or not self.sessions[user.logged_in_user]:
            print("==> No sessions found.")
            return
        
        print("\nYour Study Sessions:")
        print("{:<5} {:<20} {:<15} {:<15} {:<15} {:<10}".format(
            "No.", "Name", "Start Time", "End Time", "Duration", "Status"))
        
        for i, session in enumerate(self.sessions[user.logged_in_user], 1):
            duration = f"{session['actual_duration']} min" if session['actual_duration'] else "N/A"
            end_time = session['end_time'] if session['end_time'] else "N/A"
            print("{:<5} {:<20} {:<15} {:<15} {:<15} {:<10}".format(
                i, session['name'], session['start_time'], end_time, duration, session['status']))

    def get_encouragement(self):
        try:
            response = requests.get("https://api.quotable.io/random?tags=inspirational")
            if response.status_code == 200:
                data = response.json()
                return f"\n==> Encouragement: {data['content']} - {data['author']}\n"
        except requests.exceptions.RequestException:
            pass
        return "\n==> Keep going! Your hard work will pay off.\n"

class ProgressReport:
    """Handle user progress tracking and reporting."""
    def __init__(self, user_manager, session_manager):
        self.user_manager = user_manager
        self.session_manager = session_manager
    
    def view_report(self):
        if not self.user_manager.is_logged_in():
            print("==> Please log in to view your progress report.")
            return
        
        user = self.user_manager.get_current_user()
        if not user:
            return
        
        print("\n=== YOUR PROGRESS REPORT ===")
        print(f"Current Streak: {user['streak']} days")
        print(f"Total Points: {user['points']}")
        print(f"Badges Earned: {', '.join(user['badges']) if user['badges'] else 'None'}")

        total_minutes = 0
        if self.user_manager.logged_in_user in self.session_manager.sessions:
            for session in self.session_manager.sessions[self.user_manager.logged_in_user]:
                if session['actual_duration']:
                    total_minutes += session['actual_duration']
        
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        print(f"Total Study Time: {hours} hours and {minutes} minutes")

        self.check_badges(user)

        print("\n=== PERSONALIZED MESSAGE ===")
        print(self.generate_personalized_message(user))
    
    def check_badges(self, user):
        new_badges = []
        
        if user['streak'] >= 7 and "7-Day Streak" not in user['badges']:
            new_badges.append("7-Day Streak")
        if user['streak'] >= 30 and "30-Day Streak" not in user['badges']:
            new_badges.append("30-Day Streak")
        if user['points'] >= 1000 and "1000 Points" not in user['badges']:
            new_badges.append("1000 Points")
        
        if new_badges:
            user['badges'].extend(new_badges)
            self.user_manager.save_users()
            print(f"\n==> New Badges Earned: {', '.join(new_badges)}")
    
    def generate_personalized_message(self, user):
        messages = []
        
        if user['streak'] == 0:
            messages.append("It's a great day to start a new streak!")
        elif user['streak'] < 3:
            messages.append(f"Your {user['streak']}-day streak is a good start! Keep it going.")
        elif user['streak'] < 7:
            messages.append(f"Awesome! You're on a {user['streak']}-day streak. You're building great habits!")
        else:
            messages.append(f"Wow! A {user['streak']}-day streak! You're crushing it!")
        
        if user['points'] < 100:
            messages.append("Every minute of study counts. Keep adding to your points!")
        elif user['points'] < 500:
            messages.append(f"You've earned {user['points']} points already. Great progress!")
        else:
            messages.append(f"With {user['points']} points, you're showing serious dedication!")
        
        if not user['badges']:
            messages.append("Complete challenges to earn your first badge!")
        else:
            messages.append(f"Your badges show your commitment: {', '.join(user['badges'])}")
        
        return " ".join(messages)

class Leaderboard:
    """Handle user rankings and leaderboard display."""
   def __init__(self, user_manager):
        self.user_manager = user_manager
    
    def view_leaderboard(self):
        print("\n=== LEADERBOARD ===")
        print("{:<5} {:<20} {:<10} {:<10} {:<20}".format(
            "Rank", "Username", "Streak", "Points", "Badges"))

        sorted_users = sorted(
            self.user_manager.users,
            key=lambda x: (-x['streak'], -x['points'], len(x['badges']))
        )
        
        for rank, user in enumerate(sorted_users[:10], 1):
            badges = ', '.join(user['badges'][:3]) + ('...' if len(user['badges']) > 3 else '')
            print("{:<5} {:<20} {:<10} {:<10} {:<20}".format(
                rank, user['username'], user['streak'], user['points'], badges))

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
