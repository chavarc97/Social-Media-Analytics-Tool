import pydgraph
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
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


def create_user(
    client,
    username: str,
    email: str,
    bio: Optional[str] = None,
    is_admin: bool = False,
    follower_count: int = 0,
    following_count: int = 0,
    is_active: bool = True
) -> str:

    txn = client.txn()
    try:
        # First check if username or email already exists
        check_query = """
        query checkUser($u: string, $e: string) {
            existing_username(func: eq(username, $u)) {
                uid
            }
            existing_email(func: eq(email, $e)) {
                uid
            }
        }
        """
        variables = {'$u': username, '$e': email}
        resp = txn.query(check_query, variables=variables)
        resp_json = json.loads(resp.json)

        if resp_json.get('existing_username'):
            logger.error(f"Username '{username}' already exists")
            raise Exception(f"Username '{username}' already exists")
        if resp_json.get('existing_email'):
            logger.error(f"Email '{email}' already exists")
            raise Exception(f"Email '{email}' already exists")

        # Prepare user data
        user_data = f"""
          _:user <dgraph.type> "User" .
          _:user <username> "{username}" .
          _:user <email> "{email}" .
          _:user <joinDate> "{datetime.now().isoformat()}" .
          _:user <isAdmin> "{str(is_admin).lower()}"^^<xs:boolean> .
          _:user <isActive> "{str(is_active).lower()}"^^<xs:boolean> .
          _:user <follower_count> "{follower_count}"^^<xs:int> .
          _:user <following_count> "{following_count}"^^<xs:int> .
        """

        # Add optional fields if provided
        if bio:
            user_data += f'_:user <bio> "{bio}" .\n'

    # Convert nquads to bytes
        user_data_bytes = user_data.encode('utf-8')
        # Create mutation using nquads
        mutation = pydgraph.Mutation(set_nquads=user_data_bytes)

        # Execute mutation
        response = txn.mutate(mutation=mutation)

        # Commit transaction
        txn.commit()

        # Get the UID of the created user
        if response.uids:
            return response.uids.get('user')
        else:
            logger.error("No UID returned for created user")
            raise Exception("Failed to create user - no UID returned")

    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise
    finally:
        txn.discard()

def create_post(
    client,
    author_uid: str,
    content: str,
    hashtags: Optional[List[str]] = None,
    community_uid: Optional[str] = None,
) -> str:
    """Create a new post in Dgraph"""
    txn = client.txn()
    try:
        # Prepare post data as NQuads
        nquads = f"""
            _:post <dgraph.type> "Post" .
            _:post <content> "{content}" .
            _:post <created_at> "{datetime.now().isoformat()}" .
            _:post <likes_count> "0"^^<xs:int> .
            _:post <shares_count> "0"^^<xs:int> .
            _:post <is_archived> "false"^^<xs:boolean> .
            _:post <author> <{author_uid}> .
        """
        
        if community_uid:
            nquads += f'_:post <communities> <{community_uid}> .\n'
            
        if hashtags:
            for tag in hashtags:
                nquads += f"""
                    _:hashtag_{tag} <dgraph.type> "Hashtag" .
                    _:hashtag_{tag} <name> "{tag}" .
                    _:hashtag_{tag} <usage_count> "1"^^<xs:int> .
                    _:hashtag_{tag} <trending_score> "1.0"^^<xs:float> .
                    _:post <hashtags> _:hashtag_{tag} .
                """

        # Convert to bytes and execute mutation
        mutation = pydgraph.Mutation(set_nquads=nquads.encode('utf-8'))
        response = txn.mutate(mutation=mutation)
        txn.commit()

        if response.uids:
            return response.uids.get('post')
        else:
            raise Exception("Failed to create post - no UID returned")

    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise
    finally:
        txn.discard()

