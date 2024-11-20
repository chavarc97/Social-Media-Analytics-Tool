import pydgraph
import json
import data_parser

def create_schema(client):
    schema = data_parser.CSV_Parser(client=client)
    schema.load_schema()
    
    
def create_data(client):
    data = data_parser.CSV_Parser(client=client)
    data.load_data("data")


def drop_all(client):
    drop = data_parser.CSV_Parser(client=client)
    drop.drop_all()
    
"""
    QUERY METHODS ACCORDING TO APP FUNCTIONALITY
"""