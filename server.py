from flask import Flask, render_template, request, redirect, url_for
import datetime
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_ckeditor import CKEditor, CKEditorField


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
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    date: Mapped[str] = mapped_column(String(100), nullable=False)
    
    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'
    
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
    author = StringField('Author', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[DataRequired()])
    blog_content = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

#creating a login form using bootsrap flask
class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email address'})
    password = StringField('', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')


#send data to email
def send_contact_email(name, email, phone, message):

    # Email configuration
    sender_email = "israepersonaluseonly@gmail.com"  
    sender_password = "ltlmawxcqblwfhgapassword"   
    receiver_email = "israeguennouni99@gmail.com" 
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"New Contact Form Submission from {name}"
    
    # Email body
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



#get current year
def get_current_year():
    return datetime.datetime.now().year

#get current date
def get_current_date():
    return datetime.datetime.now().strftime("%Y-%m-%d")



#fetch blog posts from created api
def get_blog_posts():
    try:
        blog_posts = db.session.execute(db.select(BlogPost)).scalars().all()
        return [post.to_dict() for post in blog_posts]
        
    except (requests.RequestException, requests.HTTPError, ValueError, FileNotFoundError):
        #network errors, HTTP status errors, JSON parsing errors,and file errors
        return []




@app.route('/')
def home():
    return render_template('index.html',
                         posts=get_blog_posts(), 
                         page_title="Unwind your soul",
                         page_subtitle="A Meditation content related platform",
                         page_background_type="image",  # Keep the original background for index
                         page_background_image=url_for('static', filename='background.jpg'),
                         year=get_current_year())

@app.route('/about')
def about():
    return render_template('about.html', 
                         page_title="About Meditations",
                         page_subtitle="This is what we do.",
                         page_background_type="image",  # Changed from "black" to "image"
                         page_background_image=url_for('static', filename='about_img.jpg'),  # Your about image
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

@app.route('/post/<int:id>')
def post(id):
    #get blogs first
    blog_posts = get_blog_posts()
    #find the specific post by id
    blog = None
    for post in blog_posts:
         if post['id'] == id:
             blog = post
             break
    if blog is None:
        return "Post not found", 404
    
    return render_template('post.html', 
                         page_title=blog['title'],
                         page_subtitle=blog['subtitle'],
                         page_meta=f"Posted by {blog['author']}",
                         page_body=blog['body'],
                         page_background_type="black",  # Options: "image", "black", "custom"
                         page_background_image=None,  # Set to image URL if type is "image" or "custom"
                         year=get_current_year(),
                         blog=blog)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        pass
    return render_template('login.html', 
                         show_header=False,
                         year=get_current_year(),
                         form=login_form)

@app.route('/blog_modal', methods=['GET', 'POST', 'PUT', 'DELETE'])
def blog_modal():
    blog_post_form = BlogPostForm()
    
    # Handle form submission
    if request.method == 'POST':
        if blog_post_form.validate_on_submit():
            new_blog_post = BlogPost(
                title=blog_post_form.title.data,
                subtitle=blog_post_form.subtitle.data,
                body=blog_post_form.blog_content.data,
                author=blog_post_form.author.data,
                date=get_current_date()
            )
            db.session.add(new_blog_post)
            db.session.commit()
            return redirect(url_for('home'))
        # If validation fails, the form will automatically retain the submitted data
    
    # For GET requests, check if we have saved form data in session
    elif request.method == 'GET':
        # Pre-populate form with session data if available
        if 'blog_form_data' in request.args:
            blog_post_form.title.data = request.args.get('title', '')
            blog_post_form.subtitle.data = request.args.get('subtitle', '')
            blog_post_form.author.data = request.args.get('author', '')
            blog_post_form.image_url.data = request.args.get('image_url', '')
            blog_post_form.blog_content.data = request.args.get('blog_content', '')
    
    return render_template('blog_modal.html',
                         show_header=False,
                         year=get_current_year(),
                         form=blog_post_form)

# def run_initial_migration():
    
#     with app.app_context():
#         # Count posts
#         all_posts = db.session.execute(db.select(BlogPost)).scalars().all()
#         post_count = len(all_posts)
        
#         # Clear existing posts if any
#         if post_count > 0:
#             db.session.execute(db.delete(BlogPost))
#             db.session.commit()
#         #run migration and populate from api
#         try:
#             response = requests.get("https://api.npoint.io/db4eaa79651d1ec3953e")
#             response.raise_for_status()
#             api_posts = response.json()
            
            
#             for i, post_data in enumerate(api_posts):
#                 new_post = BlogPost(
#                     title=post_data['title'],
#                     subtitle=post_data['subtitle'], 
#                     body=post_data['body'],
#                     author=post_data.get('author', 'Unknown'),
#                     date=post_data.get('date', get_current_date())
#                 )
#                 db.session.add(new_post)
            
#             db.session.commit()
            
#         except Exception as e:
#             db.session.rollback()


# run_initial_migration()
# app.run(debug=True)