def follow_user(client, follower_uid: str, target_uid: str) -> bool:
    """Make one user follow another user"""
    # Clean the UIDs - remove spaces and ensure proper format
    follower_uid = follower_uid.strip()
    target_uid = target_uid.strip()
    txn = client.txn()
    try:
        query = f"""
        query {{
            follows(func: uid({follower_uid})) {{
                follows @filter(uid({target_uid})) {{
                    uid
                }}
            }}
        }}
        """
        resp = txn.query(query)
        resp_json = json.loads(resp.json)

        if resp_json.get('follows') and resp_json['follows'][0].get('follows'):
            raise Exception("Already following this user")

        # Create follow relationship
        nquads = f"""
            <{follower_uid}> <follows> <{target_uid}> .
            <{target_uid}> <followers> <{follower_uid}> .
        """

        # Also update the follower count
        query_count = f"""
        query {{
            user(func: uid({target_uid})) {{
                uid
                follower_count
            }}
        }}
        """
        count_resp = txn.query(query_count)
        count_json = json.loads(count_resp.json)
        
        current_count = 0
        if count_json.get('user') and len(count_json['user']) > 0:
            current_count = int(count_json['user'][0].get('follower_count', 0))
        
        nquads += f"""
            <{target_uid}> <follower_count> "{current_count + 1}"^^<xs:int> .
        """

        mutation = pydgraph.Mutation(set_nquads=nquads.encode('utf-8'))
        txn.mutate(mutation=mutation)
        txn.commit()
        return True

    except Exception as e:
        logger.error(f"Error following user: {e}")
        raise
    finally:
        txn.discard()

def join_community(client, user_uid: str, community_uid: str) -> bool:
    """Add user to a community"""
    # Clean the UIDs
    user_uid = user_uid.strip()
    community_uid = community_uid.strip()
    
    txn = client.txn()
    try:
        # Check if already a member using direct uid filtering
        query = f"""
        query {{
            community(func: uid({community_uid})) {{
                members @filter(uid({user_uid})) {{
                    uid
                }}
            }}
        }}
        """
        resp = txn.query(query)
        resp_json = json.loads(resp.json)

        if resp_json.get('community') and resp_json['community'][0].get('members'):
            raise Exception("Already a member of this community")

        # Add user to community
        nquads = f"""
            <{community_uid}> <members> <{user_uid}> .
            <{user_uid}> <communities> <{community_uid}> .
        """

        mutation = pydgraph.Mutation(set_nquads=nquads.encode('utf-8'))
        txn.mutate(mutation=mutation)
        txn.commit()
        return True, logger.info(f"User {user_uid} joined community {community_uid}")

    except Exception as e:
        logger.error(f"Error joining community: {e}")
        raise
    finally:
        txn.discard()


def like_post(client, user_uid: str, post_uid: str) -> bool:
    """Like a post and update its likes count"""
    # Clean the UIDs
    user_uid = user_uid.strip()
    post_uid = post_uid.strip()
    
    txn = client.txn()
    try:
        # First check if already liked
        query = f"""
        query {{
            post(func: uid({post_uid})) {{
                uid
                likes_count
                liked_by @filter(uid({user_uid})) {{
                    uid
                }}
            }}
        }}
        """
        resp = txn.query(query)
        resp_json = json.loads(resp.json)

        if not resp_json.get('post'):
            raise Exception("Post not found")
            
        post_data = resp_json['post'][0]
        
        # Check if user already liked the post
        if post_data.get('liked_by'):
            raise Exception("You've already liked this post")

        current_likes = int(post_data.get('likes_count', 0))

        # Update likes count and add user to liked_by
        nquads = f"""
            <{post_uid}> <likes_count> "{current_likes + 1}"^^<xs:int> .
            <{post_uid}> <liked_by> <{user_uid}> .
        """

        mutation = pydgraph.Mutation(set_nquads=nquads.encode('utf-8'))
        txn.mutate(mutation=mutation)
        txn.commit()
        return True

    except Exception as e:
        logger.error(f"Error liking post: {e}")
        raise
    finally:
        txn.discard()

            
