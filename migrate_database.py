import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_data():
    # SQLite connection (your local database)
    sqlite_conn = sqlite3.connect('instance/blog.db')  # Path to your local db file
    sqlite_cursor = sqlite_conn.cursor()
    
    # PostgreSQL connection (your Render database)
    postgres_url = os.environ.get('DATABASE_URL')  # Your Render PostgreSQL URL
    # Remove 'postgresql://' and parse the URL
    if postgres_url.startswith('postgresql://'):
        postgres_url = postgres_url.replace('postgresql://', '')
    
    # Parse connection details
    # Format: user:password@host:port/database
    user_pass, host_db = postgres_url.split('@')
    user, password = user_pass.split(':')
    host_port, database = host_db.split('/')
    host, port = host_port.split(':')
    
    postgres_conn = psycopg2.connect(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password
    )
    postgres_cursor = postgres_conn.cursor()
    
    try:
        # Migrate Users table (if it exists)
        print("Migrating users...")
        try:
            sqlite_cursor.execute("SELECT id, email, password, name, role, date_joined, profile_picture FROM user")
            users = sqlite_cursor.fetchall()
            
            for user in users:
                try:
                    postgres_cursor.execute("""
                        INSERT INTO "user" (id, email, password, name, role, date_joined, profile_picture) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s) 
                        ON CONFLICT (email) DO NOTHING
                    """, user)
                    postgres_conn.commit()
                except Exception as e:
                    print(f"Error inserting user {user[1]}: {e}")
                    postgres_conn.rollback()
                    continue
            print(f"Migrated {len(users)} users")
        except sqlite3.OperationalError as e:
            print(f"No user table found or error: {e}")
        
        # Migrate Blog Posts
        print("Migrating blog posts...")
        try:
            sqlite_cursor.execute("SELECT id, title, subtitle, body, author_id, date FROM blog_post")
            posts = sqlite_cursor.fetchall()
            
            for post in posts:
                try:
                    postgres_cursor.execute("""
                        INSERT INTO blog_post (id, title, subtitle, body, author_id, date) 
                        VALUES (%s, %s, %s, %s, %s, %s) 
                        ON CONFLICT (id) DO NOTHING
                    """, post)
                    postgres_conn.commit()
                except Exception as e:
                    print(f"Error inserting post {post[1]}: {e}")
                    postgres_conn.rollback()
                    continue
            print(f"Migrated {len(posts)} blog posts")
        except sqlite3.OperationalError as e:
            print(f"No blog_post table found or error: {e}")
        
        # Migrate Comments (if you have any)
        print("Migrating comments...")
        try:
            sqlite_cursor.execute("SELECT id, content, date, author_id, post_id FROM comment")
            comments = sqlite_cursor.fetchall()
            
            for comment in comments:
                try:
                    postgres_cursor.execute("""
                        INSERT INTO comment (id, content, date, author_id, post_id) 
                        VALUES (%s, %s, %s, %s, %s) 
                        ON CONFLICT (id) DO NOTHING
                    """, comment)
                    postgres_conn.commit()
                except Exception as e:
                    print(f"Error inserting comment {comment[0]}: {e}")
                    postgres_conn.rollback()
                    continue
            print(f"Migrated {len(comments)} comments")
        except sqlite3.OperationalError:
            print("No comments table found, skipping...")
        
        # Update sequences (important for PostgreSQL)
        try:
            postgres_cursor.execute("SELECT setval('user_id_seq', (SELECT MAX(id) FROM \"user\"));")
            postgres_cursor.execute("SELECT setval('blog_post_id_seq', (SELECT MAX(id) FROM blog_post));")
            postgres_cursor.execute("SELECT setval('comment_id_seq', (SELECT MAX(id) FROM comment));")
            postgres_conn.commit()
            print("Migration completed successfully!")
        except Exception as e:
            print(f"Error updating sequences: {e}")
            postgres_conn.rollback()
        
    except Exception as e:
        print(f"Migration failed: {e}")
        postgres_conn.rollback()
    
    finally:
        sqlite_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    migrate_data()