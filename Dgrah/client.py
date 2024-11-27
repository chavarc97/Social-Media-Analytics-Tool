from . import model
from . import queries
from . import utils  # For clear_screen() and other utilities
from . import init_dgraph

def print_menu():
    mm_options = {
        1: "Query data",
        2: "Delete users with influenceScore less than a given threshold. i.e. > 5.0",
        3: "Drop All",
        4: "Exit",
    }
    for key in mm_options.keys():
        print(key, "--", mm_options[key])


def main(client, client_stub):   
    # menu loop
    while True:
        utils.clear_screen()
        print_menu()
        option = int(input("Enter option: "))
        if option == 1:
            q = queries.Queries(client)
            q.query_menu()
        elif option == 2:

            model.delete_user(client)
        elif option == 3:
            model.drop_all(client)

        elif option == 4:
            model.drop_all(client)
            print("Exiting...")
            init_dgraph.close_client_stub(client_stub)
            exit(0)
        else:
            print("Invalid option")
            utils.clear_screen()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error: {}".format(e))
