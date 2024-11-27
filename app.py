from Dgrah.client import main as clientMain
from Dgrah import init_dgraph
import os


D_client, D_client_stub = init_dgraph.run()

def print_menu_op():
    mm_options = {
        1: "Content Analysis",
        2: "Search",
        3: "View Logs",
        4: "Settings",
        5: "Exit"
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
                pass
            elif option == 3:
                pass
            elif option == 4:
                pass
            elif option == 5:
                print("Exiting...")
                exit(0)
            else:
                print("Invalid option")
                main()
            
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == "__main__":
    main()