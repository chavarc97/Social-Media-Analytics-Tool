import os
import pydgraph
from . import client as dgraph_client
from . import model


DGRAPH_URI = os.getenv("DGRAPH_URI", "localhost:9080")



def create_client_stub():
    return pydgraph.DgraphClientStub(DGRAPH_URI)

def create_schema(client):
    model.create_schema(client)
        
def load_data(client):
    model.create_data(client)

def close_client_stub(client_stub):
    client_stub.close()
        
def run():
    client_stub = create_client_stub()
    client = pydgraph.DgraphClient(client_stub)
    
    model.drop_all(client) # Reset the database
    create_schema(client)
    load_data(client)
        
    return client, client_stub

