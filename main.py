class User:
    """This is the users class"""

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