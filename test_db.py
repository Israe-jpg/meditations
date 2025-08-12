from server import app, db, BlogPost, get_blog_posts

with app.app_context():
    # Create tables
    db.create_all()
    
    # Test getting posts
    print("Testing get_blog_posts()...")
    posts = get_blog_posts()
    
    print(f"Total posts: {len(posts)}")
    for post in posts:
        print(f"ID: {post['id']}, Title: {post['title']}, Source: {post.get('source', 'unknown')}")
    
    print("\nDatabase posts:")
    db_posts = db.session.execute(db.select(BlogPost)).scalars().all()
    for post in db_posts:
        print(f"DB ID: {post.id}, Title: {post.title}") 