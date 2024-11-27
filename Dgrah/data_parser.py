import pydgraph
import csv
import json
import logging
from typing import Dict
import os
from . import schema
from . import relationships

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
        self.logger.info(
            f"Schema loaded: {users, posts, comments, communities, trends, analytics, patterns, activities, influences, content}"
        )
        

    def load_data(self, data_dir: str):
        """Load all CSV files from the directory"""
        # Verify the directory exists
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        try:
            # process base nodes
            user_uids = self._load_users(f"{data_dir}/users.csv")
            posts = self._load_posts(f"{data_dir}/post.csv")
            comments = self._load_comments(f"{data_dir}/comment.csv")
            communities = self._load_communities(f"{data_dir}/communities.csv")
            trends = self._load_trends(f"{data_dir}/trends.csv")
            analytics = self.load_analytics(f"{data_dir}/analytics.csv")
            patterns = self._load_patterns(f"{data_dir}/patterns.csv")
            influences = self._load_influence_scores(f"{data_dir}/influence.csv")
            content = self._load_content(f"{data_dir}/content.csv")
            hashtags = self._load_hashtags(f"{data_dir}/hashtags.csv")
            activities = self._load_activities(f"{data_dir}/activity.csv")

            # create relationships
            rel = relationships.Relationships(self.client, self.logger)
            rel.create_user_relationships(f"{data_dir}/users.csv", user_uids)
            rel.create_post_relationships(f"{data_dir}/post.csv", posts, user_uids, communities, content)
            rel.create_comment_relationships(f"{data_dir}/comment.csv", comments, user_uids, posts)
            rel.create_pattern_relationships(f"{data_dir}/patterns.csv", patterns, user_uids, communities)
            rel.create_influence_relationships(f"{data_dir}/influence.csv", influences, user_uids)
            rel.create_analytics_relationships(f"{data_dir}/analytics.csv", analytics, user_uids)
            rel.create_activity_relationships(f"{data_dir}/activity.csv", activities, user_uids, communities)
            rel.create_content_relationships(f"{data_dir}/content.csv", content, posts, comments, user_uids, communities)
            rel.create_hashtag_relationships(f"{data_dir}/hashtags.csv", hashtags, posts, comments)
            rel.create_community_relationships(f"{data_dir}/communities.csv", communities, user_uids, posts, patterns)
            rel.create_trend_relationships(f"{data_dir}/trends.csv", trends, user_uids)
            
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
        
    def delete_user(self):
        """Delete users with influenceScore less than a given threshold"""
        min_influence = 50.0
        query = """
        query findUsers($min_influence: float) {
            usersToDelete(func: lt(influenceScore, $min_influence)) {
                uid
            }
        }
        """
        variables = {
            '$min_influence': str(min_influence)
        }
        try:
            # Step 1: Query users that match the condition
            res = self.client.txn(read_only=True).query(query, variables=variables)
            result = json.loads(res.json)
            
            # Step 2: Prepare the mutation for deletion
            users_to_delete = result.get("usersToDelete", [])
            if users_to_delete:
                uids_to_delete = [user["uid"] for user in users_to_delete]
                mutation = {
                    "delete": [{"uid": uid} for uid in uids_to_delete]
                }
                # Step 3: Perform the delete mutation
                self.client.txn().mutate(set_json=mutation)
                print(f"Deleted {len(uids_to_delete)} users.")
            else:
                print("No users found to delete.")

        except Exception as e:
            print(f"Error deleting users: {str(e)}")
            
        
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
        txn = self.client.txn()
        resp = None
        try:
            users = []
            with open(file_path, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    users.append(
                        {
                            "dgraph.type": "User",
                            "uid": "_:" + row["user_id"],
                            "username": row["username"],
                            "email": row["email"],
                            "bio": row["bio"],
                            "joinDate": row["joinDate"],
                            "isAdmin": bool(row["isAdmin"]),
                            "followerCount": int(row["followerCount"]),
                            "isActive": bool(row["isActive"]),
                            "following_count": int(row["following_count"]),
                        }
                    )
            self.logger.info(f"Loading {len(users)} users from {file_path}")
            resp = txn.mutate(set_obj=users)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids

    def _load_trends(self, file_path: str) -> Dict:
        """Load trends into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            trends = []
            with open(file_path, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    trends.append(
                        {
                            "dgraph.type": "Trend",
                            "uid": "_:" + row["trend_id"],
                            "name": row["name"],
                            "score": float(row["score"]),
                            "start_date": row["start_date"],
                        }
                    )

            self.logger.info(f"Loading {len(trends)} trends from {file_path}")
            resp = txn.mutate(set_obj=trends)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids

    def _load_communities(self, file_path: str) -> Dict:
        """Load communities into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            communities = []
            with open(file_path, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    communities.append(
                        {
                            "dgraph.type": "Community",
                            "uid": "_:" + row["community_id"],
                            "name": row["name"],
                            "description": row["description"],
                            "created_at": row["created_at"],
                            "health_score": float(row["health_score"]),
                        }
                    )

            self.logger.info(f"Loading {len(communities)} communities from {file_path}")
            resp = txn.mutate(set_obj=communities)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids

    def load_analytics(self, file_path: str) -> Dict:
        """Load analytics into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            analytics = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    analytics.append({
                        'dgraph.type': 'Analytics',
                        'uid': '_:' + row["analytics_id"],
                        'metric_type': row["metric_type"],
                        'value': float(row["value"]),
                        'timestamp': row["timestamp"]
                    })
            
            self.logger.info(f"Loading {len(analytics)} analytics")
            resp = txn.mutate(set_obj=analytics)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids

    def _load_activities(self, file_path: str) -> Dict:
        """Load activities into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            activities = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    activities.append({
                        'dgraph.type': 'Activity',
                        'uid': '_:' + row["activity_id"],
                        'type': row["type"],
                        'timestamp': row["timestamp"],
                        'duration': float(row["duration"])
                    })
            
            self.logger.info(f"Loading {len(activities)} activities")
            resp = txn.mutate(set_obj=activities)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids
    
    
    def _load_comments(self, file_path: str) -> Dict:
        """Load comments into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            comments = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    comments.append({
                        'dgraph.type': 'Comment',
                        'uid': '_:' + row["comment_id"],
                        'content': row["content"],
                        'created_at': row["created_at"],
                        'likes_count': int(row["likes_count"]),
                        'sentiment_score': float(row["sentiment_score"])
                    })
            
            self.logger.info(f"Loading {len(comments)} comments")
            resp = txn.mutate(set_obj=comments)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids
    
    
    def _load_content(self, file_path: str) -> Dict:
        """Load content into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            contents = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    contents.append({
                        'dgraph.type': 'Content',
                        'uid': '_:' + row["content_id"],
                        'type': row["type"],
                        'created_at': row["created_at"],
                        'engagement_rate': float(row["engagement_rate"]),
                        'lifecycle_stage': row["lifecycle_stage"]
                    })
            
            self.logger.info(f"Loading {len(contents)} contents")
            resp = txn.mutate(set_obj=contents)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids
    
    def _load_hashtags(self, file_path: str) -> Dict:
        """Load hashtags into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            hashtags = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    hashtags.append({
                        'dgraph.type': 'Hashtag',
                        'uid': '_:' + row["hashtag_id"],
                        'name': row["name"],
                        'usage_count': int(row["usage_count"]),
                        'trending_score': float(row["trending_score"])
                    })
            
            self.logger.info(f"Loading {len(hashtags)} hashtags")
            resp = txn.mutate(set_obj=hashtags)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids
    
    def _load_influence_scores(self, file_path: str) -> Dict:
        """Load influence scores into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            influence_scores = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    influence_scores.append({
                        'dgraph.type': 'InfluenceScore',
                        'uid': '_:' + row["score_id"],
                        'score_value': float(row["score_value"]),
                        'computed_at': row["computed_at"],
                        'factors': row["factors"].split(",")
                    })
            
            self.logger.info(f"Loading {len(influence_scores)} influence scores")
            resp = txn.mutate(set_obj=influence_scores)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids
    
    def _load_patterns(self, file_path: str) -> Dict:
        """Load user patterns into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            patterns = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    patterns.append({
                        'dgraph.type': 'Pattern',
                        'uid': '_:' + row["pattern_id"],
                        'type': row["type"],
                        'frequency': float(row["frequency"]),
                        'last_seen': row["last_seen"]
                    })
            
            self.logger.info(f"Loading {len(patterns)} patterns")
            resp = txn.mutate(set_obj=patterns)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids
    
    def _load_posts(self, file_path: str) -> Dict:
        """Load posts into the graph"""
        txn = self.client.txn()
        resp = None
        try:
            posts = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    posts.append({
                        'dgraph.type': 'Post',
                        'uid': '_:' + row["post_id"],
                        'content': row["content"],
                        'created_at': row["created_at"],
                        'likes_count': int(row["likes_count"]),
                        'shares_count': int(row["shares_count"]),
                        'is_archived': row["is_archived"].lower() == 'true'
                    })
            
            self.logger.info(f"Loading {len(posts)} posts")
            resp = txn.mutate(set_obj=posts)
            txn.commit()
        finally:
            txn.discard()
        return resp.uids
    
