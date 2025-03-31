class User:
    """This is the users class"""

class StudySession:
    """Handles study session tracking for users."""

    def __init__(self, db):
        self.db = db

    def start_session(self, user):
        """Start a new study session for the user."""
        if not user.is_logged_in():
            print("==> Please log in to start a study session.")
            return

        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']

        # Record the start time of the session
        start_time = datetime.now()

        cursor.execute("INSERT INTO study_sessions (user_id, start_time, status) VALUES (%s, %s, %s)",
                       (user_id, start_time, "Ongoing"))
        self.db.commit()

        print(f"==> Study session started for {user.logged_in_user} at {start_time}.")

    def end_session(self, user):
        """End the current study session for the user."""
        if not user.is_logged_in():
            print("==> Please log in to end a study session.")
            return

        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']

        # Get the ongoing study session
        cursor.execute("SELECT * FROM study_sessions WHERE user_id = %s AND status = %s ORDER BY start_time DESC LIMIT 1",
                       (user_id, "Ongoing"))
        session = cursor.fetchone()

        if not session:
            print("==> No ongoing study session found.")
            return

        # Calculate the duration of the session
        end_time = datetime.now()
        duration = (end_time - session['start_time']).total_seconds() / 60  # in minutes

        # Update the session to completed
        cursor.execute("UPDATE study_sessions SET end_time = %s, actual_duration = %s, status = %s WHERE session_id = %s",
                       (end_time, duration, "Completed", session['session_id']))
        self.db.commit()

        # Update user progress (e.g., add points based on session duration)
        cursor.execute("UPDATE users SET points = points + %s WHERE user_id = %s", (duration, user_id))
        self.db.commit()

        print(f"==> Study session ended for {user.logged_in_user} at {end_time}. Duration: {duration} minutes.")

    def view_all_sessions(self, user):
        """View all study sessions for the logged-in user."""
        if not user.is_logged_in():
            print("==> Please log in to view your study sessions.")
            return

        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']

        # Fetch all study sessions for the user
        cursor.execute("SELECT * FROM study_sessions WHERE user_id = %s ORDER BY start_time DESC", (user_id,))
        sessions = cursor.fetchall()

        if not sessions:
            print("==> No study sessions found.")
            return

        print("\n=== STUDY SESSIONS ===")
        for session in sessions:
            start_time = session['start_time']
            end_time = session.get('end_time', 'N/A')
            duration = session.get('actual_duration', 'N/A')
            status = session['status']
            print(f"Start: {start_time}, End: {end_time}, Duration: {duration} mins, Status: {status}")

    def get_session_progress(self, user):
        """Get the progress of a specific session."""
        if not user.is_logged_in():
            print("==> Please log in to view your session progress.")
            return

        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']

        # Get the ongoing session
        cursor.execute("SELECT * FROM study_sessions")

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
    """Handle user rankings and leaderboard display."""
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
    """Handle study groups and resources."""
class StudyGroup:
    """Handle study groups and resources."""
    
    def __init__(self, db):
        """Initialize the StudyGroup class with database connection."""
        self.db = db
    
    def create_group(self, user):
        """Create a new study group."""
        if not user.is_logged_in():
            print("==> Please log in to create a study group.")
            return
            
        cursor = self.db.cursor
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (user.logged_in_user,))
        user_id = cursor.fetchone()['user_id']
        
        group_name = input("Enter group name: ")
        description = input("Enter group description: ")
        subject = input("Enter subject/topic: ")
        max_members = input("Enter maximum number of members (leave blank for unlimited): ")
        
        if not max_members:
            max_members = None
        else:
            try:
                max_members = int(max_members)
                if max_members <= 0:
                    print("==> Maximum members must be a positive number.")
                    return
            except ValueError:
                print("==> Please enter a valid number for maximum members.")
                return
        
        # Check if a group with this name already exists
        cursor.execute("SELECT * FROM study_groups WHERE group_name = %s", (group_name,))
        if cursor.fetchone():
            print("==> A group with this name already exists. Please choose a different name.")
            return
            
        # Create the group
        cursor.execute(
            "INSERT INTO study_groups (group_name, description, subject, max_members, creator_id, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (group_name, description, subject, max_members, user_id, datetime.now())
        )
        self.db.commit()
        
        # Get the new group's ID
        cursor.execute("SELECT group_id FROM study_groups WHERE group_name = %s", (group_name,))
        group_id = cursor.fetchone()['group_id']
        
        # Add the creator as a member
        cursor.execute(
            "INSERT INTO group_members (group_id, user_id, role, joined_at) VALUES (%s, %s, %s, %s)",
            (group_id, user_id, "admin", datetime.now())
        )
        self.db.commit()
        
        print(f"==> Study group '{group_name}' created successfully!")
    
    def view_groups(self):
        """View all available study groups."""
        cursor = self.db.cursor
        cursor.execute("""
            SELECT sg.group_id, sg.group_name, sg.description, sg.subject, 
                   sg.max_members, u.username as creator, 
                   COUNT(gm.user_id) as member_count,
                   sg.created_at
            FROM study_groups sg
            JOIN users u ON sg.creator_id = u.user_id
            LEFT JOIN group_members gm ON sg.group_id = gm.group_id
            GROUP BY sg.group_id
            ORDER BY sg.created_at DESC
        """)
        groups = cursor.fetchall()
        
        if not groups:
            print("==> No study groups found.")
            return
            
        print("\n=== AVAILABLE STUDY GROUPS ===")
        for i, group in enumerate(groups, 1):
            max_members_display = group['max_members'] if group['max_members'] else "Unlimited"
            print(f"\n{i}. {group['group_name']} - {group['subject']}")
            print(f"   Description: {group['description']}")
            print(f"   Created by: {group['creator']}")
            print(f"   Members: {group['member_count']}/{max_members_display}")
            print(f"   Created: {group['created_at'].strftime('%Y-%m-%d')}")
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

        choice = input("\n Choose an option: ")
        if choice == '1':
            # call the login function
        elif choice == '2':
            # call the register function
        elif choice == '3':
            # delete the current session
            print("Goodbye for now!")
            break
        else:
            print("You choose the wrong thing!")
    # IF YES
        # THE MAIN APP MENU

if __name__ == "__main__":
    main()