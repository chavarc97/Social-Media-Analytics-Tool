import os
import pydgraph
import model

DGRAPH_URI = os.getenv('DGRAPH_URI', 'localhost:9080')

def print_menu():
    mm_options = {
        1: "Create data",
        2: "Query data",
        3: "Delete users with influenceScore less than a given threshold. i.e. > 5.0",
        4: "Drop All",
        5: "Exit",
    }
    for key in mm_options.keys():
        print(key, '--', mm_options[key])
        

def create_client_stub():
    return pydgraph.DgraphClientStub(DGRAPH_URI)


def create_client(client_stub):
    return pydgraph.DgraphClient(client_stub)


def close_client_stub(client_stub):
    client_stub.close()
    
    
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
        
    
def main():
    # Init Client Stub and Dgraph Client
    client_stub = create_client_stub()
    client = create_client(client_stub)
    
    # create schema
    clear_screen()
    print_menu()
    # menu loop
    while True:
        option = int(input('Enter option: '))
        if option == 1:
            model.create_data(client)
        elif option == 2:
            model.query_data(client)
        elif option == 3:
            model.delete_data(client)
        elif option == 4:
            model.drop_all(client)
        elif option == 5:
            model.drop_all(client)
            close_client_stub(client_stub)
            exit(0)
        else:
            print('Invalid option')
            clear_screen()
            print_menu()
    
    
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('Error: {}'.format(e))