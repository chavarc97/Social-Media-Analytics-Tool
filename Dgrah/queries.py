import json
import client as c
from typing import Dict
from datetime import datetime, timedelta


class Queries:
    def __init__(self, client):
        self.client = client

    def query_menu(self):
        qm_options = {
            1: "Track content interactions for a given user",
            2: "analyze follower network",
            3: "get trending topics",
            4: "Generate user feed",
            5: "Monitor community health metrics",
            6: "Analyze user behavior patterns",
            7: "Get personalized content recommendations",
            8: "Get detailed performance metrics for a post",
            9: "Analyze network growth",
            10: "Calculate user influence",
            11: "Analyze content lifecycle patterns",
            12: "Exit"
        }
        for key in qm_options.keys():
            print(key, '--', qm_options[key])

        while True:
            option = int(input('Enter option: '))
            match option:
                case 1:
                    c.clear_screen()
                    users = self.available_usrs()
                    self.print_dict(users)
                    user = str(input('Enter username: '))
                    print("**********************************************")
                    print('Tracking user interactions...')
                    print("**********************************************")
                    self.track_user_interactions(user)
                    break
                case 2:
                    c.clear_screen()
                    users = self.available_usrs()
                    self.print_dict(users)
                    user = str(input('Enter username: '))
                    print("**********************************************")
                    print('Analyzing follower network...')
                    print("**********************************************")
                    self.analyze_follower_network(user)
                    break
                case 3:
                    c.clear_screen()
                    print("**********************************************")
                    print('Getting trending topics...')
                    print("**********************************************")
                    self.get_trending_topics()
                    break
                case 4:
                    c.clear_screen()
                    print("**********************************************")
                    print('Generating user feed...')
                    print("**********************************************")
                    users = self.available_usrs()
                    self.print_dict(users)
                    user = str(input('Enter username: '))
                    self.generate_user_feed(user)
                    break
                case 5:
                    c.clear_screen()
                    print("**********************************************")
                    print('Monitoring community health metrics...')
                    print("**********************************************")
                    comunities = self.available_communities()
                    self.print_dict(comunities)
                    community = str(input('Enter community name: '))
                    self.monitor_community_health(community)
                    break
                case 6:
                    c.clear_screen()
                    print("**********************************************")
                    print('Analyzing user behavior patterns...')
                    print("**********************************************")
                    users = self.available_usrs()
                    self.print_dict(users)
                    user = str(input('Enter username: '))
                    self.analyze_user_patterns(user)
                    break
                case 7:
                    c.clear_screen()
                    print("**********************************************")
                    print('Getting personalized content recommendations...')
                    print("**********************************************")
                    users = self.available_usrs()
                    self.print_dict(users)
                    user = str(input('Enter username: '))
                    self.get_recommendations(user)
                    break
                case 8:
                    c.clear_screen()
                    print("**********************************************")
                    print('Getting performance metrics for a post...')
                    print("**********************************************")
                    print("""
                          Enter start date and end date in the format: YYYY-MM-DD
                          eg. 
                          start_date = "2024-01-12"
                          end_date = "2024-01-13" 
                          """)
                    start_date = str(input('Enter start date: '))
                    end_date = str(input('Enter end date: '))
                    try:
                        self.get_post_performance(start_date, end_date)
                    except Exception:
                        print("No data available for the given date range.")
                    finally:    
                        break
                case 9:
                    c.clear_screen()
                    print("**********************************************")
                    print('Analyzing network growth...')
                    print("**********************************************")
                    print("Enter start date in the format: YYYY-MM-DD eg. 2024-01-01")
                    start_date = str(input('Enter start date: '))
                    try:
                        self.analyze_network_growth(start_date)
                    except Exception:
                        print("No data available for the given date range.")
                    finally:
                        break
                case 10:
                    c.clear_screen()
                    print("**********************************************")
                    print('Calculating user influence...')
                    print("**********************************************")
                    users = self.available_usrs()
                    self.print_dict(users)
                    user = str(input('Enter username: '))
                    self.calculate_user_influence(user)
                    break
                case 11:
                    c.clear_screen()
                    print("**********************************************")
                    print('Analyzing content lifecycle patterns...')
                    print("**********************************************")
                    self.analyze_content_lifecycle_patterns()
                    break
                    c.print_menu()
                case 12:
                    # go back to main menu
                    c.clear_screen()
                    c.print_menu()
                    break
                case _:
                    print('Invalid option')
                    break

    def track_user_interactions(self, username: str):
        """Track all content interactions for a given user"""
        query = """
        query UserInteractions($username: string) {
        user(func: eq(username, $username)) {
            username
            email
            bio
            joinDate
            followerCount
            following_count
            isActive
            isAdmin
            
            # Posts created by user
            posts: ~author @filter(eq(dgraph.type, "Post")) {
                uid
                content
                created_at
                likes_count
                shares_count
                # Community where post was made
                posted_in {
                    name
                }
            }
            
            # Comments by user
            comments: ~author @filter(eq(dgraph.type, "Comment")) {
                uid
                content
                created_at
                likes_count
                sentiment_score
                # Post that was commented on
                on_post {
                    content
                    created_at
                }
            }
            
            # Communities the user belongs to
            member_of {
                name
                description
                health_score
                created_at
            }
            
            # Trends user follows
            follows_trend {
                name
                score
                start_date
            }
            
            # Users being followed
            follows {
                username
                followerCount
            }
            
            # Activities
            activities: ~user @filter(eq(dgraph.type, "Activity")) {
                type
                timestamp
                duration
                # Community where activity occurred
                community {
                    name
                }
            }
            
            # Analytics data
            analytics: ~user @filter(eq(dgraph.type, "Analytics")) {
                metric_type
                value
                timestamp
            }
            
            # Influence score
            influence: ~user @filter(eq(dgraph.type, "InfluenceScore")) {
                score_value
                computed_at
                factors
            }
            
            # User patterns
            patterns: ~user {
                type
                frequency
                last_seen
            }
        }
    }
        """
        variables = {'$username': username}
        return self._run_query(query, variables)

    def analyze_follower_network(self, username: str):
        """Analyze follower network"""
        query = """
        query FollowerNetwork($username: string) {
            user(func: eq(username, $username)) {
                username
                followerCount: count(~followers)
                following_count: count(follows)
                
                # People who follow this user
                followers: ~follows {
                    uid
                    username
                    followerCount
                }
                
                # People this user follows
                following: follows {
                    uid
                    username
                    followerCount
                }
            }
        }
        """
        variables = {'$username': username}
        return self._run_query(query, variables)

    def get_trending_topics(self, limit: int = 10):
        """Get trending topics based on engagement"""
        query = """
        query TrendingTopics($limit: int) {
            trending(func: eq(dgraph.type, "Trend"), 
                    orderdesc: score, 
                    first: $limit) @filter(gt(score, 0)) {
                name
                score
                start_date
                
                # Count of followers
                follower_count: count(followers)
                
                # Get related posts
                related_posts: ~posts @filter(eq(dgraph.type, "Post")) {
                content
                likes_count
                shares_count
                }
            }
        }
        """
        variables = {'$limit': str(limit)}
        return self._run_query(query, variables)

    def generate_user_feed(self, username: str, limit: int = 20):
        """Generate personalized feed for user"""
        query = """
            query UserFeed($username: string, $limit: int) {
                user(func: eq(username, $username)) {
                    username
                    email
                    bio
                    joinDate
                    followerCount
                    following_count
                    isActive
                    
                    # Get users they follow and their posts
                    follows {
                        username
                        followerCount
                        isActive
                        # Get posts from each followed user
                        posts: ~author @filter(eq(dgraph.type, "Post")) {
                            uid
                            content
                            created_at
                            likes_count
                            shares_count
                            is_archived
                            hashtags
                            author {
                                username
                            }
                            posted_in {
                                name
                                description
                            }
                        }
                    }
                    
                    # Get communities they're members of
                    member_of {
                        uid
                        community_name
                        description
                        created_at
                        health_score
                        # Get posts in each community
                        post {
                            uid
                            content
                            created_at
                            likes_count
                            shares_count
                            is_archived
                            hashtags
                            author {
                                username
                                followerCount
                            }
                            # Get comments on posts
                            ~post {
                                content
                                likes_count
                                sentiment_score
                                author {
                                    username
                                }
                            }
                        }
                    }
                    
                    # Get user's trends
                    follows_trend {
                        name
                        score
                        start_date
                    }
                    
                    # Get user's activities
                    activities: ~user @filter(eq(dgraph.type, "Activity")) {
                        type
                        timestamp
                        duration
                        community {
                            name
                        }
                    }
                }
        }
        """
        variables = {'$username': str(username), '$limit': str(limit)}
        return self._run_query(query, variables)

    def monitor_community_health(self, community: str):
        """Monitor community health metrics"""
        query = """
        query CommunityHealth($community: string) {
            community(func: eq($community, name)) {
                name
                description
                health_score
                created_at
                
                # Member metrics
                member_count: count(members)
                admin_count: count(admins)
                
                # Activities in community
                activities: ~community @filter(eq(dgraph.type, "Activity")) {
                    type
                    timestamp
                    duration
                    user {
                        username
                    }
                }
                
                # Posts in community
                post {
                    total_posts: count(posted_in)
										total_likes: likes_count
                  	total_shares: shares_count
                }
                
                # Patterns in community
                patterns {
                    type
                    frequency
                    last_seen
                }
            }
        }
        """
        variables = {'$community': str(community)}
        return self._run_query(query, variables)

    def analyze_user_patterns(self, username: str):
        """Analyze user behavior patterns"""
        query = """
        query UserPatterns($username: string) {
            patterns(func: eq($username, username)) {
                username
                
                # User activities
                activities: ~user @filter(eq(dgraph.type, "Activity")) {
                    type
                    timestamp
                    duration
                    community {
                        name
                    }
                }
                
                # User communities
                member_of {
                    name
                    health_score
                    patterns {
                        type
                        frequency
                    }
                }
                
                # User posts
                posts: ~author @filter(eq(dgraph.type, "Post")) {
                    content
                    likes_count
                    shares_count
                    created_at
                }
            }
        }
        """
        variables = {'$username': username}
        return self._run_query(query, variables)

    def get_post_performance(self, start_date: str, end_date: str):
        """Get detailed performance metrics for a post"""
        query = """
            query content_analytics($start_date: string, $end_date: string) {
            # Get engagement metrics for posts
            posts(func: type(Post)) @filter(ge(created_at, $start_date) AND le(created_at, $end_date)) {
                uid
                content
                created_at
                likes_count
                shares_count
                engagement_rate: lifecycle {
                engagement_rate
                }
                comment_count: count(comments)
                comments {
                sentiment_score
                created_at
                likes_count
                replies: count(comments)
                }
            }
            
            # Get activity patterns
            activities(func: type(Activity)) @filter(ge(timestamp, $start_date) AND le(timestamp, $end_date)) {
                timestamp
                duration
                type
            }
            
            # Get content lifecycle stages
            content(func: type(Content)) @filter(ge(created_at, $start_date) AND le(created_at, $end_date)) {
                lifecycle_stage
                engagement_rate
                created_at
            }
        }
        """
        variables = {
            "$start_date": start_date,
            "$end_date": end_date
        }
        return self._run_query(query, variables)


    def get_recommendations(self, username: str, limit: int = 10):
        """Get personalized content recommendations"""
        query = """
        query Recommendations($username: string, $limit: int = 10) {
            # Get our user for context
            user(func: eq(username, $username)) @filter(type(User)) {
                username
                follows {
                    username
                }
            }

            # Food-related content based on hashtags - prioritize recent + high engagement
            food_recommendations(func: type(Post), orderdesc: likes_count, first: $limit) 
            @filter(has(content) AND 
                    regexp(content, /#food|#restaurant|#dining/i) AND 
                    ge(likes_count, 10) AND 
                    ge(created_at, "2024-01-01")) {
                content
                likes_count
                shares_count
                created_at
                author {
                    username
                }
                hashtags {
                    name
                }
            }

            # Art-related content based on hashtags and following interests
            art_recommendations(func: type(Post), orderdesc: likes_count, first: $limit) 
            @filter(has(content) AND 
                    regexp(content, /#art|#digital|#drawing|#artist/i) AND 
                    ge(likes_count, 10) AND 
                    ge(created_at, "2024-01-01")) {
                content
                likes_count
                shares_count
                created_at
                author {
                    username
                }
                hashtags {
                    name
                }
            }

            # General trending content excluding food and art
            trending_recommendations(func: type(Post), orderdesc: likes_count, first: $limit)
            @filter(has(content) AND 
                    NOT regexp(content, /#food|#restaurant|#art|#digital/i) AND
                    ge(likes_count, 10) AND 
                    ge(created_at, "2024-01-01")) {
                content
                likes_count
                shares_count
                created_at
                author {
                    username
                }
                hashtags {
                    name
                }
            }
        }
        """
        variables = {'$username': str(username), '$limit': str(limit)}
        return self._run_query(query, variables)

    def analyze_network_growth(self, start_date: str):
        """
        Analyze and predict network growth across multiple dimensions:
        - User growth and adoption
        - Community expansion
        - Content trends
        - Engagement patterns
        - Network connectivity
        """
        end_date = "2024-11-30"
        query = """
        query historical_data($start_date: string, $end_date: string) {
            # User data with all relevant connections
            users(func: type(User)) @filter(ge(joinDate, $start_date) AND le(joinDate, $end_date)) {
                uid
                username
                email
                bio
                joinDate
                isAdmin
                followerCount
                isActive
                following_count
                follows {
                uid
                username
                }
                followers {
                uid
                username
                }
                trends {
                uid
                name
                score
                }
                communities {
                uid
                name
                health_score
                }
            }
            
            # Community data with members and health metrics
            communities(func: type(Community)) @filter(ge(created_at, $start_date) AND le(created_at, $end_date)) {
                uid
                name
                description
                created_at
                health_score
                members {
                uid
                username
                }
                posts {
                uid
                content
                }
                admins {
                uid
                username
                }
                patterns {
                uid
                type
                frequency
                }
            }
            
            # Post data with full relationships
            posts(func: type(Post)) @filter(ge(created_at, $start_date) AND le(created_at, $end_date)) {
                uid
                content
                created_at
                likes_count
                shares_count
                is_archived
                hashtags {
                uid
                name
                }
                author: authored_by {
                uid
                username
                }
                comments {
                uid
                content
                sentiment_score
                }
                community: communities {
                uid
                name
                health_score
                }
                lifecycle {
                uid
                lifecycle_stage
                engagement_rate
                }
            }
            
            # Activity data with user and community context
            activities(func: type(Activity)) @filter(ge(timestamp, $start_date) AND le(timestamp, $end_date)) {
                uid
                type
                timestamp
                duration
                user {
                uid
                username
                }
                community {
                uid
                name
                }
            }
            
            # Pattern data for trend analysis
            patterns(func: type(Pattern)) @filter(ge(last_seen, $start_date)) {
                uid
                type
                frequency
                last_seen
                user {
                uid
                username
                }
                community {
                uid
                name
                }
            }
        }
        """
        variables = {
            "$start_date": start_date,
            "$end_date": end_date
        }

        return self._run_query(query, variables)

    def calculate_user_influence(self, username: str):
        """Calculate comprehensive user influence score"""
        query = """
        query UserInfluence($username: string) {
        # Basic user info and direct relationships
        user(func: eq(username, $username)) {
            username
            email
            bio
            joinDate
            followerCount
            following_count
            isAdmin
            isActive
            
            # Users they follow
            follows {
                username
                followerCount
            }
            
            # Influence scores
            ~user @filter(eq(dgraph.type, "InfluenceScore")) {
                score_value
                computed_at
                factors
            }
            
            # Posts 
            ~author @filter(eq(dgraph.type, "Post")) {
                uid
                content
                created_at
                likes_count
                shares_count
                posted_in {
                    name
                    description
                    health_score
                }
                hashtags
            }
            
            # Community memberships
            member_of {
                name
                description
                created_at
                health_score
                patterns {
                    type
                    frequency
                }
            }
        }

        # Comments in separate block
        userComments(func: eq(username, $username)) {
            ~author @filter(eq(dgraph.type, "Comment")) {
                content
                created_at
                likes_count
                sentiment_score
                on_post {
                    content
                    author {
                        username
                    }
                }
            }
        }
            
        # Activities in separate block
        userActivities(func: eq(username, $username)) {
            ~user @filter(eq(dgraph.type, "Activity")) {
                type
                timestamp
                duration
                community {
                    name
                }
            }
        }
            
        # Analytics in separate block
        userAnalytics(func: eq(username, $username)) {
            ~user @filter(eq(dgraph.type, "Analytics")) {
                metric_type
                value
                timestamp
            }
        }
            
        # Patterns in separate block - corrected relationship direction
        userPatterns(func: eq(username, $username)) {
            observed_in_user @filter(eq(dgraph.type, "Pattern")) {
                type
                frequency
                last_seen
                community {
                    name
                }
            }
        }
            
        # Trends in separate block
        userTrends(func: eq(username, $username)) {
            follows_trend {
                name
                score
                start_date
                followers
            }
        }
    }
        """
        variables = {'$username': username}
        return self._run_query(query, variables)

    def analyze_content_lifecycle_patterns(self):
        """
        Analyze content lifecycle patterns across different types of content, communities, and user groups.

        Args:
            days_back: Number of days of data to analyze
            min_engagement: Minimum engagement rate to filter content

        Returns:
            Comprehensive analysis of content lifecycles, patterns, and trends
        """
        query = """
            query ContentLifecycleAnalysis {
                # Potential Viral Content (High engagement + high share ratio)
                viral_candidates(func: type(Content)) 
                @filter(ge(engagement_rate, 0.85) AND has(related_posts)) {
                    content_type
                    created_at
                    engagement_rate
                    related_posts @filter(ge(shares_count, 40)) {
                        content
                        likes_count
                        shares_count
                        created_at
                        communities {
                            name
                            health_score
                        }
                    }
                }
                
                # High-Growth Content (Technical + Educational)
                tech_content(func: type(Content)) {
                    related_posts @filter(regexp(content, /#programming|#tech/i) AND ge(likes_count, 100)) {
                        content
                        likes_count
                        shares_count
                        created_at
                        communities {
                            name
                            health_score
                        }
                    }
                }
                
                # Community Performance Correlation
                top_communities(func: type(Community)) 
                @filter(ge(health_score, 0.90)) {
                    name
                    health_score
                    patterns @filter(ge(frequency, 0.85)) {
                        type
                        frequency
                        last_seen
                    }
                }
                
                # Rising Content Analysis
                rising_content(func: type(Content)) 
                @filter(eq(lifecycle_stage, "rising") AND ge(likes_count, 150)) {
                    content_type
                    engagement_rate
                    created_at
                    related_posts {
                        content
                        likes_count
                        shares_count
                    }
                }
                
                # Trending Content Analysis
                trending_content(func: type(Content)) 
                @filter(eq(lifecycle_stage, "trending") AND ge(engagement_rate, 0.90)) {
                    content_type
                    engagement_rate
                    created_at
                    related_posts {
                        content
                        likes_count
                        shares_count
                    }
                }
                
                # Trend Performance Analysis
                top_trends(func: type(Trend)) 
                @filter(ge(score, 89)) {
                    name
                    score
                    start_date
                    ~hashtags @filter(type(Post)) {
                        content
                        likes_count
                        shares_count
                        created_at
                    }
                }
                
                # Content Engagement Decay Analysis
                engagement_decay(func: type(Content)) 
                @filter(has(lifecycle_stage) AND le(engagement_rate, 0.80)) {
                    lifecycle_stage
                    engagement_rate
                    created_at
                    related_posts @filter(has(likes_count)) {
                        content
                        likes_count
                        shares_count
                        created_at
                    }
                }
        }
        """

        return self._run_query(query)

    def available_usrs(self) -> Dict:
        """Get all available users in the database."""
        users = {}
        query = """{
            
                user(func: has(username)) {
                    username
                }
    
        }"""
        try:
            res = self.client.txn(read_only=True).query(query)
            result = json.loads(res.json)
            # save all usernames in a dictionary
            for user in result['user']:
                users[user['username']] = user['username']
            return users
        except Exception as e:
            print(f"Error querying users: {str(e)}")
            return None

    def available_communities(self) -> Dict:
        """Get all available communities in the database."""
        communities = {}
        query = """
        {
            communities(func: type(Community)) {
                uid
                name
            }
        }
        """

        try:
            res = self.client.txn(read_only=True).query(query)
            result = json.loads(res.json)

            # Create dictionary mapping community UIDs to names
            communities = {
                community['uid']: community['name']
                for community in result.get('communities', [])
            }
            return communities

        except Exception as e:
            print(f"Error querying communities: {str(e)}")
            return None

    def available_posts(self) -> Dict:
        """Get all available posts in the database."""
        posts = {}
        query = """{
            
                post(func: type(Post)) {
                    uid
                    content
                }
    
        }"""
        try:
            res = self.client.txn(read_only=True).query(query)
            result = json.loads(res.json)
            # save all posts in a dictionary
            for post in result['post']:
                posts[post['uid']] = post['content']
            return posts

        except Exception as e:
            print(f"Error querying posts: {str(e)}")
            return None

    def print_dict(self, d: Dict):
        for key in d.keys():
            print(key, '--', d[key])

    def _run_query(self, query, variables=None):
        """Helper method to run queries"""
        txn = self.client.txn(read_only=True)
        try:
            if variables:
                response = txn.query(query, variables=variables)
            else:
                response = txn.query(query)

            res = json.loads(response.json)
            print(json.dumps(res, indent=4))
        finally:
            txn.discard()
