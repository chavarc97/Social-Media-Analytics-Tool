from cassandra.cluster import Cluster
import uuid
from datetime import datetime

# Connect to Cassandra
def connect_to_cassandra(keyspace='social_media'):
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()
    session.set_keyspace(keyspace)
    return session

# Dynamic Insert Data Functions

def insert_login_record(session):
    username = input("Enter username: ")
    login_time = datetime.now()
    email = input("Enter email: ")
    device = input("Enter device type: ")
    ip = input("Enter IP address: ")
    location = input("Enter location: ")

    query = """
    INSERT INTO login_activity (username, login_time, email, device, ip, location)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    session.execute(query, (username, login_time, email, device, ip, location))
    print("Login record inserted.")

def retrieve_login_history(session):
    username = input("Enter username to retrieve login history: ")
    query = "SELECT * FROM login_activity WHERE username = %s;"
    rows = session.execute(query, (username,))
    for row in rows:
        print(row)

def insert_account_deactivation(session):
    username = input("Enter username: ")
    action_time = datetime.now()
    email = input("Enter email: ")
    action_type = input("Enter action type (e.g., deactivation): ")
    device = input("Enter device type: ")

    query = """
    INSERT INTO account_activity (username, action_time, email, action_type, device)
    VALUES (%s, %s, %s, %s, %s);
    """
    session.execute(query, (username, action_time, email, action_type, device))
    print("Account deactivation inserted.")

def retrieve_account_deactivation(session):
    username = input("Enter username to retrieve account deactivation logs: ")
    query = "SELECT * FROM account_activity WHERE username = %s;"
    rows = session.execute(query, (username,))
    for row in rows:
        print(row)

def insert_profile_change(session):
    username = input("Enter username: ")
    change_time = datetime.now()
    profile_change = input("Enter profile change (e.g., bio): ")
    old_value = input("Enter old value: ")
    new_value = input("Enter new value: ")
    change_type = input("Enter change type (e.g., update): ")
    change_src = input("Enter change source (e.g., mobile): ")

    query = """
    INSERT INTO profile_changes (username, change_time, profile_change, old_value, new_value, change_type, change_src)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    session.execute(query, (username, change_time, profile_change, old_value, new_value, change_type, change_src))
    print("Profile change inserted.")

def retrieve_profile_change_history(session):
    username = input("Enter username to retrieve profile change history: ")
    query = "SELECT * FROM profile_changes WHERE username = %s;"
    rows = session.execute(query, (username,))
    for row in rows:
        print(row)

def insert_post_activity(session):
    username = input("Enter username: ")
    post_time = datetime.now()
    email = input("Enter email: ")
    post_id = uuid.uuid4()  # Generate a unique UUID for the post
    post_ip = input("Enter post IP address: ")
    device = input("Enter device type: ")
    post_location = input("Enter post location: ")

    query = """
    INSERT INTO post_activity (username, post_time, email, post_id, post_ip, device, post_location)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    session.execute(query, (username, post_time, email, post_id, post_ip, device, post_location))
    print("Post activity inserted.")

def retrieve_post_activity(session):
    username = input("Enter username to retrieve post activity: ")
    query = "SELECT * FROM post_activity WHERE username = %s;"
    rows = session.execute(query, (username,))
    for row in rows:
        print(row)

def insert_error_log(session):
    username = input("Enter username: ")
    error_time = datetime.now()
    email = input("Enter email: ")
    section = input("Enter section (e.g., login): ")
    error_message = input("Enter error message: ")
    error_code = int(input("Enter error code: "))  # Convert to integer

    query = """
    INSERT INTO error_logs (username, error_time, email, section, error_message, error_code)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    session.execute(query, (username, error_time, email, section, error_message, error_code))
    print("Error log inserted.")

def retrieve_error_logs(session):
    username = input("Enter username to retrieve error logs: ")
    query = "SELECT * FROM error_logs WHERE username = %s;"
    rows = session.execute(query, (username,))
    for row in rows:
        print(row)

def insert_search_activity(session):
    username = input("Enter username: ")
    search_timestamp = datetime.now()
    email = input("Enter email: ")
    search_query = input("Enter search query: ")
    search_location = input("Enter search location: ")
    device = input("Enter device type: ")
    ip = input("Enter IP address: ")

    query = """
    INSERT INTO search_activity (username, search_timestamp, email, search_query, search_location, device, ip)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    session.execute(query, (username, search_timestamp, email, search_query, search_location, device, ip))
    print("Search activity inserted.")

def retrieve_search_activity(session):
    username = input("Enter username to retrieve search activity: ")
    query = "SELECT * FROM search_activity WHERE username = %s;"
    rows = session.execute(query, (username,))
    for row in rows:
        print(row)

def insert_friend_request(session):
    sender_username = input("Enter sender username: ")
    receiver_username = input("Enter receiver username: ")
    request_time = datetime.now()
    status = input("Enter request status (e.g., pending): ")
    request_location = input("Enter request location: ")

    query = """
    INSERT INTO friend_requests (sender_username, receiver_username, request_time, status, request_location)
    VALUES (%s, %s, %s, %s, %s);
    """
    session.execute(query, (sender_username, receiver_username, request_time, status, request_location))
    print("Friend request inserted.")

def retrieve_friend_requests(session):
    sender_username = input("Enter sender username to retrieve friend requests: ")
    query = "SELECT * FROM friend_requests WHERE sender_username = %s;"
    rows = session.execute(query, (sender_username,))
    for row in rows:
        print(row)