import os
import requests
import json

BASE_URL = "http://localhost:5001"
TOKEN = None
global USER_ID


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def make_request(method, endpoint, data=None, auth=True):
    headers = {"Content-Type": "application/json"}
    if auth and TOKEN:
        headers["Authorization"] = TOKEN  # Add Bearer prefix

    url = f"{BASE_URL}/{endpoint}"
    print(f"Request headers: {headers}")
    response = requests.request(method, url, headers=headers, json=data)
    print(f"Response: {response.text}")
    return response.json()


def user_management_menu():
    while True:
        print("\nUser Management:")
        print("1. Register User")
        print("2. Login")
        print("3. Enable 2FA")
        print("4. Reset Password")
        print("5. Back")

        choice = input("Choice: ")
        if choice == "1":
            data = {
                "username": input("Username: "),
                "email": input("Email: "),
                "password": input("Password: "),
                "profile": {
                    "full_name": input("Full Name: "),
                    "bio": input("Bio: ")
                }
            }
            print(make_request("POST", "register", data, auth=False))
        elif choice == "2":
            data = {
                "username": input("Username: "),
                "password": input("Password: ")
            }
            response = make_request("POST", "login", data, auth=False)
            global TOKEN, USER_ID
            TOKEN = response.get("session_token")
            USER_ID = response.get("user", {}).get("id")
            print(f"Login response: {response}")
            print(f"Token value: {TOKEN}")
            print(f"User ID: {USER_ID}")
            print(response)
        elif choice == "3":
            response = make_request("POST", "2fa/enable")
            if response.get("secret"):
                print(f"2FA Secret: {response['secret']}")
                print(f"Backup Codes: {response['backup_codes']}")
            print(response)
        elif choice == "4":
            # Request password reset
            email = input("Enter email for password reset: ")
            response = make_request(
                "POST", "password-reset", {"email": email}, auth=False)
            print(response)

            if response.get("reset_token"):
                # Complete password reset
                new_password = input("Enter new password: ")
                reset_response = make_request(
                    "POST",
                    f"password-reset/{response['reset_token']}",
                    {"new_password": new_password},
                    auth=False
                )
                print(reset_response)
        elif choice == "5":
            break


def content_menu():
    if not USER_ID:
        print("Please login first to get user ID")
        return

    while True:
        print("\nContent Management:")
        print("1. Create Post")
        print("2. Search Content")
        print("3. Back")

        choice = input("Choice: ")
        if choice == "1":
            data = {
                "user_id": USER_ID,
                "text": input("Text: "),
                "tags": input("Tags (comma-separated): ").split(","),
                "visibility": input("Visibility (public/private): ")
            }
            print(make_request("POST", "content", data))
        elif choice == "2":
            query = input("Search query: ")
            print(make_request("GET", f"search?query={query}&type=content"))
        elif choice == "3":
            break


def social_menu():
    while True:
        print("\nSocial Features:")
        print("1. Follow User")
        print("2. Unfollow User")
        print("3. View Notifications")
        print("4. Back")

        choice = input("Choice: ")
        if choice == "1":
            data = {
                "action": "follow",
                "followed_id": input("User ID to follow: ")
            }
            print(make_request("POST", "follow", data))
        elif choice == "2":
            data = {
                "action": "unfollow",
                "followed_id": input("User ID to unfollow: ")
            }
            print(make_request("POST", "follow", data))
        elif choice == "3":
            user_id = input("Your user ID: ")
            print(make_request("GET", f"notifications/unread/{user_id}"))
        elif choice == "4":
            break


def settings_menu():
    while True:
        print("\nSettings:")
        print("1. Update UI Preferences")
        print("2. Update Privacy Settings")
        print("3. Back")

        choice = input("Choice: ")
        if choice == "1":
            data = {
                "theme": input("Theme (light/dark): "),
                "accessibility_options": input("Accessibility options (comma-separated): ").split(",")
            }
            user_id = input("Your user ID: ")
            print(make_request("POST", f"ui-preferences/{user_id}", data))
        elif choice == "2":
            data = {
                "profile_visibility": input("Profile visibility (public/private): "),
                "content_visibility": input("Content visibility (public/followers): ")
            }
            print(make_request("PUT", "privacy-settings", data))
        elif choice == "3":
            break


def main_menu():
    while True:
        clear_screen()
        print("\nAPI Testing Menu")
        print("1. User Management")
        print("2. Content Management")
        print("3. Social Features")
        print("4. Settings")
        print("5. Exit")

        choice = input("Choice: ")
        if choice == "1":
            user_management_menu()
        elif choice == "2":
            content_menu()
        elif choice == "3":
            social_menu()
        elif choice == "4":
            settings_menu()
        elif choice == "5":
            break


if __name__ == "__main__":
    main_menu()
