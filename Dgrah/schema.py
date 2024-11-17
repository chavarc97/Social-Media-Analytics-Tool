user_schema = """
    type User {
        user_id
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
    
    user_id: string @id .
    username: string @index(exact) .
    email: string @index(exact) .
    bio: string .
    joinDate: dateTime .
    isAdmin: bool .
    followerCount: int .
    influenceScore: [Influence] @reverse .
    isActive: bool .
    tracked_by: [Analytics] @reverse .
    follows: [User] @reverse .
    trends: [Trend] @reverse .
    followers: [User] @reverse .
    posts: [Post] @reverse .
    comments: [Comment] @reverse .
    communities: [Community] @reverse .
    follower_count: int @index(int) .
    following_count: int @index(int) .
    
"""

post_schema = """
    type Post {
        post_id
        content 
        created_at 
        likes_count 
        shares_count
        hashtags
        author
        comments
        community
        is_archived
        lifecycle 
    }
    
    post_id: string @id .
    content: string @index(term, fulltext) .
    created_at: dateTime .
    likes_count: int @index(int) .
    shares_count: int @index(int) .
    hashtags: [Hashtag] @reverse .
    comments: [Comment] @reverse .
    author: User @reverse .
    # links to community but not required
    community: [Community] @reverse(field: posts) .
    is_archived: bool .
    lifecycle: [Content] @reverse .
"""

comment_schema = """
    type Comment {
        comment_id
        content
        created_at
        likes_count
        liked_by
        author
        post
        lifecycle
        sentiment_score
    }
    
    comment_id: string @id .
    content: string @index(term, fulltext) .
    created_at: dateTime .
    likes_count: int @index(int) .
    liked_by: [User] @reverse .
    author: User @reverse .
    post: Post @reverse .
    lifecycle: [Content] @reverse .
    sentiment_score: float
"""

community_schema = """
    type Community {
        community_id
        name
        description
        created_at
        members
        posts
        admins
        patterns
        health_score
    }
    
    community_id: string @id .
    name: string @index(exact) .
    description: string .
    created_at: dateTime .
    members: [User] @reverse(field: communities) .
    posts: [Post] @reverse .
    admins: [User] @reverse .
    patterns: [Activity] 
    health_score: float
"""

content_schema = """
    type Content {
        content_id
        type
        created_at
        engagement_rate
        lifecycle_stage
        related_posts
        related_comments
        related_users
        related_communities    
    }
    
    content_id: string @id .
    type: string @index(exact) .
    created_at: dateTime .
    engagement_rate: float .
    lifecycle_stage: string .
    related_posts: [Post] @reverse .
    related_comments: [Comment] @reverse .
    related_users: [User] @reverse .
    related_communities: [Community] @reverse .
"""

influence_schema = """
    type Influence {
        score_id
        user
        score_value
        computed_at
        factors
    }
    
    score_id: string @id .
    user: User @reverse .
    score_value: float .
    computed_at: dateTime .
    factors: [string] .
"""

activity_schema = """
    type Activity {
        activity_id
        type
        timestamp
        user
        duration
        community
    }
    
    activity_id: string @id .
    type: string @index(exact) .
    timestamp: dateTime .
    user: User @reverse(field: generates) .
    duration: float .
    community: Community @reverse .
"""

analytics_schema = """
    type Analytics {
        analytics_id
        user
        metric_type
        value
        timestamp
    }
    
    analytics_id: string @id .
    user: User @reverse(field: tracked_by) .
    metric_type: string @index(exact) .
    value: float .
    timestamp: dateTime .
"""

trend_schema = """
    type Trend {
        trend_id
        name
        followers
        score
        start_date
    }
    
    trend_id: string @id .
    name: string @index(exact) .
    followers: [User] @reverse(field: trends) .
    score: float .
    start_date: dateTime .
"""

patter_schema = """
    type Pattern {
        pattern_id
        user
        community
        type
        frequency
        last_seen
    }
    
    pattern_id: string @id .
    user: User @reverse .
    community: Community @reverse .
    type: string @index(exact) .
    frequency: float .
    last_seen: dateTime .
"""