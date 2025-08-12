from server import app, db

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
    print("You can now use the blog post form.") 