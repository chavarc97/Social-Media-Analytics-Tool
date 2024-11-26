user_schema = """
    username: string @index(exact) .
    email: string @index(exact) .
    bio: string .
    joinDate: dateTime .
    isAdmin: bool .
    followerCount: int .
    influenceScore: [uid] @reverse .
    isActive: bool .
    tracked_by: [uid] @reverse .
    follows: [uid] @reverse .
    trends: [uid] @reverse .
    followers: [uid] @reverse .
    posts: [uid] @reverse .
    comments: [uid] @reverse .
    communities: [uid] @reverse .
    follower_count: int @index(int) .
    following_count: int @index(int) .
    
    type User {
        username
        email
        bio
        joinDate
        isAdmin
        followerCount
        influenceScore
        isActive
        tracked_by
        follows
        followers
        trends
        posts
        comments
        communities
        follower_count
        following_count
    }
"""

post_schema = """
    type Post {
        content 
        created_at 
        likes_count 
        shares_count
        hashtags
        author
        comments
        communities
        is_archived
        lifecycle 
    }
    
    content: string @index(term, fulltext) .
    created_at: dateTime .
    likes_count: int @index(int) .
    shares_count: int @index(int) .
    hashtags: [uid] @reverse .
    comments: [uid] @reverse .
    author: uid @reverse .
    # links to community but not required
    communities: [uid] @reverse .
    is_archived: bool .
    lifecycle: [uid] @reverse .
"""

comment_schema = """
    type Comment {
        content
        created_at
        likes_count
        liked_by
        author
        post
        lifecycle
        sentiment_score
    }
    
    content: string @index(term, fulltext) .
    created_at: dateTime .
    likes_count: int @index(int) .
    liked_by: [uid] @reverse .
    author: uid @reverse .
    post: uid @reverse .
    lifecycle: [uid] @reverse .
    sentiment_score: float .
"""

community_schema = """
    type Community {
        name
        description
        created_at
        members
        posts
        admins
        patterns
        health_score
    }
    
    name: string @index(exact) .
    description: string .
    created_at: dateTime .
    members: [uid] @reverse .
    posts: [uid] @reverse .
    admins: [uid] @reverse .
    patterns: [uid] .
    health_score: float .
"""

content_schema = """
    type Content {
        content_type
        created_at
        engagement_rate
        lifecycle_stage
        related_posts
        related_comments
        related_users
        related_communities    
    }
    
    content_type: string @index(exact) .
    created_at: dateTime .
    engagement_rate: float .
    lifecycle_stage: string .
    related_posts: [uid] @reverse .
    related_comments: [uid] @reverse .
    related_users: [uid] @reverse .
    related_communities: [uid] @reverse .
"""

influence_schema = """
    type Influence {
        user
        score_value
        computed_at
        factors
    }
    
    user: uid @reverse .
    score_value: float .
    computed_at: dateTime .
    factors: [string] .
"""

activity_schema = """
    type Activity {
        type
        timestamp
        user
        duration
        community
    }
    
    type: string @index(exact) .
    timestamp: dateTime .
    user: uid @reverse .
    duration: float .
"""

analytics_schema = """
    type Analytics {
        user
        metric_type
        value
        timestamp
    }
    
    user: uid @reverse .
    metric_type: string @index(exact) .
    value: float .
    timestamp: dateTime .
"""

trend_schema = """
    type Trend {
        name
        followers
        score
        start_date
    }
    
    name: string @index(exact) .
    followers: [uid] @reverse .
    score: float .
    start_date: dateTime .
"""

pattern_schema = """
    type Pattern {
        user
        community
        type
        frequency
        last_seen
    }
    
    user: uid @reverse .
    type: string @index(exact) .
    frequency: float .
    last_seen: dateTime .
    community: uid @reverse .
"""

hashtags_schema = """
    type Hashtag {
        name
        posts
        comments
        usage_count
        trending_score
    }
    
    name: string @index(exact) .
    posts: [uid] @reverse .
    comments: [uid] @reverse .
    usage_count: int .
    trending_score: float .
    
"""

global_schema = user_schema + post_schema + comment_schema + community_schema + content_schema + \
    influence_schema + activity_schema + analytics_schema + \
    trend_schema + pattern_schema + hashtags_schema
