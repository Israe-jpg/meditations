from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
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
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user


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

#User table configuration
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))

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
    blog_content = CKEditorField('Blog Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

#creating a login form using bootsrap flask
class LoginForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email address'})
    password = StringField('', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Login')

#creating a register form using bootsrap flask
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()], render_kw={'placeholder': 'Name'})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'placeholder': 'Email address'})
    password = StringField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters long')], render_kw={'placeholder': 'Password'})
    submit = SubmitField('Register')

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

#initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
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
                         page_background_type="image",  
                         page_background_image=url_for('static', filename='background.jpg'),
                         year=get_current_year())

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
                         page_background_type="black",  
                         page_background_image=None,  
                         year=get_current_year(),
                         blog=blog)

#Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and user.password == login_form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', 
                         show_header=False,
                         year=get_current_year(),
                         form=login_form)

@app.route('/register', methods=['GET', 'POST'])
def register(): 
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        new_user = User(
            name=register_form.name.data,
            email=register_form.email.data,
            password=register_form.password.data
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', 
                         show_header=False,
                         year=get_current_year(),
                         form=register_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

#Blog routes
@app.route('/blog_modal', methods=['GET', 'POST'])
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
def add_post():
    # Initialize form
    form = BlogPostForm()
    
    # Handle form submission    
    if form.validate_on_submit():
        new_blog_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.blog_content.data,
            author=form.author.data,
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
def edit_post(id):
    blog_post = BlogPost.query.get_or_404(id)
    form = BlogPostForm()
    
    if form.validate_on_submit():
        # Handle form submission for editing
        blog_post.title = form.title.data
        blog_post.subtitle = form.subtitle.data
        blog_post.body = form.blog_content.data
        blog_post.author = form.author.data
        blog_post.date = get_current_date()  # Update date
        db.session.commit()
        return redirect(url_for('home'))
    
    # Pre-populate form with existing data ONLY for GET requests
    if request.method == 'GET':
        form.title.data = blog_post.title
        form.subtitle.data = blog_post.subtitle
        form.author.data = blog_post.author
        form.blog_content.data = blog_post.body
    
    return render_template('blog_modal.html',
                         show_header=False,
                         year=get_current_year(),
                         form=form,
                         edit_mode=True,
                         post_id=id)



@app.route('/delete_post/<int:id>', methods=['DELETE'])
def delete_post(id):
    blog_post = BlogPost.query.get(id)
    db.session.delete(blog_post)
    db.session.commit()
    return redirect(url_for('home'))

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

if __name__ == "__main__":
    app.run(debug=True)

