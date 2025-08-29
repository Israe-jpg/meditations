from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, make_response, flash, abort, jsonify
from datetime import date
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Optional
from werkzeug.utils import secure_filename
import os
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, ForeignKey
from flask_ckeditor import CKEditor, CKEditorField
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import pdfkit
from io import BytesIO
import werkzeug.security
from functools import wraps


app = Flask(__name__)

#initialize CKEditor  
ckeditor = CKEditor(app)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


bootstrap = Bootstrap4(app)
app.config['SECRET_KEY'] = 'MYSECRETKEY1234'



#Blog table configuration
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)  # Nullable for migration
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Relationships
    author: Mapped['User'] = relationship(back_populates='posts')
    comments: Mapped[list['Comment']] = relationship(back_populates='post', cascade='all, delete-orphan')
    
    def to_dict(self):
        result = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        # Add author name from relationship if available
        if hasattr(self, 'author') and self.author:
            result['author'] = self.author.name
        elif 'author' in result and isinstance(result['author'], str):
            # Keep existing string author for backward compatibility
            pass
        else:
            result['author'] = 'Unknown'
        return result
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'
    
with app.app_context():
    db.create_all()

#User table configuration
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    role: Mapped[str] = mapped_column(String(20), default='regular', nullable=False)
    date_joined: Mapped[str] = mapped_column(String(100), default=None, nullable=True)
    profile_picture: Mapped[str] = mapped_column(String(100), default='default_profile.jpg', nullable=True)
    posts: Mapped[list['BlogPost']] = relationship(back_populates='author')
    comments: Mapped[list['Comment']] = relationship(back_populates='author')

#Comment table configuration
class Comment(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("blog_post.id"), nullable=False)
    
    # Relationships
    author: Mapped['User'] = relationship(back_populates='comments')
    post: Mapped['BlogPost'] = relationship(back_populates='comments')
    
    def __repr__(self):
        return f'<Comment {self.id}>'



with app.app_context():
    db.create_all()
    

#Creating a flask contact form
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])

#Create a blog post form
class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    subtitle = StringField('Subtitle', validators=[DataRequired()])
    blog_content = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

#creating a login form using bootsrap flask
class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email address'})
    password = PasswordField('', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')

#creating a register form using bootsrap flask
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={'placeholder': 'Name'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email address'})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Register')

#Create a comment form
class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()], render_kw={'placeholder': 'Write your comment here...', 'rows': 3})
    submit = SubmitField('Post Comment')

#Create a profile picture upload form
class ProfilePictureForm(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[Optional()])
    submit = SubmitField('Update Picture')

