#!/usr/bin/env python3
from cassandra.cluster import Cluster
import csv

# Step 1: Connect to Cassandra DB
def connect_to_cassandra(keyspace):
    cluster = Cluster(['localhost'])
    session = cluster.connect()
    CREATE_KEYSPACE = """
        CREATE KEYSPACE IF NOT EXISTS {}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': {} }}
    """
    session.execute(CREATE_KEYSPACE.format(keyspace, 1))
    session.set_keyspace(keyspace)
    return session

# Step 2: Create tables
def create_tables(session):
    queries = [
        """
        CREATE TABLE IF NOT EXISTS login_activity (
            username TEXT,
            login_time TIMESTAMP,
            email TEXT,
            device TEXT,
            ip TEXT,
            location TEXT,
            PRIMARY KEY ((username), login_time)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS account_activity (
            username TEXT,
            action_time TIMESTAMP,
            email TEXT,
            action_type TEXT,
            device TEXT,
            PRIMARY KEY ((username), action_time)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS profile_changes (
            username TEXT,
            change_time TIMESTAMP,
            profile_change TEXT,
            old_value TEXT,
            new_value TEXT,
            change_type TEXT,
            change_src TEXT,
            PRIMARY KEY ((username), change_time)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS post_activity (
            username TEXT,
            post_time TIMESTAMP,
            email TEXT,
            post_id UUID,
            post_ip TEXT,
            device TEXT,
            post_location TEXT,
            PRIMARY KEY ((username), post_time)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS error_logs (
            username TEXT,
            error_time TIMESTAMP,
            email TEXT,
            section TEXT,
            error_message TEXT,
            error_code INT,
            PRIMARY KEY ((username), error_time)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS search_activity (
            username TEXT,
            search_timestamp TIMESTAMP,
            email TEXT,
            search_query TEXT,
            search_location TEXT,
            device TEXT,
            ip TEXT,
            PRIMARY KEY ((username), search_timestamp)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS friend_requests (
            sender_username TEXT,
            receiver_username TEXT,
            request_time TIMESTAMP,
            status TEXT,
            request_location TEXT,
            PRIMARY KEY ((sender_username), request_time)
        );
        """
    ]
    for query in queries:
        session.execute(query)
    print("Tables created successfully.")

# Step 3: Seed data from CSV files
def seed_data_from_csv(session, table_name, csv_file, columns):
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            session.execute(query, [row[col] for col in columns])
    print(f"Data seeded into {table_name} from {csv_file}.")

# Main execution
def main():
    keyspace = 'social_media'
    session = connect_to_cassandra(keyspace)
    
    # Step 2: Create tables
    create_tables(session)
    
    # Step 3: Seed data
    csv_files = {
        "login_activity": ("Cassandra/data/login_activity.csv", ["username", "login_time", "email", "device", "ip", "location"]),
        "account_activity": ("Cassandra/data/account_activity.csv", ["username", "action_time", "email", "action_type", "device"]),
        "profile_changes": ("Cassandra/data/profile_changes.csv", ["username", "change_time", "profile_change", "old_value", "new_value", "change_type", "change_src"]),
        "post_activity": ("Cassandra/data/post_activity.csv", ["username", "post_time", "email", "post_id", "post_ip", "device", "post_location"]),
        "error_logs": ("Cassandra/data/error_logs.csv", ["username", "error_time", "email", "section", "error_message", "error_code"]),
        "search_activity": ("Cassandra/data/search_activity.csv", ["username", "search_timestamp", "email", "search_query", "search_location", "device", "ip"]),
        "friend_requests": ("Cassandra/data/friend_requests.csv", ["sender_username", "receiver_username", "request_time", "status", "request_location"])
    }
    
    for table, (csv_file, columns) in csv_files.items():
        seed_data_from_csv(session, table, csv_file, columns)

if __name__ == "__main__":
    main()