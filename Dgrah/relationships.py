import pydgraph
import csv
import json
import logging
from typing import Dict


class Relationships:
    def __init__(self, client: pydgraph.DgraphClient, logger: logging.Logger):
        self.client = client
        self.logger = logger

    def create_user_relationships(self, file_path: str, user_uids: Dict):
        """Create relationships between users (follows, followers) and their trends/communities"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    user_uid = user_uids[row["user_id"]]

                    # Process follows relationships
                    if row["follows"]:
                        follows_list = row["follows"].split(",")
                        for followed_id in follows_list:
                            if followed_id in user_uids:
                                edges.append(
                                    {
                                        "uid": user_uid,
                                        "follows": {"uid": user_uids[followed_id]},
                                    }
                                )

                    # Process trends relationships
                    if row["trends"]:
                        trends_list = row["trends"].split(",")
                        for trend_id in trends_list:
                            edges.append(
                                {
                                    "uid": user_uid,
                                    "follows_trend": {"uid": "_:" + trend_id},
                                }
                            )

                    # Process community memberships
                    if row["communities"]:
                        communities_list = row["communities"].split(",")
                        for community_id in communities_list:
                            edges.append(
                                {
                                    "uid": user_uid,
                                    "member_of": {"uid": "_:" + community_id},
                                }
                            )

            self.logger.info(f"Creating {len(edges)} user relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()

    def create_post_relationships(self, file_path: str, post_uids: Dict, user_uids: Dict, 
                            community_uids: Dict, content_uids: Dict):
        """Create relationships for posts with authors, communities, comments, and content lifecycle"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["post_id"] not in post_uids:
                        self.logger.warning(f"Post ID {row['post_id']} not found in UIDs")
                        continue
                        
                    post_uid = post_uids[row["post_id"]]
                    
                    # Link to author
                    if row["author"] in user_uids:
                        edges.append({
                            "uid": post_uid,
                            "authored_by": {
                                "uid": user_uids[row["author"]]
                            }
                        })
                    
                    # Link to communities
                    if row["community"]:
                        for community_id in row["community"].split(","):
                            if community_id in community_uids:
                                edges.append({
                                    "uid": post_uid,
                                    "posted_in": {
                                        "uid": community_uids[community_id]
                                    }
                                })
                    
                    # Link to lifecycle content - Use the mapped UID instead of raw ID
                    if row["lifecycle"] and row["lifecycle"] in content_uids:
                        edges.append({
                            "uid": post_uid,
                            "has_lifecycle": {
                                "uid": content_uids[row["lifecycle"]]
                            }
                        })
            
            if not edges:
                self.logger.warning("No post relationships to create")
                return None
                
            self.logger.info(f"Creating {len(edges)} post relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        except Exception as e:
            self.logger.error(f"Error in create_post_relationships: {str(e)}")
            raise
        finally:
            txn.discard()

    def create_comment_relationships(
        self, file_path: str, comment_uids: Dict, user_uids: Dict, post_uids: Dict
    ):
        """Create relationships for comments with authors, posts, and likes"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["comment_id"] not in comment_uids:
                        self.logger.warning(f"Comment ID {row['comment_id']} not found in UIDs")
                        continue
                        
                    comment_uid = comment_uids[row["comment_id"]]
                    
                    # Link to author
                    if row["author"] in user_uids:
                        edges.append({
                            "uid": comment_uid,
                            "authored_by": {
                                "uid": user_uids[row["author"]]
                            }
                        })
                    
                    # Link to post
                    if row["post"] in post_uids:
                        edges.append({
                            "uid": comment_uid,
                            "on_post": {
                                "uid": post_uids[row["post"]]
                            }
                        })
                    
                    # Process likes
                    if row["liked_by"]:
                        for liker_id in row["liked_by"].split(","):
                            if liker_id in user_uids:
                                edges.append({
                                    "uid": user_uids[liker_id],
                                    "likes": {
                                        "uid": comment_uid
                                    }
                                })
            
            if not edges:
                self.logger.warning("No comment relationships to create")
                return None
                
            self.logger.info(f"Creating {len(edges)} comment relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        except Exception as e:
            self.logger.error(f"Error in create_comment_relationships: {str(e)}")
            raise
        finally:
            txn.discard()
            
            
    def create_pattern_relationships(self, file_path: str, pattern_uids: Dict, user_uids: Dict, community_uids: Dict):
        """Create relationships between patterns and users/communities"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    pattern_uid = pattern_uids[row["pattern_id"]]
                    
                    # Link to user
                    if row["user"] in user_uids:
                        edges.append({
                            "uid": pattern_uid,
                            "observed_in_user": {
                                "uid": user_uids[row["user"]]
                            }
                        })
                    
                    # Link to community
                    if row["community"] in community_uids:
                        edges.append({
                            "uid": pattern_uid,
                            "community": {
                                "uid": community_uids[row["community"]]
                            }
                        })
            
            self.logger.info(f"Creating pattern relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()
    
    
    def create_influence_relationships(self, file_path: str, influence_uids: Dict, user_uids: Dict):
        """Create relationships between influence scores and users"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["user"] in user_uids:
                        edges.append({
                            "uid": influence_uids[row["score_id"]],
                            "user": {
                                "uid": user_uids[row["user"]]
                            }
                        })
            
            self.logger.info(f"Creating influence relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()
        

    def create_activity_relationships(self, file_path: str, activity_uids, user_uids, community_uids):
        """Create relationships between activities and users, communities"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    activity_uid = activity_uids[row["activity_id"]]

                    # Link to user
                    if row["user"] in user_uids:
                        edges.append(
                            {
                                "uid": activity_uid,
                                "user": {"uid": user_uids[row["user"]]},
                            }
                        )

                    # Link to community
                    if row["community"] in community_uids:
                        edges.append(
                            {
                                "uid": activity_uid,
                                "community": {"uid": community_uids[row["community"]]},
                            }
                        )

            self.logger.info(f"Creating activity relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()
            
            
    def create_analytics_relationships(self, file_path: str, analytics_uids: Dict, user_uids: Dict):
        """Create relationships between analytics and users"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["user"] in user_uids:
                        edges.append({
                            "uid": analytics_uids[row["analytics_id"]],
                            "user": {
                                "uid": user_uids[row["user"]]
                            }
                        })
            
            self.logger.info(f"Creating analytics relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()
        
        
    def create_content_relationships(self, file_path: str, content_uids: Dict, 
                               post_uids: Dict, comment_uids: Dict, 
                               user_uids: Dict, community_uids: Dict):
        """Create relationships between content and related entities"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    content_uid = content_uids[row["content_id"]]
                    
                    # Link related posts
                    if row["related_posts"]:
                        for post_id in row["related_posts"].split(","):
                            if post_id in post_uids:
                                edges.append({
                                    "uid": content_uid,
                                    "related_posts": {
                                        "uid": post_uids[post_id]
                                    }
                                })
                    
                    # Link related comments
                    if row["related_comments"]:
                        for comment_id in row["related_comments"].split(","):
                            if comment_id in comment_uids:
                                edges.append({
                                    "uid": content_uid,
                                    "related_comments": {
                                        "uid": comment_uids[comment_id]
                                    }
                                })
                    
                    # Link related users
                    if row["related_users"]:
                        for user_id in row["related_users"].split(","):
                            if user_id in user_uids:
                                edges.append({
                                    "uid": content_uid,
                                    "related_users": {
                                        "uid": user_uids[user_id]
                                    }
                                })
                    
                    # Link related communities
                    if row["related_communities"]:
                        for community_id in row["related_communities"].split(","):
                            if community_id in community_uids:
                                edges.append({
                                    "uid": content_uid,
                                    "related_communities": {
                                        "uid": community_uids[community_id]
                                    }
                                })
            
            self.logger.info(f"Creating content relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()
            
            
    
    def create_hashtag_relationships(self, file_path: str, hashtag_uids: Dict, 
                                post_uids: Dict, comment_uids: Dict):
        """Create relationships between hashtags and posts/comments"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    hashtag_uid = hashtag_uids[row["hashtag_id"]]
                    
                    # Link posts using this hashtag
                    if row["posts"]:
                        for post_id in row["posts"].split(","):
                            if post_id in post_uids:
                                edges.append({
                                    "uid": hashtag_uid,
                                    "posts": {
                                        "uid": post_uids[post_id]
                                    }
                                })
                    
                    # Link comments using this hashtag
                    if row["comments"]:
                        for comment_id in row["comments"].split(","):
                            if comment_id in comment_uids:
                                edges.append({
                                    "uid": hashtag_uid,
                                    "comments": {
                                        "uid": comment_uids[comment_id]
                                    }
                                })
            
            self.logger.info(f"Creating hashtag relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()
            
    
    def create_community_relationships(self, file_path: str, community_uids: Dict, 
                                 user_uids: Dict, post_uids: Dict, pattern_uids: Dict):
        """Create relationships between communities and their members, posts, admins, and patterns"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    community_uid = community_uids[row["community_id"]]
                    
                    # Connect members
                    if row["members"]:
                        for member_id in row["members"].split(","):
                            if member_id in user_uids:
                                edges.append({
                                    "uid": community_uid,
                                    "members": {
                                        "uid": user_uids[member_id]
                                    }
                                })
                    
                    # Connect posts
                    if row["posts"]:
                        for post_id in row["posts"].split(","):
                            if post_id in post_uids:
                                edges.append({
                                    "uid": community_uid,
                                    "post": {
                                        "uid": post_uids[post_id]
                                    }
                                })
                    
                    # Connect admins
                    if row["admins"]:
                        for admin_id in row["admins"].split(","):
                            if admin_id in user_uids:
                                edges.append({
                                    "uid": community_uid,
                                    "admins": {
                                        "uid": user_uids[admin_id]
                                    }
                                })
                    
                    # Connect patterns
                    if row["patterns"]:
                        for pattern_id in row["patterns"].split(","):
                            if pattern_id in pattern_uids:
                                edges.append({
                                    "uid": community_uid,
                                    "patterns": {
                                        "uid": pattern_uids[pattern_id]
                                    }
                                })
            
            self.logger.info(f"Creating community relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()
            
            
    def create_trend_relationships(self, file_path: str, trend_uids: Dict, user_uids: Dict):
        """Create relationships between trends and their followers"""
        txn = self.client.txn()
        try:
            edges = []
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    trend_uid = trend_uids[row["trend_id"]]
                    
                    # Connect followers
                    if row["followers"]:
                        for follower_id in row["followers"].split(","):
                            if follower_id in user_uids:
                                edges.append({
                                    "uid": trend_uid,
                                    "followers": {
                                        "uid": user_uids[follower_id]
                                    }
                                })
                                # Also create the reverse relationship
                                edges.append({
                                    "uid": user_uids[follower_id],
                                    "follows_trend": {
                                        "uid": trend_uid
                                    }
                                })
            
            self.logger.info(f"Creating trend relationships")
            resp = txn.mutate(set_obj=edges)
            txn.commit()
            return resp
        finally:
            txn.discard()