from Dgrah.client import main as clientMain
from Dgrah import init_dgraph
from Cassandra import init_db, client as cassandraMain
from pymongo import MongoClient
from API.menu import main_menu as mongoMain
import os

D_client, D_client_stub = init_dgraph.run()
init_db.main()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["app_database"]

def print_menu_op():
    mm_options = {
        1: "Dgraph",
        2: "Cassandra",
        3: "MongoDB",
        4: "Exit"
    }
    print("Main Menu")
    for key, value in mm_options.items():
        print("{}. {}".format(key, value))


def main():
    try:
        # Main menu
        while True:
            print_menu_op()
            option = int(input("Enter option: "))
            if option == 1:
                clientMain(D_client, D_client_stub)
            elif option == 2:
                cassandraMain.main()
                pass
            elif option == 3:
                mongoMain(mongo_db)
                pass
            elif option == 4:
                print("Exiting...")
                exit(0)
            else:
                print("Invalid option")
                main()
            
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    main()
    
