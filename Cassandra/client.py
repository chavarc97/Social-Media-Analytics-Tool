import os
from . import model
from cassandra.cluster import Cluster
import uuid

# Connect to Cassandra
def connect_to_cassandra(keyspace='social_media'):
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace(keyspace)
    return session

# Menu functions
def print_menu():
    menu_options = {
        1: "Insert Login Record",
        2: "Retrieve Login History",
        3: "Insert Account Deactivation",
        4: "Retrieve Account Deactivation Logs",
        5: "Insert Profile Change",
        6: "Retrieve Profile Change History",
        7: "Insert Post Activity",
        8: "Retrieve Post Activity",
        9: "Insert Error Log",
        10: "Retrieve Error Logs",
        11: "Insert Search Activity",
        12: "Retrieve Search Activity",
        13: "Insert Friend Request",
        14: "Retrieve Friend Requests",
        15: "Exit"
    }
    
    for key in menu_options.keys():
        print(f"{key} -- {menu_options[key]}")

def handle_user_input(session):
    while True:
        print_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            model.insert_login_record(session)
        elif choice == '2':
            model.retrieve_login_history(session)
        elif choice == '3':
            model.insert_account_deactivation(session)
        elif choice == '4':
            model.retrieve_account_deactivation(session)
        elif choice == '5':
            model.insert_profile_change(session)
        elif choice == '6':
            model.retrieve_profile_change_history(session)
        elif choice == '7':
            model.insert_post_activity(session)
        elif choice == '8':
            model.retrieve_post_activity(session)
        elif choice == '9':
            model.insert_error_log(session)
        elif choice == '10':
            model.retrieve_error_logs(session)
        elif choice == '11':
            model.insert_search_activity(session)
        elif choice == '12':
            model.retrieve_search_activity(session)
        elif choice == '13':
            model.insert_friend_request(session)
        elif choice == '14':
            model.retrieve_friend_requests(session)
        elif choice == '15':
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")


def create_client_stub():
    return ""


def create_client(client_stub):
    return ""


def close_client_stub(client_stub):
    pass


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def main():
    keyspace = 'social_media'
    session = connect_to_cassandra(keyspace)
    handle_user_input(session)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error: {}".format(e))
