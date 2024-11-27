import pydgraph
import json
import os
from . import data_parser

def create_schema(client):
    schema = data_parser.CSV_Parser(client=client)
    schema.load_schema()
    
    
def create_data(client):
    data = data_parser.CSV_Parser(client=client)
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    data.load_data(data_dir)


def drop_all(client):
    drop = data_parser.CSV_Parser(client=client)
    drop.drop_all()
    
    
def delete_user(client, ):
    delete = data_parser.CSV_Parser(client)
    delete.delete_user()