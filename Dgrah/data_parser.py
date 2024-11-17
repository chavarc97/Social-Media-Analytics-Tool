import pydgraph
import pandas as pd
import json
import logging
from typing import Dict
import schema

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class CSV_Parser:
    def __init__(self, client):
        """Initialize with a pydgraph client"""
        self.client = client
        self.logger = logging.getLogger(__name__)
        # store maps for nodes
        
        
    def set_schema(self, schema: str):
        """Set schema for the graph"""
        schema_str = schema
        
        return self.client.alter(pydgraph.Operation(schema=schema_str))
    
    
    def load_data(self, data_dir: str):
        """Load all CSV files from the directory"""
        try: 
            # process base nodes
            
            # Process relationships
            pass
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    
    def _create_mutation(self, data: Dict) -> Dict:
        """Create a mutation object for pydgraph"""
        txn = self.client.txn()
        try:
            mutation = json.dumps(data)
            assigned = txn.mutate(set_obj=data)
            txn.commit()
            return assigned
        finally:
            txn.discard()
            
            