from flask import Flask, render_template, request, redirect, url_for
import datetime
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean


app = Flask(__name__)

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
    body = TextAreaField('Body', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
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
        response = requests.get("https://api.npoint.io/db4eaa79651d1ec3953e")
        response.raise_for_status()
        api_posts = response.json()
        #add source prefix to api posts
        for post in api_posts:
            post['id'] = f"api_{post['id']}"
        #add dource prefix to db posts
        db_posts = db.session.execute(db.select(BlogPost)).scalars().all()
        for post in db_posts:
            post_dict = post.to_dict()
            post_dict['id'] = f"db_{post_dict['id']}"
            #merge the two
            api_posts.append(post_dict)
        return api_posts
        
    except (requests.RequestException, requests.HTTPError, ValueError, FileNotFoundError):
        #network errors, HTTP status errors, JSON parsing errors,and file errors
        api_posts = []
    return api_posts

@app.route('/')
def home():
    return render_template('index.html',
                         posts=get_blog_posts(), 
                         page_title="Unwind your soul",
                         page_subtitle="A Meditation content related platform",
                         year=get_current_year())

@app.route('/about')
def about():
    return render_template('about.html', 
                         page_title="About Meditations",
                         page_subtitle="This is what we do.",
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
                         year=get_current_year(),
                         form = contact_form)

@app.route('/post/<string:id>')
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
                         page_meta="Posted by Meditations",
                         page_body=blog['body'],
                         year=get_current_year())

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
    if blog_post_form.validate_on_submit():
        new_blog_post = BlogPost(
            title=blog_post_form.title.data,
            subtitle=blog_post_form.subtitle.data,
            body=blog_post_form.body.data,
            author=blog_post_form.author.data,
            date=get_current_date()
        )
        db.session.add(new_blog_post)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('blog_modal.html',
                         show_header=False,
                         year=get_current_year(),
                         form=blog_post_form)

