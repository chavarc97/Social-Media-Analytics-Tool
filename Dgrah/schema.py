user_schema = """
    type User {
        username
        email
        bio
        joinDate
        isAdmin
        influenceScore
        location
        follows: [uid]
        posts: [uid]
        comments: [uid]
        communities: [uid]
    }
    
    username: string @index(exact) .
    email: string @index(exact) .
    bio: string .
    joinDate: dateTime .
    isAdmin: bool .
    influenceScore: float @index(float) .
    location: geo @index(geo) .
    follows: [uid] @reverse .
    posts: [uid] @reverse .
    comments: [uid] @reverse .
    communities: [uid] @reverse .
"""

post_schema = """
    type Post {
        title
        body
        datePublished
        author
        comments: [uid]
        tags
    }
    
    
    
"""