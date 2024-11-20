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
        
        
    def set_schema(self, schema):
        """Set schema for the graph"""
        schema_str = schema
        try:
            self.logger.info(f"Setting schema: {schema_str}")
            return self.client.alter(pydgraph.Operation(schema=schema_str))
        except Exception as e:
            self.logger.error(f"Error setting schema: {str(e)}")
            raise
    
    def load_schema(self):
        users = self.set_schema(schema.user_schema)
        posts = self.set_schema(schema.post_schema)
        comments = self.set_schema(schema.comment_schema)
        communities = self.set_schema(schema.community_schema)
        trends = self.set_schema(schema.trend_schema)
        analytics = self.set_schema(schema.analytics_schema)
        patterns = self.set_schema(schema.pattern_schema)
        activities = self.set_schema(schema.activity_schema)
        influences = self.set_schema(schema.influence_schema)
        content = self.set_schema(schema.content_schema)
        self.logger.info(f"Schema loaded: {users, posts, comments, communities, trends, analytics, patterns, activities, influences, content}")
    
    def load_data(self, data_dir: str):
        """Load all CSV files from the directory"""
        try: 
            # process base nodes
            self._load_users(f"{data_dir}/users.csv")
            self._load_posts(f"{data_dir}/post.csv")
            self._load_comments(f"{data_dir}/comment.csv")
            self._load_communities(f"{data_dir}/communities.csv")
            self._load_trends(f"{data_dir}/trends.csv")
            self._load_analytics(f"{data_dir}/analytics.csv")
            self._load_patterns(f"{data_dir}/patterns.csv")
            self._load_activities(f"{data_dir}/activity.csv")
            self._load_influences(f"{data_dir}/influence.csv")
            self._load_content(f"{data_dir}/content.csv")
            
            pass
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
        
        
    def drop_all(self):
        """Drop all data from the graph"""
        try:
            self.logger.info("Dropping all data from the graph")
            return self.client.alter(pydgraph.Operation(drop_all=True))
        except Exception as e:
            self.logger.error(f"Error dropping data: {str(e)}")
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
     
    """
    Load data into the graph using the following methods:
    """        
    def _load_users(self, file_path: str) -> Dict:
        """Load users into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} users from {file_path}")
        
        for _, row in df.iterrows():
            try:
                user_data = {
                    "dgraph.type": "User",
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "email": row["email"],
                    "bio": row["bio"],
                    "joinDate": row["joinDate"],
                    "isAdmin": bool(row["isAdmin"]),
                    "followerCount": int(row["followerCount"]),
                    "isActive": bool(row["isActive"]),
                    "following_count": int(row["following_count"]),
                    "follows": [].append(row["follows"].split(",")),
                    "followers": [].append(row["followers"].split(",")),
                    "trends": [].append(row["trends"].split(",")),
                    "communities": [].append(row["communities"].split(","))     
                }
                assigned = self._create_mutation(user_data)
                uid_map[row["user_id"]] = assigned
                self.logger.info(f"User {row['user_id']} loaded")
                
            except Exception as e:
                self.logger.error(f"Error loading user: {str(e)}")
                continue
            
            self.logger.info(f"Successfully loaded {len(uid_map)} users")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} users")
            
            self.logger.debug("User ID to UID mapping:")
            for user_id, uid in uid_map.items():
                self.logger.debug(f"{user_id} -> {uid}")
                
    
    def _load_posts(self, file_path: str) -> Dict:
        """Load posts into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} posts from {file_path}")
            
        for _, row in df.iterrows():
            try:
                post_data = {
                    "dgraph.type": "Post",
                    "post_id": row["post_id"],
                    "content": row["content"],
                    "created_at": row["created_at"],
                    "likes_count": int(row["likes_count"]),
                    "shares_count": int(row["shares_count"]),
                    "hashtags": [].append(row["hashtags"].split(",")),
                    "author": row["author"],
                    "comments": [].append(row["comments"].split(",")),
                    "community": [].append(row["community"].split(",")),
                    "is_archived": bool(row["is_archived"]),
                    "lifecycle": row["lifecycle"]
                }
                assigned = self._create_mutation(post_data)
                uid_map[row["post_id"]] = assigned
                self.logger.info(f"Post {row['post_id']} loaded")
                    
            except Exception as e:
                self.logger.error(f"Error loading post: {str(e)}")
                continue
            
            self.logger.info(f"Successfully loaded {len(uid_map)} posts")
            
    
    def _load_comments(self, file_path: str) -> Dict:
        """Load comments into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} comments from {file_path}")
        try:
            for _, row in df.iterrows():
                comment_data = {
                    "dgraph.type": "Comment",
                    "comment_id": row["comment_id"],
                    "content": row["content"],
                    "created_at": row["created_at"],
                    "likes_count": int(row["likes_count"]),
                    "liked_by": [].append(row["liked_by"].split(",")),
                    "author": row["author"],
                    "post": row["post"],
                    "lifecycle": row["lifecycle"],
                    "sentiment_score": float(row["sentiment_score"])
                }
                assigned = self._create_mutation(comment_data)
                uid_map[row["comment_id"]] = assigned
                self.logger.info(f"Comment {row['comment_id']} loaded")
        except Exception as e:
            self.logger.error(f"Error loading comment: {str(e)}")
            raise
        
        if len(uid_map) < len(df):
            self.logger.warning(f"Failed to load {len(df) - len(uid_map)} comments")
        else:
            self.logger.info(f"Successfully loaded {len(uid_map)} comments")
            
    # Load Communities
    def _load_communities(self, file_path: str) -> Dict:
        """Load communities into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} communities from {file_path}")
        
        for _, row in df.iterrows():
            try:
                community_data = {
                    "dgraph.type": "Community",
                    "community_id": row["community_id"],
                    "name": row["name"],
                    "description": row["description"],
                    "created_at": row["created_at"],
                    "members": [].append(row["members"].split(",")),
                    "posts": [].append(row["posts"].split(",")),
                    "admins": [].append(row["admins"].split(",")),
                    "patterns": [].append(row["patterns"].split(",")),
                    "health_score": float(row["health_score"])
                }
                assigned = self._create_mutation(community_data)
                uid_map[row["community_id"]] = assigned
                self.logger.info(f"Community {row['community_id']} loaded")
            except Exception as e:
                self.logger.error(f"Error loading community: {str(e)}")
                continue
            
            self.logger.info(f"Successfully loaded {len(uid_map)} communities")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} communities")
            
            self.logger.debug("Community ID to UID mapping:")
            for community_id, uid in uid_map.items():
                self.logger.debug(f"{community_id} -> {uid}")
                
    
    def _load_trends(self, file_path: str) -> Dict:
        """Load trends into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} trends from {file_path}")
        
        for _, row in df.iterrows():
            try:
                trend_data = {
                    "dgraph.type": "Trend",
                    "trend_id": row["trend_id"],
                    "name": row["name"],
                    "followers": [].append(row["followers"].split(",")),
                    "score": float(row["score"]),
                    "start_date": row["start_date"]
                }
                assigned = self._create_mutation(trend_data)
                uid_map[row["trend_id"]] = assigned
                self.logger.info(f"Trend {row['trend_id']} loaded")
            except Exception as e:
                self.logger.error(f"Error loading trend: {str(e)}")
                continue
            self.logger.info(f"Successfully loaded {len(uid_map)} trends")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} trends")

    
    def _load_analytics(self, file_path: str) -> Dict:
        """Load analytics into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} analytics from {file_path}")
        
        for _, row in df.iterrows():
            try:
                analytics_data = {
                    "dgraph.type": "Analytics",
                    "analytics_id": row["analytics_id"],
                    "user": row["user"],
                    "metric_type": row["metric_type"],
                    "value": float(row["value"]),
                    "timestamp": row["timestamp"]
                }
                assigned = self._create_mutation(analytics_data)
                uid_map[row["analytics_id"]] = assigned
                self.logger.info(f"Analytics {row['analytics_id']} loaded")
            except Exception as e:
                self.logger.error(f"Error loading analytics: {str(e)}")
                continue
            self.logger.info(f"Successfully loaded {len(uid_map)} analytics")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} analytics")

    
    def _load_patterns(self, file_path: str) -> Dict:
        """Load patterns into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} patterns from {file_path}")
        
        for _, row in df.iterrows():
            try:
                pattern_data = {
                    "dgraph.type": "Pattern",
                    "pattern_id": row["pattern_id"],
                    "user": row["user"],
                    "community": row["community"],
                    "type": row["type"],
                    "frequency": float(row["frequency"]),
                    "last_seen": row["last_seen"],
                }
                assigned = self._create_mutation(pattern_data)
                uid_map[row["pattern_id"]] = assigned
                self.logger.info(f"Pattern {row['pattern_id']} loaded")
            except Exception as e:
                self.logger.error(f"Error loading pattern: {str(e)}")
                continue
            self.logger.info(f"Successfully loaded {len(uid_map)} patterns")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} patterns")

    
    def _load_activities(self, file_path: str) -> Dict:
        """Load activities into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        
        self.logger.info(f"Loading {len(df)} activities from {file_path}")
        
        for _, row in df.iterrows():
            try:
                activity_data = {
                    "dgraph.type": "Activity",
                    "activity_id": row["activity_id"],
                    "type": row["type"],
                    "timestamp": row["timestamp"],
                    "user": row["user"],
                    "duration": float(row["duration"]),
                    "community": row["community"],
                }
                assigned = self._create_mutation(activity_data)
                uid_map[row["activity_id"]] = assigned
                self.logger.info(f"Activity {row['activity_id']} loaded")
            except Exception as e:
                self.logger.error(f"Error loading activity: {str(e)}")
                continue
            self.logger.info(f"Successfully loaded {len(uid_map)} activities")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} activities")

    
    def _load_influences(self, file_path: str) -> Dict:
        """Load influences into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} influences from {file_path}")
        
        for _, row in df.iterrows():
            try:
                influence_data = {
                    "dgraph.type": "Influence",
                    "score_id": row["score_id"],
                    "user": row["user"],
                    "score_value": float(row["score_value"]),
                    "computed_at": row["computed_at"],
                    "factors": [].append(row["factors"].split(","))
                }
                assigned = self._create_mutation(influence_data)
                uid_map[row["influence_id"]] = assigned
                self.logger.info(f"Influence {row['influence_id']} loaded")
            except Exception as e:
                self.logger.error(f"Error loading influence: {str(e)}")
                continue
            self.logger.info(f"Successfully loaded {len(uid_map)} influences")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} influences")

    
    def _load_content(self, file_path: str) -> Dict:
        """Load content into the graph"""
        df = pd.read_csv(file_path)
        uid_map = {}
        self.logger.info(f"Loading {len(df)} content from {file_path}")
        
        for _, row in df.iterrows():
            try:
                content_data = {
                    "dgraph.type": "Content",
                    "content_id": row["content_id"],
                    "type": row["type"],
                    "created_at": row["created_at"],
                    "engagement_rate": float(row["engagement_rate"]),
                    "lifecycle_stage": row["lifecycle_stage"],
                    "related_posts": [].append(row["related_posts"].split(",")),
                    "related_comments": [].append(row["related_comments"].split(",")),
                    "related_users": [].append(row["related_users"].split(",")),
                    "related_communities": [].append(row["related_communities"].split(","))
                }
                assigned = self._create_mutation(content_data)
                uid_map[row["content_id"]] = assigned
                self.logger.info(f"Content {row['content_id']} loaded")
            except Exception as e:
                self.logger.error(f"Error loading content: {str(e)}")
                continue
            self.logger.info(f"Successfully loaded {len(uid_map)} content")
            if len(uid_map) < len(df):
                self.logger.warning(f"Failed to load {len(df) - len(uid_map)} content")

    