#send data to email
def send_contact_email(name, email, phone, message):

    # Email configuration
    sender_email = "israepersonaluseonly@gmail.com"  
    sender_password = "password"   
    receiver_email = "israeguennouni99@gmail.com" 
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"New Contact Form Submission from {name}"
    
    # Eroles()mail body
    body = f"""
    New contact form submission received!
    
    Name: {name}
    Email: {email}
    Phone: {phone}
    Message: {message}
    
    This email was sent from your website contact form.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

#initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

#user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#get current year
def get_current_year():
    return date.today().year

#get current date
def get_current_date():
    return date.today().strftime("%B %d, %Y")

# Make current year available in all templates
@app.context_processor
def inject_current_year():
    return {'get_current_year': get_current_year}



#fetch blog posts from created api
def get_blog_posts():
    try:    
        blog_posts = db.session.execute(db.select(BlogPost).order_by(BlogPost.date.desc()).limit(3)).scalars().all()
        return [post.to_dict() for post in blog_posts]
        
    except (requests.RequestException, requests.HTTPError, ValueError, FileNotFoundError):
        #network errors, HTTP status errors, JSON parsing errors,and file errors
        return []


#make a python decorator to check if user is admin
def is_admin(user=None):
    if user is None:
        user = current_user
    return user.is_authenticated and user.role == 'admin'

#Helper function for file upload
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_profile_picture(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create unique filename with user id
        file_extension = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"profile_{current_user.id}_{get_current_date().replace(' ', '_').replace(',', '')}_{filename}"
        
        # Save to static folder
        upload_path = os.path.join(app.root_path, 'static', unique_filename)
        file.save(upload_path)
        
        return unique_filename
    return None

#make a python decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if user is logged in
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # Then check if user is admin
        if not is_admin():
            abort(403)  
        return f(*args, **kwargs)
    return decorated_function



@app.route('/')
def home():
    # Check if this is a first-time user and clear the flag
    is_first_time = session.pop('first_time_user', False)

    #initial posts
    initial_posts = get_blog_posts()
    
    return render_template('index.html',
                         posts=initial_posts, 
                         page_title="Unwind your soul",
                         page_subtitle="A Meditation content related platform",
                         page_background_type="image",  
                         page_background_image=url_for('static', filename='background.jpg'),
                         year=get_current_year(),
                         is_first_time_user=is_first_time)

#load more posts
@app.route('/load_posts')
def load_posts():
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 3, type=int)
    
    try:
        blog_posts = db.session.execute(
            db.select(BlogPost)
            .order_by(BlogPost.date.desc())
            .offset(offset)
            .limit(limit)
        ).scalars().all()
        
        posts_data = []
        for post in blog_posts:
            post_dict = post.to_dict()
            posts_data.append(post_dict)
        
        # Check if there are more posts available
        total_posts = db.session.scalar(db.select(db.func.count(BlogPost.id)))
        has_more = offset + limit < total_posts
        
        return jsonify({
            'posts': posts_data,
            'has_more': has_more,
            'total_posts': total_posts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/about')
def about():
    return render_template('about.html', 
                         page_title="About Meditations",
                         page_subtitle="This is what we do.",
                         page_background_type="image", 
                         page_background_image=url_for('static', filename='about_img.jpg'), 
                         year=get_current_year())


@app.route("/contact", methods=["GET", "POST"])
def contact():
    contact_form = ContactForm()
    submitted = False
    email_sent = False
    
    if contact_form.validate_on_submit():
        submitted = True
        email_sent = send_contact_email(
            contact_form.name.data,
            contact_form.email.data,
            contact_form.phone.data,
            contact_form.message.data
        )
    
    return render_template('contact.html',
                         submitted=submitted,
                         email_sent = email_sent,
                         page_title="Contact Me",
                         page_subtitle="Have questions? I have answers.",
                         page_background_type="black",  # Options: "image", "black", "custom"
                         page_background_image=None,  # Set to image URL if type is "image" or "custom"
                         year=get_current_year(),
                         form = contact_form)


#Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user:
            # User exists, check password
            if werkzeug.security.check_password_hash(user.password, login_form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                # Wrong password
                flash('Password incorrect, please try again.', 'error')
                return redirect(url_for('login'))
        else:
            # Email doesn't exist in database
            flash('That email does not exist, please try again.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html', 
                         show_header=False,
                         year=get_current_year(),
                         form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register(): 
    register_form = RegisterForm()
    
    if register_form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=register_form.email.data).first()
        if existing_user:
            flash('You\'ve already signed up with that email, log in instead!', 'error')
            return redirect(url_for('login'))
        
        hashed_password = werkzeug.security.generate_password_hash(register_form.password.data, method='scrypt', salt_length=16)
        new_user = User(
            name=register_form.name.data,
            email=register_form.email.data,
            password=hashed_password,
            role='regular',  # Default role for new users
            date_joined=get_current_date(),  # Set registration date
            profile_picture='default_profile.jpg'  # Set default profile picture
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        # Set session flag to indicate this is a new registration
        session['first_time_user'] = True
        return redirect(url_for('home'))
    
    # If form validation fails, show errors
    if request.method == 'POST':
        flash('Please check the form for errors and try again.', 'error')
    
    return render_template('register.html', 
                         show_header=False,
                         year=get_current_year(),
                         form=register_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/download')
@login_required
def download():
    # Handle existing users who might not have date_joined
    registration_date = current_user.date_joined if current_user.date_joined else "Not Available"
    
    data = {
        'user_name': current_user.name,
        'user_email': current_user.email,
        'user_role': current_user.role.title(),
        'registration_date': registration_date,
        'current_date': get_current_date()
    }
    rendered_html = render_template('pdf_template.html', data=data)
    
    # Configure wkhtmltopdf path for Windows
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe')
    
    #convert html to pdf
    pdf_bytes = pdfkit.from_string(rendered_html, False, configuration=config)
    #create a response using the pdf bytes
    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename={current_user.name}_id_card.pdf'
        
    return response



#Blog routes
@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    # Get the blog post from database
    blog_post = BlogPost.query.get_or_404(id)
    
    # Create comment form
    comment_form = CommentForm()
    
    # Handle comment submission
    if comment_form.validate_on_submit() and current_user.is_authenticated:
        new_comment = Comment(
            content=comment_form.content.data,
            author_id=current_user.id,
            post_id=id,
            date=get_current_date()
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post', id=id))
    
    # Get all comments for this post
    comments = Comment.query.filter_by(post_id=id).order_by(Comment.id.desc()).all()
    
    return render_template('post.html', 
                         page_title=blog_post.title,
                         page_subtitle=blog_post.subtitle,
                         page_meta=f"Posted by {blog_post.author.name if blog_post.author else 'Unknown'}",
                         page_body=blog_post.body,
                         page_background_type="black",  
                         page_background_image=None,  
                         year=get_current_year(),
                         blog=blog_post,
                         comments=comments,
                         comment_form=comment_form)

#delete comments
@app.route('/delete_comment/<int:id>', methods=['POST'])
@admin_required
def delete_comment(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('post', id=comment.post_id))


@app.route('/blog_modal', methods=['GET', 'POST'])
@admin_required
def blog_modal():
    
    # Check if this is an edit request using query parameters
    edit_param = request.args.get('edit')
    id_param = request.args.get('id')
    
    if edit_param and id_param:
        # Redirect to the proper edit route
        return redirect(url_for('edit_post', id=int(id_param)))
    
    # Otherwise, handle as add new post
    return redirect(url_for('add_post'))

@app.route('/add_post', methods=['GET', 'POST'])
@admin_required
def add_post():
    # Initialize form
    form = BlogPostForm()
    
    # Handle form submission    
    if form.validate_on_submit():
        new_blog_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.blog_content.data,
            author_id=current_user.id,
            date=get_current_date()
            )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('home'))
    
    return render_template('blog_modal.html',
                         show_header=False,
                         year=get_current_year(),
                         form=form,
                         edit_mode=False)

@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_post(id):
    blog_post = BlogPost.query.get_or_404(id)
    form = BlogPostForm()
    
    if form.validate_on_submit():
        # Handle form submission for editing
        blog_post.title = form.title.data
        blog_post.subtitle = form.subtitle.data
        blog_post.body = form.blog_content.data
        blog_post.author_id = current_user.id
        blog_post.date = get_current_date()  # Update date
        db.session.commit()
        return redirect(url_for('home'))
    
    # Pre-populate form with existing data ONLY for GET requests
    if request.method == 'GET':
        form.title.data = blog_post.title
        form.subtitle.data = blog_post.subtitle
        form.blog_content.data = blog_post.body
    
    return render_template('blog_modal.html',
                         show_header=False,
                         year=get_current_year(),
                         form=form,
                         edit_mode=True,
                         post_id=id)



@app.route('/delete_post/<int:id>', methods=['POST'])
@admin_required
def delete_post(id):
    blog_post = BlogPost.query.get(id)
    if blog_post:
        db.session.delete(blog_post)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        flash('Post not found!', 'error')
        return redirect(url_for('home'))
    
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    upload_form = ProfilePictureForm()
    
    if upload_form.validate_on_submit():
        if upload_form.profile_picture.data:
            # Save the uploaded file
            filename = save_profile_picture(upload_form.profile_picture.data)
            if filename:
                # Update user's profile picture in database
                current_user.profile_picture = filename
                db.session.commit()
                flash('Profile picture updated successfully!', 'success')
            else:
                flash('Invalid file type. Please upload PNG, JPG, JPEG, or GIF files.', 'error')
        else:
            flash('Please select a file to upload.', 'error')
        
        return redirect(url_for('profile'))
    
    return render_template('profile.html',
                         page_title="Your Profile",
                         page_subtitle="Manage your account and settings",
                         page_background_type="image",
                         page_background_image=url_for('static', filename='profile_bg.jpg'),
                         year=get_current_year(),
                         upload_form=upload_form)


# AJAX route for search suggestions dropdown
@app.route('/search_suggestions', methods=['GET'])
def search_suggestions():
    search_query = request.args.get('query', '').strip()
    suggestions = []
    
    if search_query and len(search_query) >= 2:
        posts = BlogPost.query.filter(
            db.or_(
                BlogPost.title.ilike(f'%{search_query}%'),
                BlogPost.subtitle.ilike(f'%{search_query}%')
            )
        ).limit(5).all()
        
        for post in posts:
            post_url = url_for('post', id=post.id)
            suggestions.append({
                'id': post.id,
                'title': post.title,
                'subtitle': post.subtitle,
                'url': post_url
            })
    
    return jsonify(suggestions)



if __name__ == "__main__":
    app.run(debug=True)

