import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime, timedelta
import requests

# Database connection class
class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                port=3311,
                password="",
                database="studyspark"
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            exit(1)

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()

# User management class
class User:
    def __init__(self, db):
        self.db = db
        self.logged_in_user = None

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            print("==> Username already exists. Please choose a different one.")
        else:
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, streak, points, last_study_date) VALUES (%s, %s, %s, %s, %s)",
                (username, hashed_password, 0, 0, None)
            )
            self.db.commit()
            print(f"==> User '{username}' registered successfully!")

    def login(self, username, password):
        cursor = self.db.cursor
        hashed_password = self.hash_password(password)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_password))
        user = cursor.fetchone()
        if not user:
            print("==> Invalid username or password. Please try again.")
        else:
            self.logged_in_user = username
            print(f"==> User '{username}' logged in successfully!")
            self.update_streak(username)

    def update_streak(self, username):
        cursor = self.db.cursor
        cursor.execute("SELECT last_study_date, streak FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            last_study_date = result['last_study_date']
            streak = result['streak']
            today = datetime.now().date()
            if last_study_date:
                if today == last_study_date + timedelta(days=1):
                    streak += 1
                elif today > last_study_date + timedelta(days=1):
                    streak = 1
            else:
                streak = 1
            cursor.execute(
                "UPDATE users SET streak = %s, last_study_date = %s WHERE username = %s",
                (streak, today, username)
            )
            self.db.commit()

    def logout(self):
        if self.logged_in_user:
            print(f"==> User '{self.logged_in_user}' logged out successfully!")
            self.logged_in_user = None
        else:
            print("==> No user is currently logged in.")

    def is_logged_in(self):
        return self.logged_in_user is not None

    def get_current_user(self):
        if not self.logged_in_user:
            return None
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM users WHERE username = %s", (self.logged_in_user,))
        return cursor.fetchone()

# Study session management class
class StudySession:
    def __init__(self, db):
        self.db = db

    def start_session(self, user):
        if not user.is_logged_in():
            print("Please log in before starting a session.")
            return
        username = user.logged_in_user
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()['user_id']
        
        session_name = input("Enter the study session name: ")
        duration = int(input("Enter the duration of the session in minutes: "))
        start_time = datetime.now()
        
        cursor.execute(
            "INSERT INTO study_sessions (user_id, session_name, duration, start_time, status) VALUES (%s, %s, %s, %s, %s)",
            (user_id, session_name, duration, start_time, "In Progress")
        )
        self.db.commit()
        print(f"\nSession '{session_name}' has started for {username}.")
        print(f"Duration: {duration} minutes. Stay focused!")

    def end_session(self, user):
        if not user.is_logged_in():
            print("Please log in before ending a session.")
            return
        username = user.logged_in_user
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()['user_id']
        
        cursor.execute(
            "SELECT * FROM study_sessions WHERE user_id = %s AND status = %s ORDER BY start_time DESC LIMIT 1",
            (user_id, "In Progress")
        )
        session = cursor.fetchone()
        if not session:
            print("No active study session found.")
            return
        
        end_time = datetime.now()
        elapsed_time = (end_time - session['start_time']).total_seconds() / 60
        
        cursor.execute(
            "UPDATE study_sessions SET end_time = %s, actual_duration = %s, status = %s WHERE session_id = %s",
            (end_time, elapsed_time, "Completed", session['session_id'])
        )
        self.db.commit()
        print(f"\nSession '{session['session_name']}' completed!")
        print(f"Total time spent: {elapsed_time:.2f} minutes.")

    def view_all_sessions(self, user):
        if not user.is_logged_in():
            print("==> Please log in to view your sessions.")
            return
        username = user.logged_in_user
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()['user_id']
        
        cursor.execute("SELECT * FROM study_sessions WHERE user_id = %s", (user_id,))
        sessions = cursor.fetchall()
        
        if not sessions:
            print("==> No sessions found.")
            return
        
        print("\nYour Study Sessions:")
        print("{:<5} {:<20} {:<25} {:<25} {:<15} {:<10}".format(
            "No.", "Name", "Start Time", "End Time", "Duration", "Status"))
        
        for i, session in enumerate(sessions, 1):
            start_time = session['start_time'].strftime("%Y-%m-%d %H:%M:%S") if session['start_time'] else "N/A"
            end_time = session['end_time'].strftime("%Y-%m-%d %H:%M:%S") if session['end_time'] else "N/A"
            duration = f"{session['actual_duration']:.2f} min" if session['actual_duration'] else "N/A"
            print("{:<5} {:<20} {:<25} {:<25} {:<15} {:<10}".format(
                i, session['session_name'], start_time, end_time, duration, session['status']))

    def get_encouragement(self):
        try:
            response = requests.get("https://api.quotable.io/random?tags=inspirational")
            if response.status_code == 200:
                data = response.json()
                return f"\n==> Encouragement: {data['content']} - {data['author']}\n"
        except requests.exceptions.RequestException:
            pass
        return "\n==> Keep going! Your hard work will pay off.\n"

# Progress report class
class ProgressReport:
    def __init__(self, user_manager, session_manager, db):
        self.user_manager = user_manager
        self.session_manager = session_manager
        self.db = db
    
    def view_report(self):
        if not self.user_manager.is_logged_in():
            print("==> Please log in to view your progress report.")
            return
        
        user = self.user_manager.get_current_user()
        if not user:
            return
        
        cursor = self.db.cursor
        cursor.execute("SELECT badge_name FROM badges WHERE user_id = %s", (user['user_id'],))
        badges = [row['badge_name'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT SUM(actual_duration) as total FROM study_sessions WHERE user_id = %s AND status = %s", 
                       (user['user_id'], "Completed"))
        total_minutes = cursor.fetchone()['total'] or 0
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        
        print("\n=== YOUR PROGRESS REPORT ===")
        print(f"Current Streak: {user['streak']} days")
        print(f"Total Points: {user['points']}")
        print(f"Badges Earned: {', '.join(badges) if badges else 'None'}")
        print(f"Total Study Time: {hours} hours and {minutes} minutes")
        
        self.check_badges(user)
        
        print("\n=== PERSONALIZED MESSAGE ===")
        print(self.generate_personalized_message(user))
    
    def check_badges(self, user):
        cursor = self.db.cursor
        new_badges = []
        
        if user['streak'] >= 7:
            cursor.execute("SELECT * FROM badges WHERE user_id = %s AND badge_name = %s", (user['user_id'], "7-Day Streak"))
            if not cursor.fetchone():
                new_badges.append("7-Day Streak")
        
        if user['streak'] >= 30:
            cursor.execute("SELECT * FROM badges WHERE user_id = %s AND badge_name = %s", (user['user_id'], "30-Day Streak"))
            if not cursor.fetchone():
                new_badges.append("30-Day Streak")
        
        if user['points'] >= 1000:
            cursor.execute("SELECT * FROM badges WHERE user_id = %s AND badge_name = %s", (user['user_id'], "1000 Points"))
            if not cursor.fetchone():
                new_badges.append("1000 Points")
        
        for badge in new_badges:
            cursor.execute("INSERT INTO badges (user_id, badge_name) VALUES (%s, %s)", (user['user_id'], badge))
        
        if new_badges:
            self.db.commit()
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
        
        cursor = self.db.cursor
        cursor.execute("SELECT COUNT(*) as count FROM badges WHERE user_id = %s", (user['user_id'],))
        badge_count = cursor.fetchone()['count']
        
        if badge_count == 0:
            messages.append("Complete challenges to earn your first badge!")
        else:
            messages.append(f"Your {badge_count} badges show your commitment!")
        
        return " ".join(messages)

# Leaderboard class
class Leaderboard:
    def __init__(self, db):
        self.db = db
    
    def view_leaderboard(self):
        cursor = self.db.cursor
        cursor.execute("""
            SELECT u.username, u.streak, u.points, COUNT(b.badge_id) as badge_count
            FROM users u
            LEFT JOIN badges b ON u.user_id = b.user_id
            GROUP BY u.user_id
            ORDER BY u.streak DESC, u.points DESC, badge_count DESC
            LIMIT 10
        """)
        leaders = cursor.fetchall()
        
        print("\n=== LEADERBOARD ===")
        print("{:<5} {:<20} {:<10} {:<10} {:<20}".format(
            "Rank", "Username", "Streak", "Points", "Badges"))
        
        for rank, leader in enumerate(leaders, 1):
            print("{:<5} {:<20} {:<10} {:<10} {:<20}".format(
                rank, leader['username'], leader['streak'], leader['points'], leader['badge_count']))

# Study group management class
class StudyGroup:
    def __init__(self, db):
        self.db = db

    def create_group(self, user):
        if not user.is_logged_in():
            print("==> Please log in to create a study group.")
            return
        group_name = input("Enter the study group name: ")
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        creator_id = cursor.fetchone()['user_id']
        cursor.execute("INSERT INTO study_groups (group_name, creator_id) VALUES (%s, %s)", (group_name, creator_id))
        self.db.commit()
        print(f"==> Study group '{group_name}' created successfully!")

    def view_groups(self):
        cursor = self.db.cursor
        cursor.execute("""
            SELECT g.group_id, g.group_name, u.username as creator, COUNT(m.user_id) as members 
            FROM study_groups g 
            LEFT JOIN group_members m ON g.group_id = m.group_id 
            JOIN users u ON g.creator_id = u.user_id 
            GROUP BY g.group_id
        """)
        groups = cursor.fetchall()
        if not groups:
            print("==> No study groups found.")
            return
        print("\nStudy Groups:")
        for group in groups:
            print(f"ID: {group['group_id']}, Name: {group['group_name']}, Creator: {group['creator']}, Members: {group['members']}")

    def join_group(self, user):
        if not user.is_logged_in():
            print("==> Please log in to join a study group.")
            return
        group_id = input("Enter the group ID to join: ")
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']
        cursor.execute("SELECT * FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
        if cursor.fetchone():
            print("==> You are already a member of this group.")
        else:
            cursor.execute("INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)", (group_id, user_id))
            self.db.commit()
            print("==> Joined the group successfully!")

    def add_resource(self, user):
        if not user.is_logged_in():
            print("==> Please log in to add a resource.")
            return
        group_id = input("Enter the group ID to add resource to: ")
        resource_name = input("Enter the resource name: ")
        resource_link = input("Enter the resource link: ")
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']
        cursor.execute("SELECT * FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
        if not cursor.fetchone():
            print("==> You are not a member of this group.")
            return
        cursor.execute("INSERT INTO group_resources (group_id, resource_name, resource_link) VALUES (%s, %s, %s)", 
                       (group_id, resource_name, resource_link))
        self.db.commit()
        print("==> Resource added successfully!")

    def view_resources(self):
        group_id = input("Enter the group ID to view resources: ")
        cursor = self.db.cursor
        cursor.execute("SELECT * FROM group_resources WHERE group_id = %s", (group_id,))
        resources = cursor.fetchall()
        if not resources:
            print("==> No resources found for this group.")
            return
        print("\nGroup Resources:")
        for resource in resources:
            print(f"- {resource['resource_name']}: {resource['resource_link']}")

# Study reminder management class
class StudyReminder:
    def __init__(self, db):
        self.db = db

    def modify_schedule(self, user):
        if not user.is_logged_in():
            print("==> Please log in to modify your study schedule.")
            return
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']
        
        cursor.execute("SELECT * FROM study_reminders WHERE user_id = %s", (user_id,))
        reminders = cursor.fetchall()
        
        print("\nYour current reminders:")
        for i, reminder in enumerate(reminders, 1):
            print(f"{i}. {reminder['time']} - {reminder['days']}")
        
        print("\n1. Add new reminder")
        print("2. Remove reminder")
        choice = input("Choose an option: ")
        
        if choice == "1":
            time = input("Enter reminder time (HH:MM format): ")
            days = input("Enter days (comma-separated, e.g., Mon,Tue,Wed): ")
            cursor.execute("INSERT INTO study_reminders (user_id, time, days, enabled) VALUES (%s, %s, %s, %s)", 
                           (user_id, time, days, True))
            self.db.commit()
            print("==> Reminder added successfully!")
        elif choice == "2":
            if not reminders:
                print("==> No reminders to remove.")
                return
            try:
                index = int(input("Enter reminder number to remove: ")) - 1
                if 0 <= index < len(reminders):
                    reminder_id = reminders[index]['reminder_id']
                    cursor.execute("DELETE FROM study_reminders WHERE reminder_id = %s", (reminder_id,))
                    self.db.commit()
                    print("==> Reminder removed successfully!")
                else:
                    print("==> Invalid selection.")
            except ValueError:
                print("==> Please enter a valid number.")
        else:
            print("==> Invalid choice.")

# Main application function
def main():
    db = Database()
    user = User(db)
    study_session = StudySession(db)
    progress_report = ProgressReport(user, study_session, db)
    leaderboard = Leaderboard(db)
    study_group = StudyGroup(db)
    study_reminder = StudyReminder(db)
    
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
                study_reminder.modify_schedule(user)
            elif choice == '8':
                user.logout()
            else:
                print("==> Invalid choice. Please try again.")
    
    db.close()

if __name__ == "__main__":
    main()