def list_available_users(client):
    """Get list of all users"""
    txn = client.txn()
    try:
        query = """
        {
            users(func: type(User)) {
                uid
                username
                email
            }
        }
        """
        resp = txn.query(query)
        data = json.loads(resp.json)
        return data.get('users', [])
    finally:
        txn.discard()

def list_available_communities(client):
    """Get list of all communities"""
    txn = client.txn()
    try:
        query = """
        {
            communities(func: type(Community)) {
                uid
                name
                description
            }
        }
        """
        resp = txn.query(query)
        data = json.loads(resp.json)
        return data.get('communities', [])
    finally:
        txn.discard()

def list_available_posts(client):
    """Get list of all posts"""
    txn = client.txn()
    try:
        query = """
        {
            posts(func: type(Post)) {
                uid
                content
                author {
                    username
                }
            }
        }
        """
        resp = txn.query(query)
        data = json.loads(resp.json)
        return data.get('posts', [])
    finally:
        txn.discard()

def social_menu(client, user_uid: str):
    """Interactive menu for social actions"""
    while True:
        print("\nSocial Actions Menu:")
        print("1. Create Post")
        print("2. Follow User")
        print("3. Join Community")
        print("4. Like Post")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        try:
            if choice == "1":
                content = input("Enter post content: ")
                hashtags = input("Enter hashtags (comma-separated) or press enter to skip: ")
                
                # Show available communities
                print("\nAvailable Communities:")
                communities = list_available_communities(client)
                for comm in communities:
                    print(f"UID: {comm['uid']} - Name: {comm['name']}")
                    
                community_uid = input("\nEnter community UID or press enter to skip: ")
                
                hashtag_list = None
                if hashtags:
                    hashtag_list = [tag.strip() for tag in hashtags.split(',') if tag.strip()]
                
                comm_uid = None
                if community_uid:
                    comm_uid = community_uid.strip()
                    if not comm_uid.startswith('0x'):
                        comm_uid = '0x' + comm_uid
                
                post_uid = create_post(client, user_uid, content, hashtag_list, comm_uid)
                print(f"Post created successfully! UID: {post_uid}")
                
            elif choice == "2":
                print("\nAvailable Users:")
                users = list_available_users(client)
                for user in users:
                    if user['uid'] != user_uid:  # Don't show current user
                        print(f"UID: {user['uid']} - Username: {user['username']}")
                        
                target_uid = input("\nEnter UID of user to follow: ").strip()
                if not target_uid.startswith('0x'):
                    target_uid = '0x' + target_uid
                follow_user(client, user_uid, target_uid)
                print("Successfully followed user!")
                
            elif choice == "3":
                print("\nAvailable Communities:")
                communities = list_available_communities(client)
                for comm in communities:
                    print(f"UID: {comm['uid']} - Name: {comm['name']}")
                    print(f"Description: {comm['description']}")
                    print("-" * 40)
                    
                community_uid = input("\nEnter community UID: ").strip()
                if not community_uid.startswith('0x'):
                    community_uid = '0x' + community_uid
                join_community(client, user_uid, community_uid)
                print("Successfully joined community!")
                
            elif choice == "4":
                print("\nAvailable Posts:")
                posts = list_available_posts(client)
                for post in posts:
                    author = post.get('author', {}).get('username', 'Unknown')
                    print(f"UID: {post['uid']}")
                    print(f"Author: {author}")
                    print(f"Content: {post['content'][:50]}...")  # Show first 50 chars
                    print("-" * 40)
                    
                post_uid = input("\nEnter post UID: ").strip()
                if not post_uid.startswith('0x'):
                    post_uid = '0x' + post_uid
                like_post(client, user_uid, post_uid)
                print("Successfully liked post!")
                
            elif choice == "5":
                break
                
            else:
                print("Invalid choice. Please try again.")
                
        except Exception as e:
            print(f"Error: {str(e)}")