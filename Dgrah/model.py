import pydgraph
import json
import os
from typing import Dict, List
from . import data_parser
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

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
    
def add_user(client, user: Dict):
    txn = client.txn()
    resp = None
    try:
        users = []
        for key, value in user.items():
            users.append({key: value})
            
        logger.info(f"Loading {len(users)} users, {users}")
        resp = txn.mutate(set_obj=user)
        txn.commit()
    finally:
        txn.discard()
    return resp
        
    
def add_post(client, post: Dict):
    txn = client.txn()
    resp = None
    try:
        posts = []
        for key, value in post.items():
            posts.append({key: value})
            
        logger.info(f"Loading {len(posts)} posts, {posts}")
        resp = txn.mutate(set_obj=post)
        txn.commit()
    finally:
        txn.discard()
    return resp

 