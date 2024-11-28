from model import UserModel
import os

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_menu():
    print("Menu Options:")
    print("1. Add User")
    print("2. Drop All")
    print("3. Exit")

def add_user_menu():
    username = input("Enter username: ")
    email = input("Enter email: ")
    bio = input("Enter bio: ")
    try:
        user_id = UserModel.add_user(username, email, bio)
        print(f"User added successfully. ID: {user_id}")
    except Exception as e:
        print(f"Failed to add user: {e}")

def main_menu():
    while True:
        clear_screen()
        print_menu()
        choice = input("Enter choice: ")
        if choice == "1":
            add_user_menu()
        elif choice == "2":
            UserModel.drop_all()
            print("Database dropped successfully.")
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main_menu()
